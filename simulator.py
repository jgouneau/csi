import copy
from multiprocessing.sharedctypes import Value
import numpy as np
import obja

class Vertex:
    """Classe simplifiant la représentation/manipulation de la connectivité d'un sommet
    """
    def __init__(self, idx, vertex, edges):
        self.idx = idx
        self.coordinates = vertex
        self.neighbours = []
        for edge in edges:
            (a, b) = edge
            if idx == a:
                self.add_neighbor(b)
            elif idx == b:
                self.add_neighbor(a)
    
    def delete_neighbor(self, v_del_idx):
        del(self.neighbours[self.neighbours.index(v_del_idx)])
    
    def add_neighbor(self, v_add_idx):
        if v_add_idx not in self.neighbours and v_add_idx != self.idx:
            self.neighbours.append(v_add_idx)


class Simulator:
    """
    Classe permettant la simulation d'une compression d'un objet 3D suivant l'algorithme SQUEEZE 

    Args:
            vertices (list(np.array)): list of 3-elements np.arrays containing the x, y, z coordinates.
            faces (list(Face)): list of Faces objects containing the indexes a, b, c of the vertices in a face. 
    """
    def __init__(self, vertices, faces):
        problem = []
        for vertex in range(len(vertices)):
            n_faces = 0
            for face in faces:
                if vertex in [face.a, face.b, face.c]:
                    n_faces += 1
            if n_faces < 3:
                problem.append(vertex)
        # assert not problem

        self._faces = [face.clone() for face in faces]
        self._faces_exists = list(range(len(faces)))
        self._edges = []
        for face in faces:
            self._add_face_edges(face)
        self._vertices = [Vertex(idx, vertex, self._edges) for idx, vertex in enumerate(vertices)]
        self._vertices_exists = list(range(len(vertices)))
        self._batch = []
        self._i_batch = 0
    
    def _add_face_edges(self, face):
        for (a, b) in [(face.a, face.b), (face.b, face.c), (face.c, face.a)]:
            if (a, b) not in self._edges and (b, a) not in self._edges:
                self._edges.append((a, b))

    def delete_oriented_edge(self, v_del, v_del_idx, v_split, v_split_idx):
        # delete the two faces that contain v_del and v_split
        f_del = []
        for i in self._faces_exists:
            face = self._faces[i]
            if v_del_idx in [face.a, face.b, face.c] and v_split_idx in [face.a, face.b, face.c]:
                f_del.append(i)
        if len(f_del) != 2:
            print("Problem Houston")
            raise ValueError
        for i in f_del:
            del(self._faces_exists[self._faces_exists.index(i)])
        
        # modify the faces that contain v_del only
        f_modified = []
        for i in self._faces_exists:
            face = self._faces[i]
            if v_del_idx in [face.a, face.b, face.c]:
                f_modified.append(i)
                v_idx_in_face = [face.a, face.b, face.c].index(v_del_idx)
                setattr(face, ['a', 'b', 'c'][v_idx_in_face], v_split_idx)
                self._faces[i] = face
        
        # delete the edges linking v_del to its neighbours and link them to v_split
        neighbours = v_del.neighbours
        for i in neighbours:
            neighbor = self._vertices[i]
            neighbor.delete_neighbor(v_del_idx)
            neighbor.add_neighbor(v_split_idx)
            v_split.add_neighbor(i)
            self._vertices[i] = neighbor
        self._vertices[v_split_idx] = v_split
        self._vertices[v_del_idx] = v_del

        result = dict(
            i_del=v_del_idx,
            i_split=v_split_idx,
            v_del=v_del.coordinates,
            f_del=tuple(f_del),
            f_modified=f_modified,
        )
        return result
    
    def _is_valid_triangle(self, v1, v2, w):
        valid = False
        for i in self._faces_exists:
            face = self._faces[i]
            face_idx = [face.a, face.b, face.c]
            if v1 in face_idx and v2 in face_idx and w in face_idx:
                valid = True
                break
        return valid

    def generate_batch(self):
        self._batch = []
        self._i_batch = 0
        edges_to_delete = []
        edges_to_select = []

        # 2. For each edge e = (v1, v2) that will be collapsed and
        # any other vertex w that is incident to both v1 and v2,
        # the triple (v1, v2, w) must define a valid triangle in the
        # mesh Mi.
        for i, (i1, i2) in enumerate(self._edges):
            v1 = self._vertices[i1]
            v2 = self._vertices[i2]
            neighbours = []
            for neighbor in v1.neighbours:
                if neighbor in v2.neighbours:
                    neighbours.append(neighbor)
            valid = True
            for w in neighbours:
                valid *= self._is_valid_triangle(i1, i2, w)
            if valid and len(neighbours) > 1:
                edges_to_select.append(i)

        while edges_to_select:
            # select edge
            i_rand = np.random.randint(0, len(edges_to_select))
            edge_idx = edges_to_select[i_rand]

            # delete edge
            edges_to_delete.append(edge_idx)
            del(edges_to_select[i_rand])
            edge = self._edges[edge_idx]
            self._batch.append(edge)

            (i1, i2) = edge
            v1 = self._vertices[i1]
            v2 = self._vertices[i2]
            edges_not_to_select = []

            # 1. At most two vertices may be collapsed into one.
            for i, idx in enumerate(edges_to_select):
                edge = self._edges[idx]
                if i1 in edge or i2 in edge and i not in edges_not_to_select:
                    edges_not_to_select.append(i)

            # 3. For each edge e1 = (v1, v2) that will be collapsed and
            # any edge e2 = (w1,w2) forming a quadrilateral (v1, v2,
            # w1,w2) with e1 in Mi, e1 and e2 cannot be collapsed in
            # the same batch.
            for i, idx in enumerate(edges_to_select):
                (ia, ib) = self._edges[idx]
                diagonal_exists = ia in v1.neighbours or ia in v2.neighbours or ib in v1.neighbours or ib in v2.neighbours
                square_exists = (ia in v1.neighbours and ib in v2.neighbours) or (ib in v1.neighbours and ia in v2.neighbours)
                is_valid_quadrilateral = square_exists and diagonal_exists
                # is_valid_quadrilateral = (self._is_valid_triangle(i1, i2, ia) or self._is_valid_triangle(i1, i2, ib)) and (self._is_valid_triangle(i1, ia, ib) or self._is_valid_triangle(i2, ia, ib))
                if is_valid_quadrilateral and i not in edges_not_to_select:
                    edges_not_to_select.append(i)

            for i in reversed(sorted(edges_not_to_select)):
                del(edges_to_select[i])

        for i in reversed(sorted(edges_to_delete)):
            del(self._edges[i])

    def deletion(self):
        """Renvoie les infos de la prochaine arête à supprimer et la supprime.

        Raises:
            Error: S'il n'y a plus d'arêtes à supprimer ; il faut alors appeler get_m0.

        Returns:
            dict: Contient :
                ``i_del``: l'indice du sommet supprimé
                ``v_del``: les coordonnées du sommet supprimé
                ``f_del``: tuple des deux faces supprimées
                ``f_modified`` : liste des faces modifiées 
        """

        # choose next oriented edge to collapse
        if self._i_batch >= len(self._batch):
            if self._batch:
                print("1 batch OK")
                raise ValueError
            else:
                self.generate_batch()
        (v_del_idx, v_split_idx) = self._batch[self._i_batch]
        self._i_batch += 1


        v_del = self._vertices[v_del_idx]
        v_split = self._vertices[v_split_idx]
        del(self._vertices_exists[self._vertices_exists.index(v_del_idx)])

        result = self.delete_oriented_edge(v_del, v_del_idx, v_split, v_split_idx)
        return result

    def get_M0(self):
        """Retourne le model simplifié.

        Returns:
            _type_: _description_
        """
        M0 = None
        return M0