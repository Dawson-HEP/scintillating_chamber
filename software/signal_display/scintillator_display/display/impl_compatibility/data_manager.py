from datetime import datetime

import numpy as np
import pandas as pd

from OpenGL.GL import *

from scintillator_display.math.convex_hull import ConvexHullDetection as Detection

from scintillator_display.compat.universal_values import MathDisplayValues

from scintillator_display.display.impl_compatibility.vao_vbo import create_vao, update_vbo, draw_vao

from scintillator_display.display.impl_compatibility.camera_shader_controls import CameraShaderControls

import os

import time


class DataPoint:
    def __init__(self, hull_bounds, cooked_data, bit24, time, mode, vao, draw_type, n):
        self.hull_bounds = hull_bounds
        self.scintillator_binary = cooked_data
        self.int_number = bit24
        self.trigger_time = time
        self.display_mode = mode
        self.hull_vao = vao
        self.draw_type = draw_type
        self.n_shapes = n



class Data(MathDisplayValues):
    def __init__(self, impl_constant, impl, hull_colour, hull_opacity, store_normals, mode):
        
        self.matrices = CameraShaderControls()


        self.mode = mode

        self.impl = impl # "a" or "b"
        self.hull_colour = hull_colour
        self.hull_opacity = hull_opacity
        self.store_normals = store_normals
        self.reset_data_checks()
        self.detection_algorithm = Detection(impl_constant=impl_constant)

        self.test_data_created = False


        

        highest_vao = 0b101001100101010110101010
        f_sc_idx = [
        [(20,21),(16,17),(13,12),(9,8),(0,1),(5,4),],
        [(22,23),(18,19),(15,14),(11,10),(2,3),(6,7),],
        ]

        reversed_items = [5, 8, 10, 4, 7]
        

        self.test_data = [
                0b011011010110101011010110,
                0b100110101101010101101001,
                0b100101101010011101011001,
                1431655765,
                #2**33 - 1,
                0b101010101010101010101010,
                highest_vao, # = 0b101001 100101 010110 101010

                0b100110101010011001011001,
                0b011001011001101010100110,
                0b011001011010100101100101,
                0b100110100101011010011010,
            ]
        
        yellow_colour_terms =  {
            '''
             01 : 12 green red # x
             23 : 11 red green # y
             45 : 10 green red # x
              67 : 9 green red # y
              89 : 8 red green # x
            1011 : 7 red green # y
            1213 : 5 red green # y
            1415 : 4 green red # x
            1617 : 3 green red # y
            1819 : 2 red green # x
            2021 : 1 green red # y
            2223 : 6 green red # x
            '''
        }

        this_file_path = os.path.abspath(__file__)
        lst_f_path = this_file_path.split(os.sep)

        display_dir = lst_f_path[:-3]
        display_dir.append('data')

        def demo_1():
            display_dir.append('input_2025_04_09_triggers.txt')
            data_path = os.sep.join(display_dir)


            with open(data_path) as f:
                data_lines = f.readlines()

                # for old data txt
                number_data = ["".join([i for i in line if i.isnumeric()]) for line in data_lines]
                #number_data = ["".join([i for i in line if i.isnumeric()]) for line in data_lines]
                scintillator_data = [int(num, 2) for num in number_data if len(num)==24]

            return scintillator_data

        def demo_2():

            display_dir.append('sc_data.log.2025-04-22')
            data_path = os.sep.join(display_dir)

            with open(data_path) as f:
                data_lines = f.readlines()

                # for log files
                scintillator_data = [int(line.split(",")[1]) for line in data_lines if "," in line]

            return scintillator_data


        
        self.demo_data, self.demo_is_checked = self.create_points_on_initialisation(demo_1())
        self.demo_index = 4
        self.most_recent_demo_update = time.time()
        self.demo_wait_time = 2


        self.debug_data, self.debug_is_checked = self.create_points_on_initialisation(self.test_data)

        self.collected_data = []
        self.collected_is_checked = []

        highest_vao = 0

        for i in self.debug_data:
            if i.hull_vao > highest_vao:
                highest_vao = i.hull_vao
        for j in self.demo_data:
            if j.hull_vao > highest_vao:
                highest_vao = j.hull_vao

        #print(highest_vao)



    
    def create_points_on_initialisation(self, ints):
        if type(ints) == list:
            for num in ints:
                self.add_point(num)
        elif type(ints) == int:
            self.add_point(num)
        else:
            raise TypeError(f'{ints} in type {type(ints)} is not a supported type yet')
        
        data_list = self.data
        checked_list = self.impl_data_is_checked
        self.reset_data_checks()

        return data_list, checked_list



    def reset_data_checks(self):
        self.data = []
        self.impl_data_is_checked = []



    def update_data(self, arduino):

        if self.mode == 'data':
            if arduino.arduino_has_data():
                data = arduino.get_data_from_arduino()
                for data_point in data:
                    self.add_point(data_point)
                self.collected_data.extend(self.data)
                self.collected_is_checked.extend(self.impl_data_is_checked)
            self.data = self.collected_data
            self.impl_data_is_checked = self.collected_data

        elif self.mode == 'debug':

            self.data = self.debug_data
            if any(self.impl_data_is_checked):
                pass # center + 4 on each side
            else:
                self.impl_data_is_checked = self.debug_is_checked

            #print("k", len(self.data), len(self.impl_data_is_checked))

        elif self.mode == 'demo':

            if time.time()-self.most_recent_demo_update>self.demo_wait_time:
                self.demo_index+=1
                self.most_recent_demo_update=time.time()


            def get_i_range(item):
                # gets indices of list for modulo-ed demo index, plus 4 on either side
                return [(self.demo_index+j)%len(item) for j in range(-4, 5)]


            self.data = [self.demo_data[i] for i in get_i_range(self.demo_data)]

            if any(self.impl_data_is_checked):
                pass # center + 4 on each side
            else:
                self.impl_data_is_checked = [self.demo_is_checked[i] for i in get_i_range(self.demo_is_checked)]

            #print("start?", self.impl, len(self.data), len(self.impl_data_is_checked),
            #      len(get_i_range(self.demo_2025_04_09_data)), len(range(-4, 5)))



        else:
            raise Exception('invadid mode')


    def num_to_raw_binary(self, num):
        return np.array([(num & (2**i)) >> i for i in range(24)])
    
    
    def cook_data_into_scintillators(self, raw_data):
        """
        transform data ready to be interpreted by the display, then update self.data
        """
        
        f_sc_idx = [
        [(21,20),(16,17),(13,12),(8,9),(0,1),(5,4),],
        [(22,23),(18,19),(15,14),(11,10),(2,3),(6,7),],
        ]

        #f_sc_idx = [
        #[(20,21),(16,17),(13,12),(9,8),(0,1),(5,4),],
        #[(22,23),(18,19),(15,14),(11,10),(2,3),(6,7),],
        #]

        k = self.num_to_raw_binary(raw_data)[f_sc_idx]

        cooked_data = [[(int(k[0]), int(k[1])) for k in k[0]], [(int(k[0]), int(k[1])) for k in k[1]]]

        return cooked_data
    
    def get_scintillator_bounds(self, data):
        raw_data = data
        cooked_data = self.cook_data_into_scintillators(raw_data)
        scintillator_bounds = self.detection_algorithm.scintillators_to_bounds(cooked_data)

        if not scintillator_bounds:
            return None, None
        return scintillator_bounds, cooked_data
    

    def add_point(self, data):
        scintillator_bounds, cooked_data = self.get_scintillator_bounds(data)
        if scintillator_bounds != None:
            self.transform_data_per_impl(scintillator_bounds, cooked_data, data)

    def transform_data_per_impl(self, bounds, cooked_data, raw_data):
        hull_bounds = bounds

        time = datetime.now()

        if self.impl == "a":
            new_hull_bounds = self.transform_coordinates_impl_a(hull_bounds)
        elif self.impl == "b":
            #rotate = self.matrices.rotate_around_p(p=(
            #    self.SQUARE_LEN/2, -self.SPACE_BETWEEN_STRUCTURES/2, self.SQUARE_LEN/2
            #), r=(0,0,90))
            # #rotate = self.matrices.rotate(r=(0,0,90))
            new_hull_bounds = np.array(hull_bounds) - np.array([0, 0, self.SPACE_BETWEEN_STRUCTURES/2])
            #print(new_hull_bounds.shape)
            #n = np.ones((len(new_hull_bounds), 4))
            #n[:, :3] = new_hull_bounds
            #n[:, 3] = 1
            ##print(n)
            #new_hull_bounds = n @ rotate
            #new_hull_bounds = new_hull_bounds[:, :3]
            ##x = 120 - np.abs(new_hull_bounds[:, 0])
            ##x = 120 - (new_hull_bounds[:, 0])
            #x = new_hull_bounds[:, 0]
            #y = new_hull_bounds[:, 1]
            ##z = new_hull_bounds[:, 2]
            ##y = np.abs(new_hull_bounds[:, 1])
            #x = new_hull_bounds[:, 0] + self.SQUARE_LEN
            #y = new_hull_bounds[:, 1] + self.SQUARE_LEN
            ##z = new_hull_bounds[:, 2]

            #z = new_hull_bounds[:, 2] + self.SPACE_BETWEEN_STRUCTURES/2
            #z = -1*z
            #z = z - self.SPACE_BETWEEN_STRUCTURES/2

            #new_hull_bounds = np.array([x,y,z]).T




        bit24 = raw_data & 0xffffff
                
        vao, n = self.create_hull_data_and_vao(new_hull_bounds)

        self.data.append(DataPoint(new_hull_bounds,
                                   cooked_data,
                                   bit24,
                                   time,
                                   self.mode,
                                   vao,
                                   GL_TRIANGLES,
                                   n))
        self.impl_data_is_checked.append(False)

    def transform_coordinates_impl_a(self,data):
        """
        transform into my coordinate system
        """
        translate_x = -self.detection_algorithm.n / 2
        translate_y = -self.detection_algorithm.n / 2
        z_scale = 1

        lst = []
        for i, coordinates in enumerate(data):
            x = (coordinates[0] + translate_x) * -1
            y = (coordinates[1] + translate_y) *  1
            z = (coordinates[2] + self.detection_algorithm.half_gap_size - self.detection_algorithm.inter_level_gap + self.detection_algorithm.plate_thickness) / z_scale
            lst.append((x,y,z))

        return lst

    def scale_hull_bounds(self, hull_bounds):
        '''
        hull_bounds = [1, 2, 3, 4, 5, 6, 7, 8]
        '''

        idx = [[0, 7],[1, 6],[2, 5],[3, 4]]
        fan = np.array(hull_bounds)[idx]
        scale_factor = 75 if self.impl == "a" else 700 if self.impl == "b" else 0
        fan_vec = np.array([scale_factor*(p[0]-p[1])/np.linalg.norm(p[0]-p[1]) for p in fan])
        
        scaled_p0 =  fan_vec[0]+hull_bounds[0]
        scaled_p1 =  fan_vec[1]+hull_bounds[1]
        scaled_p2 =  fan_vec[2]+hull_bounds[2]
        scaled_p3 =  fan_vec[3]+hull_bounds[3]
        scaled_p4 = -fan_vec[3]+hull_bounds[4]
        scaled_p5 = -fan_vec[2]+hull_bounds[5]
        scaled_p6 = -fan_vec[1]+hull_bounds[6]
        scaled_p7 = -fan_vec[0]+hull_bounds[7]


        scaled_hull_bounds = [scaled_p0, scaled_p1,
                              scaled_p2, scaled_p3,
                              scaled_p4, scaled_p5,
                              scaled_p6, scaled_p7]

        return scaled_hull_bounds
    

    def make_points_from_high_low(self, xl, xh, yl, yh, zl, zh):
        points = np.array([
            np.array([xl, yl, zl]), # base_point + (0,    0,    0)    # BFL
            np.array([xh, yl, zl]), # base_point + (xlen, 0,    0)    # BFR
            np.array([xl, yh, zl]), # base_point + (0,    ylen, 0)    # BBL
            np.array([xh, yh, zl]), # base_point + (xlen, ylen, 0)    # BBR
            np.array([xl, yl, zh]), # base_point + (0,    0,    zlen) # TFL
            np.array([xh, yl, zh]), # base_point + (xlen, 0,    zlen) # TFR
            np.array([xl, yh, zh]), # base_point + (0,    ylen, zlen) # TBL
            np.array([xh, yh, zh]), # base_point + (xlen, ylen, zlen) # TBR
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

    def hull_setup_for_data_point(self, hull_bounds, hull_colour, hull_opacity, show_top_bottom=False):
        vertices = []

        scaled_hull_bounds = self.scale_hull_bounds(hull_bounds)
        
        centre_prism = self.make_prism_triangles(*hull_bounds, show_top_bottom)
        vertices.extend(centre_prism)

        top_triangle_fans = self.make_prism_triangles(*hull_bounds[:4], *scaled_hull_bounds[:4], show_top_bottom)
        vertices.extend(top_triangle_fans)

        bottom_triangle_fans = self.make_prism_triangles(*hull_bounds[4:], *scaled_hull_bounds[4:], show_top_bottom)
        vertices.extend(bottom_triangle_fans)

        vertices = np.array(vertices, dtype = np.float32)

        vd = np.ones((len(vertices), 10), dtype=np.float32)
        vd[:, :3]   = vertices     # vertices
        vd[:, 3:6]  = hull_colour  # colour
        vd[:, 6]    = hull_opacity # opacity
        vd[:, 7:10] = vertices     # normals (bad approximation)

        return vd
    

    def create_hull_data_and_vao(self, hull_bounds):
        hull_data = self.hull_setup_for_data_point(
            hull_bounds, self.hull_colour, self.hull_opacity)
        hull_vao = create_vao(hull_data, store_normals=self.store_normals)
        n = hull_data.shape[0]
        return hull_vao, n
    
    def draw_active_hulls(self, data_points, data_active) -> DataPoint:
        if data_points == []:
            return
        else:
            for i, j in enumerate(data_active):
                if j == True:
                    point : DataPoint = data_points[i]
                    draw_vao(point.hull_vao, point.draw_type, point.n_shapes)

    
    def generate_data_csv(self):
        """
        Create csv file
        """
        
        df = pd.DataFrame(self.data,columns=["new_hull_bounds", "cooked_data", "bit24", "time", "debug_data"])

        df = df.drop("new_hull_bounds", axis=1)
        df = df.drop("cooked_data", axis=1)

        time = datetime.now()
        time = ("").join([t if t != ":" else "." for t in str(time) ])

        try:
            df.to_csv(f"scintillator_display/data/{time}.csv")   #Current directory is set to the "data" folder
        except:
            df.to_csv(f"{time}.csv")