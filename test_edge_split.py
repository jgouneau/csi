#!/usr/bin/env python

import obja
import numpy as np
import sys

class Decimater(obja.Model):
    """
    A simple class that decimates a 3D model stupidly.
    """
    def __init__(self):
        super().__init__()
        # self.deleted_faces = set()
        # self.deleted_vertices = set()
        self.deleted_faces = []
        self.deleted_vertices = []

    def contract(self, output):
        """
        Decimates the model stupidly, and write the resulting obja in output.
        """
        operations = []

        ## sphere
        vsplit_list = [160, 135, 130, 120, 141, 95]
        vdel_list =   [161, 136, 131, 121, 143, 97]

        ## Edge collapse
        for vsplit, vdel in zip(vsplit_list, vdel_list):
            # Iterate through the faces
            for (face_index, face) in enumerate(self.faces):
                if face_index not in self.deleted_faces:
                    if vdel in [face.a,face.b,face.c]:
                        if vsplit in [face.a,face.b,face.c] :
                            # Delete the faces containing vdel and vsplit
                            self.deleted_faces.append(face_index)
                            operations.append(('face_color', face_index, face))

                        else : 
                            # Modify the faces linked to vdel
                            if vdel == face.a:
                                operations.append(('ef', face_index, face.clone()))
                                face.a = vsplit
                            elif vdel == face.b:
                                operations.append(('ef', face_index, face.clone()))
                                face.b = vsplit
                            else:
                                operations.append(('ef', face_index, face.clone()))
                                face.c = vsplit
                            
                            self.faces[face_index] = face

            # Delete the vertex
            self.deleted_vertices.append(vdel)
            operations.append(('vertex', vdel, self.vertices[vdel]))

        #Build the M0 model
        # Iterate through the vertex
        for (vertex_index, vertex) in enumerate(self.vertices):
            if vertex_index not in self.deleted_vertices :
            # Iterate through the faces
                for (face_index, face) in enumerate(self.faces):
                    if face_index not in self.deleted_faces:

                        # Delete any face related to this vertex
                        if vertex_index in [face.a,face.b,face.c]:
                            self.deleted_faces.append(face_index)
                            # Add the instruction to operations stack
                            operations.append(('face', face_index, face))

                # Delete the vertex
                self.deleted_vertices.append(vertex_index)
                operations.append(('vertex', vertex_index, vertex))

        # To rebuild the model, run operations in reverse order
        operations.reverse()

        # Modify the index of the faces
        modified_operations = []
        self.deleted_faces.reverse()
        for (ty, index, value) in operations :
            if ty in ("face", "face_color", "ef"):
                index = self.deleted_faces.index(index)
            modified_operations.append((ty, index, value))

        # Write the result in output file
        output_model = obja.Output(output, random_color=True)

        out = open("output.txt", "w")
        for (ty, index, value) in modified_operations:
            out.write(f"{ty} {index} {value}\n")
        out.close()

        # Add the operations
        for (ty, index, value) in modified_operations:
            if ty == "vertex":
                output_model.add_vertex(index, value)
            elif ty == "face":
                output_model.add_face(index, value)  
            elif ty == "face_color":
                output_model.add_face(index, value, color=(0,1,0))   
            elif ty == "ev":
                output_model.edit_vertex(index, value)            
            elif ty == "ef":
                output_model.edit_face(index, value)

def main():
    """
    Runs the program on the model given as parameter.
    """
    np.seterr(invalid = 'raise')
    model = Decimater()
    model.parse_file('example/sphere.obj')

    with open('example/sphere.obja', 'w') as output:
        model.contract(output)


if __name__ == '__main__':
    main()

















# #!/usr/bin/env python

# import obja
# import numpy as np
# import sys

# class Decimater(obja.Model):
#     """
#     A simple class that decimates a 3D model stupidly.
#     """
#     def __init__(self):
#         super().__init__()
#         # self.deleted_faces = set()
#         # self.deleted_vertices = set()
#         self.deleted_faces = []
#         self.deleted_vertices = []

#     def contract(self, output):
#         """
#         Decimates the model stupidly, and write the resulting obja in output.
#         """
#         operations = []

#         ## sphere
#         vsplit_list = [160, 135, 130, 120]
#         vdel_list =   [161, 136, 131, 121]

