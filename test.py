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
        self.deleted_faces = set()
        self.deleted_vertices = set()

    def contract(self, output):
        """
        Decimates the model stupidly, and write the resulting obja in output.
        """
        operations = []
        ## Edge collapse
        vsplit_list = [160, 135, 130, 120]
        vdel_list =   [161, 136, 131, 121]
        for vsplit, vdel in zip(vsplit_list, vdel_list):
            print(vsplit, vdel)
            # Iterate through the faces
            for (face_index, face) in enumerate(self.faces):
                if face_index not in self.deleted_faces:
                    if vdel in [face.a,face.b,face.c]:
                        if vsplit in [face.a,face.b,face.c] :
                            # Delete the faces containing vdel and vsplit
                            print(f"supprimer la face : {face}")
                            self.deleted_faces.add(face_index)
                            face.visible = False
                            operations.append(('face', face_index, face))
                        else : 
                            print("pre modif", self.faces[face_index])
                            # Modify the faces lined to vdel faces
                            if vdel == face.a:
                                operations.append(('ef', face_index, face.clone()))
                                face.a = vsplit
                            elif vdel == face.b:
                                operations.append(('ef', face_index, face.clone()))
                                face.b = vsplit
                            else:
                                operations.append(('ef', face_index, face.clone()))
                                face.c = vsplit
                            print("post modif", self.faces[face_index])
                            # if vdel == face.a:
                            #     operations.append(('ev', face.a, self.vertices[vsplit]))
                            # elif vdel == face.b:
                            #     operations.append(('ev', face.b, self.vertices[vsplit]))
                            # else:
                            #     operations.append(('ev', face.c, self.vertices[vsplit]))


            # Delete the vertex
            self.deleted_vertices.add(vdel)
            operations.append(('vertex', vdel, self.vertices[vdel]))

# 160 161
# supprimer la face : Face(159, 161, 160)
#     pre modif Face(155, 128, 161)
#     post modif Face(155, 128, 160)
# pre modif Face(12, 155, 161)
# post modif Face(12, 155, 160)
#     pre modif Face(14, 161, 128)
#     post modif Face(14, 160, 128)
# supprimer la face : Face(14, 160, 161)
#     pre modif Face(12, 161, 159)
#     post modif Face(12, 160, 159)



#         vsplit_list = [142,96]
#         vdel_list = [144, 98]
#         for vsplit, vdel in zip(vsplit_list, vdel_list):
#             print(vsplit, vdel)
#             # Iterate through the faces
#             for (face_index, face) in enumerate(self.faces):

#                 # Delete any face related to this vertex
#                 if face_index not in self.deleted_faces:
#                     if vdel in [face.a,face.b,face.c]:
#                         print(face)
#                         if vsplit in [face.a,face.b,face.c] :
#                             print(f"supprimer la face : {face}")
#                         else : 
#                             if vdel == face.a:
#                                 operations.append(('ev', face.a, self.vertices[vsplit]))
#                             elif vdel == face.b:
#                                 operations.append(('ev', face.b, self.vertices[vsplit]))
#                             else:
#                                 operations.append(('ev', face.c, self.vertices[vsplit]))
# 



        # for (vertex_index, vertex) in enumerate(self.vertices):
        #     operations.append(('ev', vertex_index, vertex + 0.25))

        # Iterate through the vertex
        for (vertex_index, vertex) in enumerate(self.vertices):
            #####
            if vertex_index not in self.deleted_vertices :
            #####
            # Iterate through the faces
                for (face_index, face) in enumerate(self.faces):
                    if face_index not in self.deleted_faces:

                        # Delete any face related to this vertex
                        if vertex_index in [face.a,face.b,face.c]:
                            self.deleted_faces.add(face_index)
                            # Add the instruction to operations stack
                            operations.append(('face', face_index, face))

                # Delete the vertex
                operations.append(('vertex', vertex_index, vertex))

        # To rebuild the model, run operations in reverse order
        operations.reverse()

        # Write the result in output file
        output_model = obja.Output(output, random_color=True)

        for (ty, index, value) in operations:
            print(ty, index, value)
            if ty == "vertex":
                output_model.add_vertex(index, value)
            elif ty == "face":
                output_model.add_face(index, value)   
            elif ty == "ev":
                output_model.edit_vertex(index, value)            
            elif ty == "ef":
                output_model.edit_face(index, value)







# def contract(self, output):
#         """
#         Decimates the model stupidly, and write the resulting obja in output.
#         """
#         operations = []
#         ## Edge collapse
#         vsplit_list = [160, 135, 130,120]
#         vdel_list = [161, 136,131,121]
#         for vsplit, vdel in zip(vsplit_list, vdel_list):
#             print(vsplit, vdel)
#             # Iterate through the faces
#             for (face_index, face) in enumerate(self.faces):

#                 # Delete any face related to this vertex
#                 if face_index not in self.deleted_faces:
#                     if vdel in [face.a,face.b,face.c]:
#                         if vsplit in [face.a,face.b,face.c] :
#                             print(f"supprimer la face : {face}")
#                         else : 
#                             if vdel == face.a:
#                                 operations.append(('ev', face.a, self.vertices[vsplit]))
#                             elif vdel == face.b:
#                                 operations.append(('ev', face.b, self.vertices[vsplit]))
#                             else:
#                                 operations.append(('ev', face.c, self.vertices[vsplit]))

#         vsplit_list = [142,96]
#         vdel_list = [144, 98]
#         for vsplit, vdel in zip(vsplit_list, vdel_list):
#             print(vsplit, vdel)
#             # Iterate through the faces
#             for (face_index, face) in enumerate(self.faces):

#                 # Delete any face related to this vertex
#                 if face_index not in self.deleted_faces:
#                     if vdel in [face.a,face.b,face.c]:
#                         print(face)
#                         if vsplit in [face.a,face.b,face.c] :
#                             print(f"supprimer la face : {face}")
#                         else : 
#                             if vdel == face.a:
#                                 operations.append(('ev', face.a, self.vertices[vsplit]))
#                             elif vdel == face.b:
#                                 operations.append(('ev', face.b, self.vertices[vsplit]))
#                             else:
#                                 operations.append(('ev', face.c, self.vertices[vsplit]))




#         # for (vertex_index, vertex) in enumerate(self.vertices):
#         #     operations.append(('ev', vertex_index, vertex + 0.25))

#         # Iterate through the vertex
#         for (vertex_index, vertex) in enumerate(self.vertices):

#             # Iterate through the faces
#             for (face_index, face) in enumerate(self.faces):

#                 # Delete any face related to this vertex
#                 if face_index not in self.deleted_faces:
#                     if vertex_index in [face.a,face.b,face.c]:
#                         self.deleted_faces.add(face_index)
#                         # Add the instruction to operations stack
#                         operations.append(('face', face_index, face))

#             # Delete the vertex
#             operations.append(('vertex', vertex_index, vertex))

#         # To rebuild the model, run operations in reverse order
#         operations.reverse()

#         # Write the result in output file
#         output_model = obja.Output(output, random_color=True)

#         for (ty, index, value) in operations:
#             if ty == "vertex":
#                 output_model.add_vertex(index, value)
#             elif ty == "face":
#                 output_model.add_face(index, value)   
#             else:
#                 output_model.edit_vertex(index, value)

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









