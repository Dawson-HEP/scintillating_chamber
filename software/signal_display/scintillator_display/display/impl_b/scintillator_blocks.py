import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *


from scintillator_display.display.impl_compatibility.vao_vbo import create_vao, update_vbo, draw_vao

from scintillator_display.compat.universal_values import MathDisplayValues

from scintillator_display.display.impl_compatibility.data_manager import Data

from scintillator_display.display.impl_compatibility.scintillator_blocks_build import ScintillatorBlocks


class ScintillatorStructure(MathDisplayValues):
    def __init__(self, data_manager:Data):
        self.data_manager = data_manager
        self.setup_structure(
                        num_doubles      =               self.NUM_SCINTILLATOR_XY_PER_STRUCTURE, # 3 each
                        x_i              =               0,
                        y_i              =               0,
                        z_i              =               0,
                        square_side_len  =               self.SQUARE_LEN, # mm
                        width_per_one    =               self.SCINTILLATOR_THICKNESS, # mm
                        dead_space       =               self.SPACE_BETWEEN_SCINTILLATORS, # mm
                        c1               = [1, 0.75, 0.75,],
                        c2               = [0.75, 1, 0.75,],
                        alpha            =           [0.8],
                        in_between_space =               self.SPACE_BETWEEN_STRUCTURES, # mm
                        )
        self.make_vao()

        k = ScintillatorBlocks(data_manager=data_manager)


    def make_prism_triangles(self, low_x, high_x, low_y, high_y, low_z, high_z):      
        points = self.data_manager.make_points_from_high_low(
            low_x, high_x, low_y, high_y, low_z, high_z)

        all_t = self.data_manager.make_prism_triangles(*points, show_top_bottom=True)

        return all_t

    def setup_structure(self,
                        num_doubles, x_i, y_i, z_i,
                        square_side_len, width_per_one, dead_space,
                        c1, c2, alpha, in_between_space):

        
        num_doubles = num_doubles
        initial_x, initial_y, initial_z = x_i, y_i, z_i
        square_side_len = square_side_len

        width_per_one = width_per_one
        dead_space = dead_space

        self.c1 = c1
        self.c2 = c2
        alpha = alpha

        vertices = []

        colours = []

        order_added = [6,5,4,3,2,1,8,7,10,9,12,11]


        for double in range(num_doubles):
            z_change = width_per_one
            base_x, base_y, base_z = initial_x, initial_y, initial_z + double*(2*width_per_one+2*dead_space)

            num_rods = 2**(double+1)

            basepoints = np.linspace(base_x, base_x+square_side_len, num_rods, endpoint=False)
            dist_bpoints = basepoints[1]-basepoints[0]


            "xy"

            for rod, s in enumerate(basepoints):

                z_start = base_z

                colour = self.c1 if rod%2==0 else self.c2
                colours.append(colour)

                #print(self.make_prism_triangles(
                #        low_x=s,
                #        high_x=s+dist_bpoints,
                #        low_y=base_y,
                #        high_y=base_y+square_side_len,
                #        low_z=z_start,
                #        high_z=z_start+z_change,
                #        ))

                vertices.extend(
                    self.make_prism_triangles(
                        low_x=s,
                        high_x=s+dist_bpoints,
                        low_y=base_y,
                        high_y=base_y+square_side_len,
                        low_z=z_start,
                        high_z=z_start+z_change,
                        )
                )



            "yx"

            for rod, s in enumerate(basepoints):

                z_start = base_z+width_per_one+dead_space
                
                colour = self.c2 if rod%2==0 else self.c1
                colours.append(colour)

                #print(self.make_prism_triangles(
                #        low_x=base_x,
                #        high_x=base_x+square_side_len,
                #        low_y=s,
                #        high_y=s+dist_bpoints,
                #        low_z=z_start,
                #        high_z=z_start+z_change,
                #        ))

                vertices.extend(
                    self.make_prism_triangles(
                        low_x=base_x,
                        high_x=base_x+square_side_len,
                        low_y=s,
                        high_y=s+dist_bpoints,
                        low_z=z_start,
                        high_z=z_start+z_change,
                        )
                )





        space_below = in_between_space

        for double in range(num_doubles):
            z_change = width_per_one
            base_x, base_y, base_z = initial_x, initial_y, initial_z - space_below - double*(2*width_per_one+2*dead_space)

            num_rods = 2**(double+1)

            "yx"
            basepoints = np.linspace(base_y, base_y+square_side_len, num_rods, endpoint=False)
            dist_bpoints = basepoints[1]-basepoints[0]

            for rod, s in enumerate(basepoints):

                z_start = base_z
                
                colour = self.c2 if rod%2==0 else self.c1
                colours.append(colour)

                #print(self.make_prism_triangles(
                #        low_x=base_x,
                #        high_x=base_x+square_side_len,
                #        low_y=s,
                #        high_y=s+dist_bpoints,
                #        low_z=z_start,
                #        high_z=z_start-z_change,
                #        ))

                vertices.extend(
                    self.make_prism_triangles(
                        low_x=base_x,
                        high_x=base_x+square_side_len,
                        low_y=s,
                        high_y=s+dist_bpoints,
                        low_z=z_start,
                        high_z=z_start-z_change,
                        )
                )

            "xy"

            for rod, s in enumerate(basepoints):


                z_start = base_z-width_per_one-dead_space

                colour = self.c1 if rod%2==0 else self.c2
                colours.append(colour)

                #print(self.make_prism_triangles(
                #        low_x=s,
                #        high_x=s+dist_bpoints,
                #        low_y=base_y,
                #        high_y=base_y+square_side_len,
                #        low_z=z_start,
                #        high_z=z_start-z_change,
                #        ))

                vertices.extend(
                    self.make_prism_triangles(
                        low_x=s,
                        high_x=s+dist_bpoints,
                        low_y=base_y,
                        high_y=base_y+square_side_len,
                        low_z=z_start,
                        high_z=z_start-z_change,
                        )
                )
            #print()

        colours = np.array(colours)
        #print(colours.shape)
        m = np.stack((colours,)*36, axis=1)
        m = m.reshape(56*36,3)
        


        all_data = np.ones((len(vertices), 10), dtype=np.float32)
        all_data[:, :3] = vertices
        all_data[:, 3:6] = m
        all_data[:, 6] = alpha
        all_data[:, 7:] = vertices

        self.all_data = np.array(all_data).astype(np.float32)

    def make_vao(self):
        self.triangles_vao, self.triangles_vbo = create_vao(self.all_data, return_vbo=True, store_normals=True)

    def renew_vbo(self):
        update_vbo(self.triangles_vbo, self.reshaped)

    def draw_scintillator_structure(self):
        draw_vao(self.triangles_vao, GL_TRIANGLES, self.all_data.shape[0])

    
    def reset_scintillator_colour(self):
        
        self.reshaped = self.all_data.reshape(56,12,3,10)

        cd = {
            0  : [1.0,   0.75, 0.75, 0.8 ],
            1  : [0.75, 1.0,   0.75, 0.8 ],
            2  : [0.75, 1.0,   0.75, 0.8 ],
            3  : [1.0,   0.75, 0.75, 0.8 ],
            4  : [1.0,   0.75, 0.75, 0.8 ],
            5  : [0.75, 1.0,   0.75, 0.8 ],
            6  : [1.0,   0.75, 0.75, 0.8 ],
            7  : [0.75, 1.0,   0.75, 0.8 ],
            8  : [0.75, 1.0,   0.75, 0.8 ],
            9  : [1.0,   0.75, 0.75, 0.8 ],
            10 : [0.75, 1.0,   0.75, 0.8 ],
            11 : [1.0,   0.75, 0.75, 0.8 ],
            12 : [1.0,   0.75, 0.75, 0.8 ],
            13 : [0.75, 1.0,   0.75, 0.8 ],
            14 : [1.0,   0.75, 0.75, 0.8 ],
            15 : [0.75, 1.0,   0.75, 0.8 ],
            16 : [1.0,   0.75, 0.75, 0.8 ],
            17 : [0.75, 1.0,   0.75, 0.8 ],
            18 : [1.0,   0.75, 0.75, 0.8 ],
            19 : [0.75, 1.0,   0.75, 0.8 ],
            20 : [0.75, 1.0,   0.75, 0.8 ],
            21 : [1.0,   0.75, 0.75, 0.8 ],
            22 : [0.75, 1.0,   0.75, 0.8 ],
            23 : [1.0,   0.75, 0.75, 0.8 ],
            24 : [0.75, 1.0,   0.75, 0.8 ],
            25 : [1.0,   0.75, 0.75, 0.8 ],
            26 : [0.75, 1.0,   0.75, 0.8 ],
            27 : [1.0,   0.75, 0.75, 0.8 ],
            28 : [0.75, 1.0,   0.75, 0.8 ],
            29 : [1.0,   0.75, 0.75, 0.8 ],
            30 : [1.0,   0.75, 0.75, 0.8 ],
            31 : [0.75, 1.0,   0.75, 0.8 ],
            32 : [0.75, 1.0,   0.75, 0.8 ],
            33 : [1.0,   0.75, 0.75, 0.8 ],
            34 : [0.75, 1.0,   0.75, 0.8 ],
            35 : [1.0,   0.75, 0.75, 0.8 ],
            36 : [1.0,   0.75, 0.75, 0.8 ],
            37 : [0.75, 1.0,   0.75, 0.8 ],
            38 : [1.0,   0.75, 0.75, 0.8 ],
            39 : [0.75, 1.0,   0.75, 0.8 ],
            40 : [0.75, 1.0,   0.75, 0.8 ],
            41 : [1.0,   0.75, 0.75, 0.8 ],
            42 : [0.75, 1.0,   0.75, 0.8 ],
            43 : [1.0,   0.75, 0.75, 0.8 ],
            44 : [0.75, 1.0,   0.75, 0.8 ],
            45 : [1.0,   0.75, 0.75, 0.8 ],
            46 : [0.75, 1.0,   0.75, 0.8 ],
            47 : [1.0,   0.75, 0.75, 0.8 ],
            48 : [1.0,   0.75, 0.75, 0.8 ],
            49 : [0.75, 1.0,   0.75, 0.8 ],
            49 : [0.75, 1.0,   0.75, 0.8 ],
            50 : [1.0,   0.75, 0.75, 0.8 ],
            51 : [0.75, 1.0,   0.75, 0.8 ],
            52 : [1.0,   0.75, 0.75, 0.8 ],
            53 : [0.75, 1.0,   0.75, 0.8 ],
            54 : [1.0,   0.75, 0.75, 0.8 ],
            55 : [0.75, 1.0,   0.75, 0.8 ],
        }

        for i, r in enumerate(self.reshaped):

            arr = cd[i]
            m = np.stack((arr,)*36, axis=0)
            k = m.reshape(12,3,4)
            self.reshaped[i, :, :, 3:7] = k

            #if i%2==0:
            #    arr = np.array([*self.c1, 0.8])
            #    m = np.stack((arr,)*36, axis=0)
            #    k = m.reshape(12,3,4)
            #    self.reshaped[i, :, :, 3:7] = k
            #
            #elif i%2==1:
            #    arr = np.array([*self.c1, 0.8])
            #    m = np.stack((arr,)*36, axis=0)
            #    k = m.reshape(12,3,4)
            #    self.reshaped[i, :, :, 3:7] = k

            #print(f'{i:2}', r[0, 0, 3:7])

        #print()
        self.reshaped.reshape(56*12*3, 10)

    
    def recolour_for_point(self, point):
        binary=self.data_manager.num_to_raw_binary(point.int_number)
        scintillators = point.scintillator_binary
        #print(type(scintillators))
        #print(type(scintillators[0]))
        #print(type(scintillators[1]))
        #print()

        # shape [ [(),*8], [(),*8] ]
        #print(scintillators)
        #print(0, scintillators[0])
        x = scintillators[0][:6] # for some reason
        y = scintillators[1]

        #print(0, x)
        #print(1, y)


        #print(len(x), len(y))
        #print("b", x)
        #print("c", y)
        #print()

        x.extend(y)
        xy=x
        #print(len(xy), xy)
        # 1,3,5,8,12,10,6,2,4,7,11,9


        #order_added = [6,5,4,3,2,1,8,7,10,9,12,11]
        order_added = [6,5,4,3,2,1,7,8,9,10,11,12]
        reversed_items = [5, 8, 10, 4, 7]



        nk = {
            6:[0,1],
            5:[2,3],
            4:[4,5,6,7],
            3:[8,9,10,11],
            2:[12,13,14,15,16,17,18,19],
            1:[20,21,22,23,24,25,26,27],
            7:[28,29],
            8:[30,31],
            9:[32,33,34,35],
            10:[36,37,38,39],
            11:[40,41,42,43,44,45,46,47],
            12:[48,49,50,51,52,53,54,55],
        }

