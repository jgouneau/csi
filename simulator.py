from tkinter import SEL_FIRST
import numpy as np


class NoMoreCompression(Exception):
    pass

class GeometricalProblem(Exception):
    pass

class Vertex:
    """Classe simplifiant la représentation/manipulation de la connectivité d'un sommet
    """
    def __init__(self, idx, vertex, edges, faces):
        self.idx = idx
        self.coordinates = vertex
        self.neighbours = []
        for edge in edges:
            (a, b) = edge
            if idx == a:
                self.add_neighbor(b)
            elif idx == b:
                self.add_neighbor(a)
        self.nearfaces = []
        for i, face in enumerate(faces):
            if idx in [face.a, face.b, face.c]:
                self.nearfaces.append(i)
    
    def del_neighbor(self, v_del_idx):
        del(self.neighbours[self.neighbours.index(v_del_idx)])
    
    def add_neighbor(self, v_add_idx):
        if v_add_idx not in self.neighbours and v_add_idx != self.idx:
            self.neighbours.append(v_add_idx)
        
    def del_nearface(self, f_del_idx):
        if f_del_idx in self.nearfaces:
            del(self.nearfaces[self.nearfaces.index(f_del_idx)])
    
    def add_nearface(self, f_add_idx):
        if f_add_idx not in self.nearfaces:
            self.nearfaces.append(f_add_idx)


