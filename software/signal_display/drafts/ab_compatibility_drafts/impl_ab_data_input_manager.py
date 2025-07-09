import os
import struct

from datetime import datetime

import serial
import numpy as np

from OpenGL.GL import *

from software.signal_display.scintillator_display.math.convex_hull import ConvexHullDetection as Detection

from software.signal_display.scintillator_display.universal_values import MathDisplayValues

from software.signal_display.scintillator_display.display.vao_vbo import create_vao, update_vbo, draw_vao

class Data(MathDisplayValues):
    def __init__(self, impl_constant, impl, hull_colour, hull_opacity, store_normals, debug=True):
        self.debug = debug
        self.impl = impl # "a" or "b"
        self.hull_colour = hull_colour
        self.hull_opacity = hull_opacity
        self.store_normals = store_normals
        self.data = []
        self.impl_a_data_is_checked = []
        self.impl_b_data_is_checked = []
        self.detection_algorithm = Detection(impl_constant=impl_constant)



        if self.debug:
            self.testing()
            pass
        else:
            if os.name == "nt":
                dsrdtr = True
                port = "COM5"
            else:
                dsrdtr = False
                port = "/dev/ttyUSB0"

            self.arduino = serial.Serial(port=port, baudrate=115200, dsrdtr=dsrdtr)


    def arduino_has_data(self):
        if self.debug:
            return False
        return self.arduino.in_waiting >= 8
    
    def get_data_from_arduino(self):
        """
        Gather the data from Arduino
        """
        self.arduino.read_until(b"\x7E")
        value = self.arduino.read(4)
        if self.arduino.read(1) != b"\x7D":
            print("serial frame end error")

        (n,) = struct.unpack("<I", value)

        return n
    
    
    def format_print(self, value):
        lsb = value & 0xFFFFFF
        b1 = (lsb >> 16) & 0xFF
        b2 = (lsb >> 8) & 0xFF
        b3 = lsb & 0xFF

        print("receive trigger: SiPM status")
        print(f"    {b1:02x}          {b2:02x}          {b3:02x}")
        print(f"    {b1:08b}    {b2:08b}    {b3:08b}")
        print()

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

        k = self.num_to_raw_binary(raw_data)[f_sc_idx]

        cooked_data = [[(int(k[0]), int(k[1])) for k in k[0]], [(int(k[0]), int(k[1])) for k in k[1]]]

        return cooked_data
    
    def is_valid_data(self, data=None):
        self.raw_data = self.get_data_from_arduino() if data==None else data
        self.cooked_data = self.cook_data_into_scintillators(self.raw_data)
        self.scintillator_bounds = self.detection_algorithm.scintillators_to_bounds(self.cooked_data)

        if self.impl == "a":
            if not self.scintillator_bounds:
                return
            elif self.scintillator_bounds == None:
                return
        elif self.impl == "b":
            if self.scintillator_bounds == None:
                return False
            return True


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
        
    
    def transform_data_per_impl(self):
        hull_bounds = self.scintillator_bounds

        time = datetime.now()

        if self.impl == "a":
            new_hull_bounds = self.transform_coordinates_impl_a(hull_bounds)
        elif self.impl == "b":
            new_hull_bounds = np.array(hull_bounds) - np.array([0, 0, self.SPACE_BETWEEN_STRUCTURES/2])



        bit24 = self.raw_data & 0xffffff
                
        point = [new_hull_bounds, self.cooked_data, bit24, time]

        self.data.append(point)
        self.impl_a_data_is_checked.append(False)
        self.impl_b_data_is_checked.append(False)

        
            
        if self.impl == "b":
            return np.array(new_hull_bounds).astype(np.float32)


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
    

    def make_points_from_high_low(self, xl, xh, yl, yh, zl, zh, colour=[], opacity=[]):
        points = np.array([
            np.array([xl, yl, zl, *colour, *opacity]), # base_point + (0,    0,    0)    # BFL
            np.array([xh, yl, zl, *colour, *opacity]), # base_point + (xlen, 0,    0)    # BFR
            np.array([xl, yh, zl, *colour, *opacity]), # base_point + (0,    ylen, 0)    # BBL
            np.array([xh, yh, zl, *colour, *opacity]), # base_point + (xlen, ylen, 0)    # BBR
            np.array([xl, yl, zh, *colour, *opacity]), # base_point + (0,    0,    zlen) # TFL
            np.array([xh, yl, zh, *colour, *opacity]), # base_point + (xlen, 0,    zlen) # TFR
            np.array([xl, yh, zh, *colour, *opacity]), # base_point + (0,    ylen, zlen) # TBL
            np.array([xh, yh, zh, *colour, *opacity]), # base_point + (xlen, ylen, zlen) # TBR
        ])
        return points
    

    def make_prism_triangles(self, p1, p2, p3, p4, p5, p6, p7, p8, show_top_bottom=False):

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

        return all_t    

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
        vd[:, :3]   = vertices
        vd[:, 3:6]  = hull_colour
        vd[:, 6]    = hull_opacity
        vd[:, 7:10] = vertices

        #if self.impl == "a":
        #    vd = np.ones((len(vertices), 10), dtype=np.float32)
        #    vd[:, :3]   = vertices
        #    vd[:, 3:6]  = hull_colour
        #    vd[:, 6]    = hull_opacity
        #    vd[:, 7:10] = vertices
        #elif self.impl == "b":
        #    vd = np.ones((len(vertices), 7), dtype=np.float32)
        #    vd[:, :3]   = vertices
        #    vd[:, 3:6]  = hull_colour
        #    vd[:, 6]    = hull_opacity

        return vd
    

    def create_hull_data_and_vao(self, hull_bounds):
        hull_data = self.hull_setup_for_data_point(
            hull_bounds, self.hull_colour, self.hull_opacity)
        hull_vao = create_vao(hull_data, store_normals=self.store_normals)
        n = hull_data.shape[0]
        return hull_vao, n
    
    def draw_active_hulls(self, data_points, data_active):
        if data_points == []:
            return
        else:
            for i, j in enumerate(data_active):
                if j == True:
                    hull_bounds = data_points[i][0]
                    vao, n = self.create_hull_data_and_vao(hull_bounds)
                    draw_vao(vao, GL_TRIANGLES, n)
    
    def testing(self):
        test_data = [
                0b011011010110101011010110,
                0b100110101101010101101001,
                0b100101101010011101011001,
                1431655765,
                #2**33 - 1
            ]
        for data in test_data:
            self.is_valid_data(data)
            self.transform_data_per_impl()