#1,3,5,8,12,10,6,2,4,7,11,9


        di = {
             0 : (1,  ("g", "r"), "yx"), # original
             1 : (3,  ("g", "r"), "yx"), # original
             2 : (5,  ("r", "g"), "yx"), # original
             3 : (8,  ("r", "g"), "xy"), # original
             4 : (12, ("g", "r"), "xy"), # original
             5 : (10, ("g", "r"), "xy"), # original
            # 5 : (10, ("g", "r"), "yx"),
             6 : (6,  ("g", "r"), "xy"), # original
             7 : (2,  ("r", "g"), "xy"), # original
             8 : (4,  ("g", "r"), "xy"), # original
             9 : (7,  ("r", "g"), "yx"), # original
            10 : (11, ("r", "g"), "yx"), # original
            11 : (9,  ("g", "r"), "yx"), # original
            #10 : (11, ("r", "g"), "xy"),
            #11 : (9,  ("g", "r"), "xy"),
        }


        #d = {
        #     0 : (6,  ("g", "r")), # x
        #     1 : (5,  ("r", "g")), # y
        #     2 : (4,  ("g", "r")), # x
        #     3 : (3,  ("g", "r")), # y
        #     4 : (2,  ("r", "g")), # x
        #     5 : (1,  ("g", "r")), # y
        #     6 : (8,  ("r", "g")), # y
        #     7 : (7,  ("r", "g")), # x
        #     8 : (10, ("g", "r")), # y
        #     9 : (9,  ("g", "r")), # x
        #    10 : (12, ("g", "r")), # y
        #    11 : (11, ("r", "g")), # x
        #}
        
        #d = {
        #     0 : (6,  ("g", "r")), # x
        #     1 : (4,  ("g", "r")), # x
        #     2 : (2,  ("r", "g")), # x
        #     3 : (7,  ("r", "g")), # x
        #     4 : (11, ("g", "r")), # x
        #     5 : (9,  ("g", "r")), # x
        #     6 : (1,  ("g", "r")), # y
        #     7 : (5,  ("r", "g")), # y
        #     8 : (3,  ("g", "r")), # y
        #     9 : (8,  ("r", "g")), # y
        #    10 : (12, ("r", "g")), # y
        #    11 : (10, ("g", "r")), # y
        #}

        #d = {
        #     0 : (6,  ("g", "r")), # x
        #     1 : (4,  ("g", "r")), # x
        #     2 : (2,  ("r", "g")), # x
        #     3 : (7,  ("r", "g")), # x
        #     4 : (11, ("r", "g")), # x
        #     5 : (9,  ("g", "r")), # x
        #     6 : (1,  ("g", "r")), # y
        #     7 : (5,  ("r", "g")), # y
        #     8 : (3,  ("g", "r")), # y
        #     9 : (8,  ("r", "g")), # y
        #    10 : (12, ("g", "r")), # y
        #    11 : (10, ("g", "r")), # y
        #}

        #print("a", [i for i, (a, b) in enumerate(xy)])

        num_to_colour = 0
        yellow = np.array([1,1,0,0.75,])

        if True:
            for i, (a, b) in enumerate(xy):
                #print(i, (a,b), len(xy))
                #print(xy)
                #print()

                r, (ra, rb), rxy = di[i]

                nk_s = nk[r]

                #rj, (ra, rb) = d[r-1]

                #j = rj
                #if j > 6:
                #    j-=6
                #else:
                #    j = 7-j
