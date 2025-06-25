import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

from scintillator_display.compat.universal_values import MathDisplayValues
from scintillator_display.display.impl_compatibility.data_manager import Data
from scintillator_display.display.impl_compatibility.vao_vbo import create_vao, update_vbo, draw_vao





class ScintillatorBlocks(MathDisplayValues):
    def __init__(self, data_manager:Data, c1=[1, 0, 0], c2=[0, 1, 0], alpha=1):

        self.c1, self.c2 = c1, c2
        self.alpha = alpha
        self.data_manager = data_manager

        self.build_structure(
                        num_doubles      =               self.NUM_SCINTILLATOR_XY_PER_STRUCTURE, # 3 each
                        x_i              =               0,
                        y_i              =               0,
                        z_i              =               0,
                        square_side_len  =               self.SQUARE_LEN, # mm
                        width_per_one    =               self.SCINTILLATOR_THICKNESS, # mm
                        dead_space       =               self.SPACE_BETWEEN_SCINTILLATORS, # mm
                        c1               =               self.c1,
                        c2               =               self.c2,
                        alpha            =               self.alpha,
                        in_between_space =               self.SPACE_BETWEEN_STRUCTURES, # mm
                        )


    def build_structure(self,
                        num_doubles, x_i, y_i, z_i,
                        square_side_len, width_per_one, dead_space,
                        c1, c2, alpha, in_between_space):

        middle_offset = in_between_space/2




        '''
        x is first  ; 0
        y is second ; 1        
        '''

        

        sipm_rods = []

        # top half
        for double in range(num_doubles):
            num_rods = 2**(double+1)
            for layer in range(2):
                base_x, base_y, base_z = x_i, y_i, (z_i + middle_offset +
                                                    (width_per_one+dead_space)*(2*double+layer))
                
                # base_x = base_y = 0, so the choice is irrelevant
                basepoints = np.linspace(base_x, base_x+square_side_len, num_rods, endpoint=False)
                dist_bpoints = basepoints[1]-basepoints[0]

                this_sipm_rod = []

                for rod, s in enumerate(basepoints):
                    prism = self.data_manager.make_prism_triangles(
                        *self.data_manager.make_points_from_high_low(
                            xl = s if not layer else base_x,
                            xh = s + dist_bpoints if not layer else square_side_len,
                            yl = square_side_len - s - dist_bpoints if layer else square_side_len,
                            yh = square_side_len - s if layer else base_y,
                            zl = base_z,
                            zh = base_z + width_per_one,
                            c  = c2 if rod%2 else c1,
                            a  = alpha,
                            is_restructured=True
                        ),
                        show_top_bottom=True
                    )
                    this_sipm_rod.append(prism)
                sipm_rods.append(np.array(this_sipm_rod[::2]))
                sipm_rods.append(np.array(this_sipm_rod[1::2]))

        # bottom half
        for double in range(num_doubles):
            num_rods = 2**(double+1)
            for layer in range(2):
                base_x, base_y, base_z = x_i, y_i, -(+z_i + middle_offset +
                                                    (width_per_one+dead_space)*(2*double+layer))
                
                # base_x = base_y = 0, so the choice is irrelevant
                basepoints = np.linspace(base_x, base_x+square_side_len, num_rods, endpoint=False)
                dist_bpoints = basepoints[1]-basepoints[0]

                this_sipm_rod = []

                for rod, s in enumerate(basepoints):
                    prism = self.data_manager.make_prism_triangles(
                        *self.data_manager.make_points_from_high_low(
                            xl = s if layer else base_x,
                            xh = s + dist_bpoints if layer else square_side_len,
                            yl = square_side_len - s - dist_bpoints if not layer else square_side_len,
                            yh = square_side_len - s if not layer else base_y,
                            zl = base_z,
                            zh = base_z - width_per_one,
                            c  = c2 if rod%2 else c1,
                            a  = alpha,
                            is_restructured=True
                        ),
                        show_top_bottom=True
                    )
                    this_sipm_rod.append(prism)
                sipm_rods.append(np.array(this_sipm_rod[::2]))
                sipm_rods.append(np.array(this_sipm_rod[1::2]))


        '''
        creates np.array having letter-codes:
        [A, B, M, N, E, F, Q, R, I, J, U, V, O, P, C, D, S, T, G, H, W, X, K, L]
        idx to ABC...VWX:
        [A, B,  C,  D, E, F,  G,  H, I, J,  K,  L, M, N,  O,  P, Q, R,  S,  T,  U,  V,  W,  X]
        [0, 1, 14, 15, 4, 5, 18, 19, 8, 9, 22, 23, 2, 3, 12, 13, 6, 7, 16, 17, 10, 11, 20, 21]
        '''
        

        idx_conversion = [0, 1, 14, 15, 4, 5, 18, 19,  8,  9, 22, 23,
                          2, 3, 12, 13, 6, 7, 16, 17, 10, 11, 20, 21]

        sorted_sipm = []
        for idx in idx_conversion:
            sorted_sipm.append(sipm_rods[idx])

        self.data = sorted_sipm

        self.make_vao()

    def reset_to_initial_colour(self):
        for i, data in enumerate(self.data):
            self.data[i][:, :, 3:7] = [*(self.c2 if i%2 else self.c1), self.alpha]

    
    def light_scintillators_for_hit(self, point):
        binary=self.data_manager.num_to_raw_binary(point.int_number)
        yellow = [1, 1, 1, 0.75]
        for i, binary_value in enumerate(binary):
            if binary_value:
                self.data[i][:, :, 3:7] = yellow

    def data_to_triangles_for_draw(self):
        triangles = []
        for sipm in self.data:
            for prism in sipm:
                for t in prism:
                    triangles.extend(t)

        return np.array(triangles, dtype=np.float32)
        
    def make_vao(self):
        self.triangles = self.data_to_triangles_for_draw()
        self.triangles_vao, self.triangles_vbo = create_vao(self.triangles, return_vbo=True, store_normals=True)

    def renew_vbo(self):
        self.triangles = self.data_to_triangles_for_draw()
        update_vbo(self.triangles_vbo, self.triangles)

    def draw_scintillator_structure(self):
        draw_vao(self.triangles_vao, GL_TRIANGLES, self.triangles.shape[0])