class Simulator:
    """
    Classe permettant la simulation d'une compression d'un objet 3D suivant l'algorithme SQUEEZE 

    Args:
            vertices (list(np.array)): list of 3-elements np.arrays containing the x, y, z coordinates.
            faces (list(Face)): list of Faces objects containing the indexes a, b, c of the vertices in a face. 
    """
    def __init__(self, vertices, faces):
        self._faces = [face.clone() for face in faces]
        self._faces_exists = list(range(len(faces)))
        self._edges = []
        for face in faces:
            self._add_face_edges(face)
        self._vertices = [Vertex(idx, vertex, self._edges, self._faces) for idx, vertex in enumerate(vertices)]
        self._vertices_exists = list(range(len(vertices)))
        self._batch = []
        self._i_batch = 0
    
    def _add_face_edges(self, face):
        for (a, b) in [(face.a, face.b), (face.b, face.c), (face.c, face.a)]:
            if (a, b) not in self._edges and (b, a) not in self._edges:
                self._edges.append((a, b))

    def delete_oriented_edge(self, v_del, i_del, v_split, i_split):
        neighbours = v_del.neighbours

        # modify the faces that contain v_del only and delete the two faces that contain v_del and v_split
        f_del = []
        f_modified = []
        for i in v_del.nearfaces:
            face = self._faces[i]
            if i_split in [face.a, face.b, face.c]:
                f_del.append(i)
            else:
                f_modified.append(i)
                v_split.add_nearface(i)
                v_idx_in_face = [face.a, face.b, face.c].index(i_del)
                setattr(face, ['a', 'b', 'c'][v_idx_in_face], i_split)
                self._faces[i] = face
        if len(f_del) != 2:
            raise GeometricalProblem(f"Edge to delete is part of {len(f_del)} triangles instead of 2.")

        common_neighbours = []
        for i in f_del:
            face = self._faces[i]
            for idx in [face.a, face.b, face.c]:
                if idx != i_del and idx != i_split:
                    common_neighbours.append(idx)
        if len(common_neighbours) != 2:
            raise GeometricalProblem(f"Edge to delete has {len(common_neighbours)} common neighbours with v_split, instead of 2.")
        n_1 = common_neighbours[0]
        n_2 = common_neighbours[1]
        for i in f_del:
            del(self._faces_exists[self._faces_exists.index(i)])
            for n in neighbours:
                neighbor = self._vertices[n]
                neighbor.del_nearface(i)

        # modify the edges that contain v_del only and delete the edges to v_del of neighbours common to v_split and v_del
        edges_to_delete = []
        for i, edge in enumerate(self._edges):
            if i_del in edge:
                if n_1 in edge or n_2 in edge or i_split in edge:
                    edges_to_delete.append(i)
                else:
                    (a, b) = edge
                    if i_del == a:
                        a = i_split
                    else:
                        b = i_split
                    self._edges[i] = (a, b)
        if len(edges_to_delete) != 3:
            raise GeometricalProblem(f"No the right number of edges were deleted : {len(edges_to_delete)} instead of 3.")
        for i in reversed(sorted(edges_to_delete)):
            del(self._edges[i])
        
        # delete the edges linking v_del to its neighbours and link them to v_split
        for i in neighbours:
            neighbor = self._vertices[i]
            neighbor.del_neighbor(i_del)
            neighbor.add_neighbor(i_split)
            v_split.add_neighbor(i)
            self._vertices[i] = neighbor
        self._vertices[i_split] = v_split
        self._vertices[i_del] = v_del

        result = dict(
            i_del=i_del,
            i_split=i_split,
            v_del=v_del.coordinates,
            f_del=tuple(f_del),
            f_modified=f_modified,
        )
        return result
    
    def _is_valid_triangle(self, v1, v2, w, faces):
        valid = False
        for i in faces:
            face = self._faces[i]
            face_idx = [face.a, face.b, face.c]
            if w in face_idx and v1 in face_idx and v2 in face_idx:
                valid = True
                break
        return valid

    def generate_batch(self):
        self._batch = []
        self._i_batch = 0
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
            nearfaces = []
            for nearface in v1.nearfaces:
                if nearface in v2.nearfaces:
                    nearfaces.append(nearface)
            valid = True
            for w in neighbours:
                valid *= self._is_valid_triangle(i1, i2, w, nearfaces)
            valid *= len(neighbours) == 2
            if valid and len(neighbours) > 1:
                edges_to_select.append(i)

        while edges_to_select:
            # select edge
            costs = []
            for i in edges_to_select:
                selected_edge = self._edges[i]
                i1,i2 = selected_edge
                v1 = self._vertices[i1]
                v2 = self._vertices[i2]
                cost_v1 = self.get_contraction_cost(v1)
                cost_v2 = self.get_contraction_cost(v2)
                costs.append(cost_v1)
                costs.append(cost_v2)
            argmin = np.argmin(costs)
            v_del_first = argmin%2 == 0
            if v_del_first:
                idx = argmin//2
            else:
                idx = (argmin-1)//2

            # delete edge
            edge_idx = edges_to_select[idx]
            del(edges_to_select[idx])
            i1, i2 = self._edges[edge_idx]
            if v_del_first:
                edge_del = (i1, i2)
            else:
                edge_del = (i2, i1)
            self._batch.append(edge_del)

            v1 = self._vertices[i1]
            v2 = self._vertices[i2]
            edges_not_to_select = []


            for i, idx in enumerate(edges_to_select):
                # 1. At most two vertices may be collapsed into one.
                edge = self._edges[idx]
                if i1 in edge or i2 in edge and i not in edges_not_to_select:
                    edges_not_to_select.append(i)
                    
                # 3. For each edge e1 = (v1, v2) that will be collapsed and
                # any edge e2 = (w1,w2) forming a quadrilateral (v1, v2,
                # w1,w2) with e1 in Mi, e1 and e2 cannot be collapsed in
                # the same batch.
                (ia, ib) = self._edges[idx]
                diagonal_exists = ia in v1.neighbours or ia in v2.neighbours or ib in v1.neighbours or ib in v2.neighbours
                square_exists = (ia in v1.neighbours and ib in v2.neighbours) or (ib in v1.neighbours and ia in v2.neighbours)
                is_valid_quadrilateral = square_exists and diagonal_exists
                # is_valid_quadrilateral = (self._is_valid_triangle(i1, i2, ia) or self._is_valid_triangle(i1, i2, ib)) and (self._is_valid_triangle(i1, ia, ib) or self._is_valid_triangle(i2, ia, ib))
                if is_valid_quadrilateral and i not in edges_not_to_select:
                    edges_not_to_select.append(i)

            for i in reversed(sorted(edges_not_to_select)):
                del(edges_to_select[i])

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
        new_batch = False
        if self._i_batch >= len(self._batch):
            self.generate_batch()
            print(f"Next batch: {len(self._batch)} edges selected")
            new_batch = True
        if not self._batch:
            raise NoMoreCompression("No more edges respecting the topological constraints")
        (i_del, i_split) = self._batch[self._i_batch]
        self._i_batch += 1


        v_del = self._vertices[i_del]
        v_split = self._vertices[i_split]
        del(self._vertices_exists[self._vertices_exists.index(i_del)])

        result = self.delete_oriented_edge(v_del, i_del, v_split, i_split)
        return result, new_batch

    def get_M0(self):
        """Retourne le model simplifié.

        Returns:
            _type_: _description_
        """
        M0 = {"faces": self._faces_exists, "vertices": self._vertices_exists}
        return M0

    def get_Q_matrix(self, v):
        """Retourne la matrice Q permettant le calcul de l'erreur sur un sommet"""

        near_faces = v.nearfaces
        Q = np.zeros((4,4))
        for i in near_faces:
            face = self._faces[i]

            # Nous choisissons 2 vecteurs appartenant au plan définit par la face
            vec1 = self._vertices[face.c].coordinates - self._vertices[face.a].coordinates 
            vec2 = self._vertices[face.b].coordinates - self._vertices[face.a].coordinates
            
            #Nous cherchons à obtenir les 4 coefficients (x,y,z,d) de l'équation du plan défini par la face
            cp = np.cross(vec1, vec2)
            x, y, z = cp
            d = np.dot(cp, self._vertices[face.c].coordinates)

            Q += np.array([[x*x,x*y,x*z,x*d],
                           [x*y, y*y,y*z, y*d],
                           [x*z, y*z, z*z, z*d],
                           [x*d, y*d, z*d, d*d]])
        return Q
    
    def get_contraction_cost(self, v):

        """Retourne le cout/erreur associé à un sommet"""

        a,b,c = v.coordinates
        v_transpose = np.array([[a,b,c,1]])
        v_regular = v_transpose.transpose()
        Q = self.get_Q_matrix(v)

        cost = np.matmul(np.matmul(v_transpose , Q),v_regular)[0][0]
        return cost