#
                #j_num = 2**((j-1)//2+1)
                ##print(rj, j, j_num)
#
                #n = num_to_colour
                #nn = n+j_num

                for mn in nk_s:
                    #print(i, r, (ra, rb), mn, (a, b), nk_s)
                    if a == 1:
                        if ra == "r":
                            if rxy == "xy":
                                if mn%2==0:
                                    self.reshaped[mn, :, :, 3:7]  = yellow
                            elif rxy == "yx":
                                if mn%2==1:
                                    self.reshaped[mn, :, :, 3:7]  = yellow

                        elif ra == "g":
                            if rxy == "xy":
                                if mn%2==0:
                                    self.reshaped[mn, :, :, 3:7]  = yellow
                            elif rxy == "yx":
                                if mn%2==1:
                                    self.reshaped[mn, :, :, 3:7]  = yellow


                    elif b == 1:
                        if ra == "r":
                            if rxy == "xy":
                                if mn%2==1:
                                    self.reshaped[mn, :, :, 3:7]  = yellow
                            elif rxy == "yx":
                                if mn%2==0:
                                    self.reshaped[mn, :, :, 3:7]  = yellow

                        elif ra == "g":
                            if rxy == "xy":
                                if mn%2==1:
                                    self.reshaped[mn, :, :, 3:7]  = yellow
                            elif rxy == "yx":
                                if mn%2==0:
                                    self.reshaped[mn, :, :, 3:7]  = yellow

            #print()
                
                #for k in range(j_num):
