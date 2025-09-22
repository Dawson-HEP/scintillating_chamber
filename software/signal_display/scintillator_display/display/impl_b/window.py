import time


import software.signal_display.scintillator_display.compat.glfw as glfw


from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

from software.signal_display.scintillator_display.display.impl_compatibility.camera_controls import CameraControls
from software.signal_display.scintillator_display.display.impl_compatibility.shader_manager import ShaderManager


from software.signal_display.scintillator_display.display.impl_b.scintillator_blocks import ScintillatorStructure
from software.signal_display.scintillator_display.display.impl_compatibility.scintillator_blocks_build import ScintillatorBlocks

from software.signal_display.scintillator_display.display.impl_compatibility.vao_vbo import create_vao, update_vbo, draw_vao

from software.signal_display.scintillator_display.display.impl_compatibility.xyz_axes import Axes

from software.signal_display.scintillator_display.display.impl_compatibility.data_manager import Data

from software.signal_display.scintillator_display.compat.pyserial_singleton import ArduinoData

from software.signal_display.scintillator_display.compat.universal_values import MathDisplayValues


class Window(MathDisplayValues):
    def __init__(self, init_mode=('data', 'debug', 'demo'), x_ratio=(3, 5, 5), y_ratio=(0, 1, 1)):

        self.x_ratio, self.y_ratio = x_ratio, y_ratio

        if init_mode not in ('data', 'debug', 'demo'):
            init_mode='debug'

        self.zeroes_offset = np.array([
            self.SQUARE_LEN/2, self.SQUARE_LEN/2, -self.SPACE_BETWEEN_STRUCTURES/2
            ])

        self.camera = CameraControls(zoom=90, offset=self.zeroes_offset)
        self.shaders = ShaderManager(self.camera,
                                     shader_names=[
                                         ("vertex_shader.glsl", "fragment_shader.glsl"),
                                         ("texture_vertex_shader.glsl", "texture_fragment_shader.glsl")
                                     ])
        
        self.arduino = ArduinoData()
        self.data_manager = Data(impl_constant=1, impl="b",
                            hull_colour=[0.5, 0, 0.5], hull_opacity=0.8,
                            store_normals=True,
                            mode=init_mode)
        #self.scintillator_structure = ScintillatorStructure(self.data_manager)
        self.scintillator_structure = ScintillatorBlocks(self.data_manager)
        self.xyz_axes = Axes(l=250)


        self.shaders.setup_opengl()
        self.normal_shader, self.texture_shader = self.shaders.shader_programs


        self.pt_selected = None
        self.show_axes = True


        lsb_one          = self.data_manager.num_to_raw_binary_lsb(0b000000000000000000000001)
        lsb_two          = self.data_manager.num_to_raw_binary_lsb(0b000000000000000000000010)
        lsb_three        = self.data_manager.num_to_raw_binary_lsb(0b000000000000000000000100)
        lsb_four         = self.data_manager.num_to_raw_binary_lsb(0b000000000000000000001000)
        lsb_five         = self.data_manager.num_to_raw_binary_lsb(0b000000000000000000010000)
        lsb_six          = self.data_manager.num_to_raw_binary_lsb(0b000000000000000000100000)
        lsb_seven        = self.data_manager.num_to_raw_binary_lsb(0b000000000000000001000000)
        lsb_eight        = self.data_manager.num_to_raw_binary_lsb(0b000000000000000010000000)
        lsb_nine         = self.data_manager.num_to_raw_binary_lsb(0b000000000000000100000000)
        lsb_ten          = self.data_manager.num_to_raw_binary_lsb(0b000000000000001000000000)
        lsb_eleven       = self.data_manager.num_to_raw_binary_lsb(0b000000000000010000000000)
        lsb_twelve       = self.data_manager.num_to_raw_binary_lsb(0b000000000000100000000000)
        lsb_thirteen     = self.data_manager.num_to_raw_binary_lsb(0b000000000001000000000000)
        lsb_fourteen     = self.data_manager.num_to_raw_binary_lsb(0b000000000010000000000000)
        lsb_fifteen      = self.data_manager.num_to_raw_binary_lsb(0b000000000100000000000000)
        lsb_sixteen      = self.data_manager.num_to_raw_binary_lsb(0b000000001000000000000000)
        lsb_seventeen    = self.data_manager.num_to_raw_binary_lsb(0b000000010000000000000000)
        lsb_eighteen     = self.data_manager.num_to_raw_binary_lsb(0b000000100000000000000000)
        lsb_nineteen     = self.data_manager.num_to_raw_binary_lsb(0b000001000000000000000000)
        lsb_twenty       = self.data_manager.num_to_raw_binary_lsb(0b000010000000000000000000)
        lsb_twenty_one   = self.data_manager.num_to_raw_binary_lsb(0b000100000000000000000000)
        lsb_twenty_two   = self.data_manager.num_to_raw_binary_lsb(0b001000000000000000000000)
        lsb_twenty_three = self.data_manager.num_to_raw_binary_lsb(0b010000000000000000000000)
        lsb_twenty_four  = self.data_manager.num_to_raw_binary_lsb(0b100000000000000000000000)
        lsb = [lsb_one, lsb_two, lsb_three, lsb_four,
               lsb_five, lsb_six, lsb_seven, lsb_eight,
               lsb_nine, lsb_ten, lsb_eleven, lsb_twelve,
               lsb_thirteen, lsb_fourteen, lsb_fifteen, lsb_sixteen,
               lsb_seventeen, lsb_eighteen, lsb_nineteen, lsb_twenty,
               lsb_twenty_one, lsb_twenty_two, lsb_twenty_three, lsb_twenty_four]
        #idx = 1
        #print(lsb_one)
        #print(lsb[0])
        for i, l in enumerate(lsb):
            self.data_manager.cook_data_into_scintillators(l, t=True, data_is_binary=True, i=i)
        #self.data_manager.cook_data_into_scintillators(lsb[idx-1], t=True, data_is_binary=True)
        import sys
        sys.exit()

        self.point = np.array([60, 60, -81, 1, 1, 1, 1]).astype(np.float32)
        self.p_vao = create_vao(self.point)

        self.line = np.array([
            [0,0,   0,1,1,1,1],
            [0,0,-162,1,1,1,1],
            [0, 1, -162, 1,1,1,1],]).astype(np.float32)
        self.l_vao = create_vao(self.line)

        self.show_colour = False



    def viewport_shenanigans(self, vm):
        vp_b = vm.add_viewport(None, None)

        vp_b.mouse_button_callback = self.mouse_callbacks
        vp_b.cursor_pos_callback = self.cursor_pos_callbacks
        vp_b.scroll_callback = self.scroll_callbacks
        vp_b.window_size_callback = self.window_callbacks

        vp_b.x_ratio, vp_b.y_ratio = self.x_ratio, self.y_ratio
        vp_b.on_render = self.render_loop


    def window_callbacks(self, window, width, height):
        if not (width==0 or height==0):
            self.camera.width, self.camera.height = width, height
            self.camera.zoom = self.camera.zoom*self.camera.aspect_ratio*self.camera.height/self.camera.width
            self.camera.aspect_ratio = width/height

            glViewport(0, 0, width, height)
            # will be changed to double viewport later


    def scroll_callbacks(self, window, xoffset, yoffset):
        scroll_amount = self.camera.zoom/27.5 if self.camera.zoom/27.5 > 0.24 else 0.24

        if ((self.camera.zoom-scroll_amount*yoffset != 0)
                and not
            ((self.camera.zoom-scroll_amount*yoffset > -0.1)
                and
             (self.camera.zoom-scroll_amount*yoffset < 0.1))):
            self.camera.zoom -= scroll_amount*yoffset
    
    def cursor_pos_callbacks(self, window, xpos, ypos):
        if self.camera.panning:
            dx = xpos - self.camera.last_x
            dy = ypos - self.camera.last_y
            self.camera.pan_x += dx * self.camera.pan_sensitivity * self.camera.zoom
            self.camera.pan_y -= dy * self.camera.pan_sensitivity * self.camera.zoom

        if self.camera.angling:
            dx = xpos - self.camera.last_x
            dy = ypos - self.camera.last_y
            self.camera.angle_x += dy * self.camera.angle_sensitivity * self.camera.zoom
            self.camera.angle_y += dx * self.camera.angle_sensitivity * self.camera.zoom

            self.camera.angle_x %= 360
            self.camera.angle_y %= 360
            self.camera.angle_z %= 360


        self.camera.last_x, self.camera.last_y = xpos, ypos
    
    def mouse_callbacks(self, window, button, action, mods):

        if action == glfw.PRESS:
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.camera.panning = True
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                self.camera.angling = True
        if action == glfw.RELEASE:
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.camera.panning = False
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                self.camera.angling = False


    def render_loop(self, paused):

        self.shaders.begin_render_gl_actions()



        self.shaders.set_shader(self.normal_shader)





        if not paused:
            self.data_manager.update_data(self.arduino)

        #if self.data_manager.mode == "debug":
        #    print("window", len(self.data_manager.impl_data_is_checked))

            

        self.data_manager.draw_active_hulls(self.data_manager.data, self.data_manager.impl_data_is_checked)


        self.scintillator_structure.reset_to_initial_colour()  
        if self.show_colour:      
            if self.pt_selected != None:
                self.scintillator_structure.light_scintillators_for_hit(self.pt_selected)
        self.scintillator_structure.renew_vbo()
        self.scintillator_structure.draw_scintillator_structure()



        if self.show_axes:
            self.xyz_axes.draw()


        draw_vao(self.p_vao, GL_POINTS, 1)
        #draw_vao(self.l_vao, GL_TRIANGLES, 3)
        #if self.data_manager.mode == "debug":
        #    print("window_2", len(self.data_manager.impl_data_is_checked))