#         vsplit_list += [141,95]
#         vdel_list += [143, 97]


#         ## Edge collapse
#         for vsplit, vdel in zip(vsplit_list, vdel_list):
#             print(vsplit, vdel)
#             # Iterate through the faces
#             for (face_index, face) in enumerate(self.faces):
#                 if face_index not in self.deleted_faces:
#                     if vdel in [face.a,face.b,face.c]:
#                         if vsplit in [face.a,face.b,face.c] :
#                             # Delete the faces containing vdel and vsplit
#                             print(f"supprimer la face : {face}")
#                             self.deleted_faces.append(face_index)
#                             # face.visible = False
#                             operations.append(('face_color', face_index, face))
#                             # operations.append(('face_color', nb_face - len(self.deleted_faces), face))

#                         else : 
#                             print("pre modif", face_index, self.faces[face_index])
#                             # Modify the faces linked to vdel
#                             if vdel == face.a:
#                                 # face.a = vsplit
#                                 operations.append(('ef', face_index, face.clone()))
#                                 face.a = vsplit
#                             elif vdel == face.b:
#                                 # face.b = vsplit
#                                 operations.append(('ef', face_index, face.clone()))
#                                 face.b = vsplit
#                             else:
#                                 # face.c = vsplit
#                                 operations.append(('ef', face_index, face.clone()))
#                                 face.c = vsplit
                            
#                             self.faces[face_index] = face
#                             # print("post modif", self.faces[face_index])

#             # Delete the vertex
#             self.deleted_vertices.append(vdel)
#             operations.append(('vertex', vdel, self.vertices[vdel]))




#         # for (vertex_index, vertex) in enumerate(self.vertices):
#         #     operations.append(('ev', vertex_index, vertex + 0.25))

#         # Iterate through the vertex
#         for (vertex_index, vertex) in enumerate(self.vertices):
#             #####
#             if vertex_index not in self.deleted_vertices :
#             #####
#             # Iterate through the faces
#                 for (face_index, face) in enumerate(self.faces):
#                     if face_index not in self.deleted_faces:

#                         # Delete any face related to this vertex
#                         if vertex_index in [face.a,face.b,face.c]:
#                             self.deleted_faces.append(face_index)
#                             # Add the instruction to operations stack
#                             operations.append(('face', face_index, face))

#                 # Delete the vertex
#                 self.deleted_vertices.append(vertex_index)
#                 operations.append(('vertex', vertex_index, vertex))

#         # To rebuild the model, run operations in reverse order
#         operations.reverse()

#         # Change the index order for the faces and vertex
#         test = []
    



#         # self.deleted_vertices.reverse()
#         self.deleted_faces.reverse()
#         ### surment changer les valeurs des faces et pas les indices, à revoir
#         # print(self.deleted_faces)
#         print(self.deleted_vertices)
#         for (ty, index, value) in operations :
#             if ty in ("vertex", "ev"):
#                 # print(self.deleted_vertices.index(index))
#                 # print(f"index = {index}, new_index = {self.deleted_vertices.index(index)}")
#                 # index = self.deleted_vertices.index(index)
#                 i = 0
#             else :
#                 # Modifier les faces pour correspondre au nouvel index
#                 index = self.deleted_faces.index(index)

#             test.append((ty, index, value))

#         operations = test


#         # Write the result in output file
#         output_model = obja.Output(output, random_color=True)

#         out = open("output.txt", "w")
#         for (ty, index, value) in operations:
#             out.write(f"{ty} {index} {value}\n")
#         out.close()

#         for (ty, index, value) in operations:
#             if ty == "vertex":
#                 output_model.add_vertex(index, value)
#             elif ty == "face":
#                 output_model.add_face(index, value)  
#             elif ty == "face_color":
#                 output_model.add_face(index, value, color=(0,1,0))   
#             elif ty == "ev":
#                 output_model.edit_vertex(index, value)            
#             elif ty == "ef":
#                 output_model.edit_face(index, value)


# def main():
#     """
#     Runs the program on the model given as parameter.
#     """
#     np.seterr(invalid = 'raise')
#     model = Decimater()
#     model.parse_file('example/sphere.obj')

#     with open('example/sphere.obja', 'w') as output:
#         model.contract(output)


# if __name__ == '__main__':
#     main()