#
                #    print(i, ind, rj, j, j_num, k, a, ra, k%2, num_to_colour)
                #    if a == 1:
                #        if ra == "r":
                #            if False:
                #            #if k%2==0:
                #            #if rj%2==0:
                #            #if True:
                #                self.reshaped[num_to_colour+0, :, :, 3:7]  = yellow
                #        elif ra == "g":
                #            if k%2==0:
                #            #if False:
                #                self.reshaped[num_to_colour+0, :, :, 3:7]  = yellow
#
#
                #    elif b == 1:
                #        if k%2==3:
                #            self.reshaped[num_to_colour+0, :, :, 3:7]  = yellow
                #    
                #    
                #    num_to_colour += 1
#
#
                #    #print()
                #
                ##print(rj, num_to_colour)


        #print()



                #if rj in [1,2,11,12]:
                #    # 4R, 4G
                #    if a == 1:
                #        #if ra == "r":
                #        self.reshaped[num_to_colour+0, :, :, 3:7]  = yellow
                #        #self.reshaped[num_to_colour+2, :, :, 3:7]  = yellow
                #        #self.reshaped[num_to_colour+4, :, :, 3:7]  = yellow
                #        #self.reshaped[num_to_colour+6, :, :, 3:7]  = yellow
                #        num_to_colour += 8
                #        #elif ra == "g":
                #        #    self.reshaped[num_to_colour+1, :, :, 3:7]  = yellow
                #        #    self.reshaped[num_to_colour+3, :, :, 3:7]  = yellow
                #        #    self.reshaped[num_to_colour+5, :, :, 3:7]  = yellow
                #        #    self.reshaped[num_to_colour+7, :, :, 3:7]  = yellow
                #        #    num_to_colour += 8
                #    #elif b == 1:
                #    #    if ra == "r":
                #    #        self.reshaped[num_to_colour+0, :, :, 3:7]  = yellow
                #    #        self.reshaped[num_to_colour+2, :, :, 3:7]  = yellow
                #    #        self.reshaped[num_to_colour+4, :, :, 3:7]  = yellow
                #    #        self.reshaped[num_to_colour+6, :, :, 3:7]  = yellow
                #    #        num_to_colour += 8
                #    #    elif ra == "g":
                #    #        self.reshaped[num_to_colour+1, :, :, 3:7]  = yellow
                #    #        self.reshaped[num_to_colour+3, :, :, 3:7]  = yellow
                #    #        self.reshaped[num_to_colour+5, :, :, 3:7]  = yellow
                #    #        self.reshaped[num_to_colour+7, :, :, 3:7]  = yellow
                #    #        num_to_colour += 8
                #
                #elif rj in [3,4,9,10]:
                #    # 2R, 2G
                #    if a == 1:
                #        self.reshaped[num_to_colour+0, :, :, 3:7]  = yellow
                #        self.reshaped[num_to_colour+2, :, :, 3:7]  = yellow
                #        num_to_colour += 4
                #    elif b == 1:
                #        self.reshaped[num_to_colour+1, :, :, 3:7]  = yellow
                #        self.reshaped[num_to_colour+3, :, :, 3:7]  = yellow
                #        num_to_colour += 4
                #
                #elif rj in [5,6,7,8]:
                #    # 1R, 1G
                #    if a == 1:
                #        self.reshaped[num_to_colour+0, :, :, 3:7]  = yellow
                #        num_to_colour += 2
                #    elif b == 1:
                #        self.reshaped[num_to_colour+1, :, :, 3:7]  = yellow
                #        num_to_colour += 2

            #print(num_to_colour, len(self.reshaped))
                #print(i, rj, j)


        #for i, b in enumerate(binary):
        #    for j in d[i]:
        #        if b == 1:
        #            yellow = np.array([1,1,0,0.75,])
