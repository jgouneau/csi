#!/usr/bin/env python

import obja
import numpy as np
import sys
import simulator as sim

class Decimater(obja.Model):
    """
    A simple class that decimates a 3D model stupidly.
    """
    def __init__(self):
        super().__init__()

    def contract(self, output):
        """
        Decimates the model stupidly, and write the resulting obja in output.
        """
        operations = []
        simulator = sim.Simulator(self.vertices, self.faces)

        for (vertex_index, vertex) in enumerate(self.vertices):
            operations.append(('vertex', (vertex_index, vertex)))
        for (face_index, face) in enumerate(self.faces):
            operations.append(('face', (face_index, face)))
        
        for i in range(100000):
            try:
                deletion = simulator.deletion()
            except ValueError:
                print(f"Error at step {i}")
                break
            # deletion = dict(
            #     i_del=v_del.idx,
            #     v_del=v_del.coordinates,
            #     f_del=tuple(f_del),
            #     f_modified=f_modified,
            # )
            operations.append(('del_face', deletion['f_del'][0]))
            operations.append(('del_face', deletion['f_del'][1]))
            for f_modified in deletion['f_modified']:
                operations.append(('edit_face', (f_modified, deletion['i_del'], deletion['i_split'])))

        # Write the result in output file
        output_model = obja.Output(output, random_color=False)

        for operation in operations:
            ty, args = operation
            if ty == "vertex":
                (index, value) = args
                output_model.add_vertex(index, value)
            elif ty == "face":
                (index, value) = args
                output_model.add_face(index, value)   
            elif ty == "del_face":
                face_id = args
                face = self.faces[face_id]
                # face.a = 0
                # face.b = 0
                # face.c = 0
                output_model.edit_face(face_id, face, color=True)
            elif ty == "edit_face":
                (face_id, i_del, i_split) = args
                face = self.faces[face_id]
                v_idx_in_face = [face.a, face.b, face.c].index(i_del)
                # setattr(face, ['a', 'b', 'c'][v_idx_in_face], i_split)
                self.faces[face_id] = face
                output_model.edit_face(face_id, face)
            else:
                (index, value) = args
                output_model.edit_vertex(index, value)

def main():
    """
    Runs the program on the model given as parameter.
    """
    np.seterr(invalid = 'raise')
    model = Decimater()
    model.parse_file('example/bunny.obj')

    with open('example/bunny.obja', 'w') as output:
        model.contract(output)


if __name__ == '__main__':
    main()
