from multiprocessing.sharedctypes import Value
import numpy as np
import obja

class Vertex:
    """Classe simplifiant la représentation/manipulation de la connectivité d'un sommet
    """
    def __init__(self, idx, vertex, faces):
        self.idx = idx
        self.coordinates = vertex
        self.neighbours = []
        for face in faces:
            face_idx = [face.a, face.b, face.c]
            if idx in face_idx:
                for neighbor in face_idx:
                    self.add_neighbor(neighbor)
        self.is_deleted = False
    
    def delete_neighbor(self, v_del_idx):
        del(self.neighbours[self.neighbours.index(v_del_idx)])
    
    def add_neighbor(self, v_add_idx):
        if v_add_idx not in self.neighbours and v_add_idx != self.idx:
            self.neighbours.append(v_add_idx)


class Face(obja.Face):
    def __init__(self, a, b, c, visible=True):
        super().__init__(a, b, c, visible)
        self.is_deleted = False


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
        assert not problem

        self._faces = [Face(face.a, face.b, face.c) for face in faces]
        self._edges = []
        self._vertices = [Vertex(idx, vertex, faces) for idx, vertex in enumerate(vertices)]

    def delete_oriented_edge(self, v_del, v_split):
        # delete the two faces that contain v_del and v_split
        f_del = []
        for i, face in enumerate(self._faces):
            if not face.is_deleted and v_del.idx in [face.a, face.b, face.c] and v_split.idx in [face.a, face.b, face.c]:
                f_del.append(i)
                self._faces[i].is_deleted = True
        if len(f_del) != 2:
            raise(ValueError)
        
        # modify the faces that contain v_del only
        f_modified = []
        for i, face in enumerate(self._faces):
            if not face.is_deleted and v_del.idx in [face.a, face.b, face.c]:
                f_modified.append(i)
                v_idx_in_face = [face.a, face.b, face.c].index(v_del.idx)
                setattr(face, ['a', 'b', 'c'][v_idx_in_face], v_split.idx)
                self._faces[i] = face
        
        # delete the edges linking v_del to its neighbours and link them to v_split
        neighbours = v_del.neighbours
        for i in neighbours:
            neighbor = self._vertices[i]
            neighbor.delete_neighbor(v_del.idx)
            neighbor.add_neighbor(v_split.idx)
            v_split.add_neighbor(i)
            self._vertices[i] = neighbor
        self._vertices[v_split.idx] = v_split
        self._vertices[v_del.idx] = v_del

        result = dict(
            i_del=v_del.idx,
            i_split=v_split.idx,
            v_del=v_del.coordinates,
            f_del=tuple(f_del),
            f_modified=f_modified,
        )
        return result

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
        found = False
        while not found:
            v_del = self._vertices[np.random.randint(0, len(self._vertices))]
            found = not v_del.is_deleted
        v_del.is_deleted = True
        neighbours = v_del.neighbours
        v_split = self._vertices[neighbours[np.random.randint(0, len(neighbours))]]

        result = self.delete_oriented_edge(v_del, v_split)
        return result

    def get_M0(self):
        """Retourne le model simplifié.

        Returns:
            _type_: _description_
        """
        M0 = None
        return M0