#
        #            self.reshaped[j, :4, :, 3:7]  = yellow
        #            self.reshaped[j, 4:8, :, 3:7]  = yellow
        #            self.reshaped[j, 8:12, :, 3:7] = yellow



        # top to bottom is 1 to 12
        # NOTE : correct to current yellow findings in data_manager
        d = {
            2:  [21, 23, 25, 27], # 1 green
            3:  [20, 22, 24, 26], # 1 red

            4:  [13, 15, 17, 19], # 2 green
            5:  [12, 14, 16, 18], # 2 red

            6:  [9, 11], # 3 green
            7:  [8, 10], # 3 red

            9:  [5, 7], # 4 green # swapped
            8:  [4, 6], # 4 red # swapped

            11: [3], # 5 green # swapped
            10: [2], # 5 red # swapped
            
            1:  [1], # 6 green
            0:  [0], # 6 red


            12: [28], # 7 red
            13: [29], # 7 green

            15: [30], # 8 red
            14: [31], # 8 green

            17: [32, 34], # 9 red # swapped
            16: [33, 35], # 9 green # swapped

            18: [36, 38], # 10 red # swapped
            19: [37, 39], # 10 green # swapped

            20: [40, 42, 44, 46], # 11 red # swapped
            21: [41, 43, 45, 47], # 11 green # swapped

            22: [48, 50, 52, 54], # 12 red # swapped
            23: [49, 51, 53, 55], # 12 green # swapped
        }


        if False:
            for i, b in enumerate(binary):
                for j in d[i]:
                    if b == 1:
                        yellow = np.array([1,1,0,0.75,])
                        self.reshaped[j, :, :, 3:7]  = yellow


        else:
            pass

        self.reshaped.reshape(56*12*3,10)