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

        i = 0
        # top half
        for double in range(num_doubles):
            num_rods = 2**(double+1)
            for xy in range(2):
                for tb in range(2):

                    absolute_z = (z_i + middle_offset + (width_per_one+dead_space)*(2*double+xy))

                    basepoints = np.linspace(x_i, x_i+square_side_len, num_rods, endpoint=False)
                    dist_bpoints = basepoints[1]-basepoints[0]

                    this_sipm_rod = []

                    for rod, s in enumerate(basepoints):

                        this_sipm_rod.append(
                            self.make_prism_triangles(
                                *self.make_points_from_high_low(
                                xl = s if (not tb^xy) else x_i,
                                xh = s + dist_bpoints if (not tb^xy) else square_side_len,
                                yl = square_side_len - s - dist_bpoints if (tb^xy) else square_side_len,
                                yh = square_side_len - s if (tb^xy) else y_i,
                                zl = (-1)**tb * (absolute_z),
                                zh = (-1)**tb * (absolute_z + width_per_one),
                                c  = c2 if rod%2 else c1,
                                a  = alpha,
                                ),
                                show_top_bottom=True
                            )
                        )
                    sipm_rods.append(np.array(this_sipm_rod[ ::2]))
                    sipm_rods.append(np.array(this_sipm_rod[1::2]))



        '''
        creates np.array having letter-codes:
        [A, B, O, P, M, N, C, D, E, F, S, T, Q, R, G, H, I, J, W, X, U, V, K, L]
        idx to ABC...VWX:
        [A, B, C, D, E, F,  G,  H,  I,  J,  K,  L, M, N, O, P,  Q,  R,  S,  T,  U,  V,  W,  X]
        [0, 1, 6, 7, 8, 9, 14, 15, 16, 17, 22, 23, 4, 5, 2, 3, 12, 13, 10, 11, 20, 21, 18, 19]
        '''

        idx_conversion = [0, 1, 6, 7, 8, 9, 14, 15, 16, 17, 22, 23,
                          4, 5, 2, 3, 12, 13, 10, 11, 20, 21, 18, 19]
        
        sorted_sipm = []
        for idx in idx_conversion:
            sorted_sipm.append(sipm_rods[idx])

        self.data = sorted_sipm

        self.make_vao()

    def make_points_from_high_low(self, xl, xh, yl, yh, zl, zh, c, a):
        points = np.array([
            np.array([xl, yl, zl, *c, a, xl, yl, zl]), # base_point + (0,    0,    0)    # BFL
            np.array([xh, yl, zl, *c, a, xh, yl, zl]), # base_point + (xlen, 0,    0)    # BFR
            np.array([xl, yh, zl, *c, a, xl, yh, zl]), # base_point + (0,    ylen, 0)    # BBL
            np.array([xh, yh, zl, *c, a, xh, yh, zl]), # base_point + (xlen, ylen, 0)    # BBR
            np.array([xl, yl, zh, *c, a, xl, yl, zh]), # base_point + (0,    0,    zlen) # TFL
            np.array([xh, yl, zh, *c, a, xh, yl, zh]), # base_point + (xlen, 0,    zlen) # TFR
            np.array([xl, yh, zh, *c, a, xl, yh, zh]), # base_point + (0,    ylen, zlen) # TBL
            np.array([xh, yh, zh, *c, a, xh, yh, zh]), # base_point + (xlen, ylen, zlen) # TBR
        ])
        return points
    

    def make_prism_triangles(self, p1, p2, p3, p4, p5, p6, p7, p8, show_top_bottom=True):

        '''
        one base has changing basepoints and x_increment of rod width
        one base has fixed basepoint and square side length increment
        z starts from box base z and add box z increment
        '''

        # front face
        tf1 = [p1, p2, p5]
        tf2 = [p2, p5, p6]

        # back face
        tb1 = [p3, p4, p7]
        tb2 = [p4, p7, p8]
        
        # left face
        tl1 = [p1, p3, p5]
        tl2 = [p3, p5, p7]

        # right face
        tr1 = [p2, p4, p6]
        tr2 = [p4, p6, p8]

        all_t = []

        all_t.extend(tf1)
        all_t.extend(tf2)
        all_t.extend(tb1)
        all_t.extend(tb2)
        all_t.extend(tl1)
        all_t.extend(tl2)
        all_t.extend(tr1)
        all_t.extend(tr2)


        if show_top_bottom:
            # bottom face
            tB1 = [p1, p2, p3]
            tB2 = [p2, p3, p4]
            # top face
            tT1 = [p5, p6, p7]
            tT2 = [p6, p7, p8]
            all_t.extend(tB1)
            all_t.extend(tB2)
            all_t.extend(tT1)
            all_t.extend(tT2)

        return np.array(all_t)    

    def reset_to_initial_colour(self):
        for i, data in enumerate(self.data):
            self.data[i][:, :, 3:7] = [*(self.c2 if i%2 else self.c1), self.alpha]
        
        #self.data[23][:, :, 3:7]=[0, 0, 0, 1]


    
    def light_scintillators_for_hit(self, point):
        binary=self.data_manager.num_to_raw_binary(point.int_number)
        yellow = [1, 1, 0, 0.75]
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