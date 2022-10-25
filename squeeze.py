#!/usr/bin/env python

import argparse
from datetime import datetime
import os
import shutil
from xmlrpc.client import Boolean
import obja
import numpy as np
import sys
import simulator as sim

class Decimater(obja.Model):
    """
    SQUEZZE
    """
    def __init__(self, color=False):
        super().__init__()
        self.deleted_faces = []
        self.color = color


    def edge_collapse(self, deletion):
        """ Collapse an edge by combining the two vertex into one

        Args
            vsplit: The vertex that is kept to be splitted during the deccompression
            vdel: The deleted vertex during the compression

        Returns:
            operations: The list of the operations carried out for the compression
        """

        operations = []
        i_del = deletion['i_del']
        i_split = deletion['i_split']
        # Delete the faces containing collapsed edge
        for i_face in deletion['f_del']:
            self.deleted_faces.append(i_face)
            operations.append(('new_face', i_face, self.faces[i_face]))

        # Modify the faces linked to the deleted vertex
        for i_face in deletion['f_modified']:
            face = self.faces[i_face]
            if i_del == face.a:
                operations.append(('ef', i_face, face.clone()))
                face.a = i_split
            elif i_del == face.b:
                operations.append(('ef', i_face, face.clone()))
                face.b = i_split
            else:
                operations.append(('ef', i_face, face.clone()))
                face.c = i_split
            self.faces[i_face] = face

        # Delete the vertex
        operations.append(('vertex', i_del, self.vertices[i_del]))

        return operations


    def build_M0(self, M0):
        """ Create the lowest level model

        Args
            M0: The parameters of the compressed model M0

        Returns:
            operations: The list of the operations carried out to create the model
        """
    
        operations = []
        
        # Remove the faces
        for face_index in M0["faces"]:
            self.deleted_faces.append(face_index)
            operations.append(('face', face_index, self.faces[face_index]))

        # Remove the vertex
        for vertex_index in M0["vertices"]:
            operations.append(('vertex', vertex_index, self.vertices[vertex_index]))
        print("M0 Done")
        return operations

    def reset_colors(self):
        operations = []
        
        # if self.deleted_faces:
        for (face_index, face) in enumerate(self.faces):
            if face_index not in self.deleted_faces :
                operations.append(('color_face', face_index, (1,1,1)))
        return operations

    def contract(self, output):
        """
        Decimates the model, and write the resulting obja in output.
        """
        operations = []
        simulator = sim.Simulator(self.vertices, self.faces)

        # Compress thee model
        print("Begining compression")
        compressing = True
        steps = 0
        while compressing:
            steps += 1
            try:
                deletion, new_batch = simulator.deletion()
            except sim.NoMoreCompression:
                print(f"Compression done after {steps} steps.")
                compressing = False
                break
            except sim.GeometricalProblem:
                print(f"Compression stopped because of a geometrical problem : {steps} steps done.")
                compressing = False
                break
            operations += self.edge_collapse(deletion)
            if self.color:
                if steps > 1 and new_batch:
                    operations += self.reset_colors()


        # Build the M0 model
        M0 = simulator.get_M0()
        operations += self.build_M0(M0)

        # To rebuild the model, run operations in reverse order
        operations.reverse()

        # Write the result in output file
        output_model = obja.Output(output, random_color=False)

        # Add the operations
        self.deleted_faces.reverse()
        for (ty, index, value) in operations:
            if ty == "vertex":
                output_model.add_vertex(index, value) 
            elif ty == "ev":
                output_model.edit_vertex(index, value)
            if ty in ("face", "new_face", "ef", "color_face"):
                index = self.deleted_faces.index(index)
                if ty == "face":
                    output_model.add_face(index, value)  
                elif ty == "new_face":
                    output_model.add_face(index, value, color=(0,1,0) * self.color)  
                elif ty == "ef":
                    output_model.edit_face(index, value)
                elif ty == "color_face":
                    output_model.color_face(index, value)
            

def main():
    """
    Runs the program on the model given as parameter.
    """
    # Parse the arguments
    parser = argparse.ArgumentParser(
        description='Convert an obj object to an obja')
    parser.add_argument('obj_file', 
                        help='The name of the obj file (works with or without the .obj)')
    parser.add_argument('--model_directory', 
                        default="example/",
                        help='The directory where the obj model is placed, example/ per default')
    parser.add_argument('--timestamp', '-t',
                        default=False,
                        const=True,
                        action='store_const',
                        help='Create the obja with a timestamp in the name of the file if specified')
    parser.add_argument('--color', '-c',
                        default=False,
                        const=True,
                        action='store_const',
                        help='Color each newly added face for each batch if specified')
    args = parser.parse_args()

    # Get the arguments
    timestamp = args.timestamp
    color = args.color
    obj = args.obj_file.split(".obj")[0]
    obj = obj.split(".obj")[0]
    directory = args.model_directory
    path_to_obj = directory + obj + ".obj"
    path_to_obja = directory + obj + ".obja"


    # Compress the model
    np.seterr(invalid = 'raise')
    model = Decimater(color)
    model.parse_file(path_to_obj)

    # Write the model
    with open(path_to_obja, 'w') as output:
        model.contract(output)

    # Create a copy with a time stamp
    if timestamp:
        now = datetime.now().strftime("_%d_%H%M%S")
        os.makedirs(directory + "timestamped/", exist_ok=True)
        path_to_obja_stamped = directory + "timestamped/" + obj + now + color* "_colored"+  ".obja"
        shutil.copyfile(path_to_obja,path_to_obja_stamped)       


if __name__ == '__main__':
    main()


