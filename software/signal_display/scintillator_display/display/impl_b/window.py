import time


import scintillator_display.compat.glfw as glfw


from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

from scintillator_display.display.impl_compatibility.camera_shader_controls import CameraShaderControls

from scintillator_display.display.impl_b.scintillator_blocks import ScintillatorStructure
from scintillator_display.display.impl_compatibility.scintillator_blocks_build import ScintillatorBlocks

from scintillator_display.display.impl_compatibility.vao_vbo import create_vao, update_vbo, draw_vao

from scintillator_display.display.impl_compatibility.xyz_axes import Axes

from scintillator_display.display.impl_compatibility.data_manager import Data

from scintillator_display.compat.pyserial_singleton import ArduinoData

from scintillator_display.compat.universal_values import MathDisplayValues


class Window(MathDisplayValues):
    def __init__(self, init_mode=('data', 'debug', 'demo'), x_ratio=(3, 5, 5), y_ratio=(0, 1, 1)):

        self.x_ratio, self.y_ratio = x_ratio, y_ratio

        if init_mode not in ('data', 'debug', 'demo'):
            init_mode='debug'

        self.zeroes_offset = np.array([
            self.SQUARE_LEN/2, self.SQUARE_LEN/2, -self.SPACE_BETWEEN_STRUCTURES/2
            ])

        self.cam_shader = CameraShaderControls(zoom=90, offset=self.zeroes_offset)
        self.arduino = ArduinoData()
        self.data_manager = Data(impl_constant=1, impl="b",
                            hull_colour=[0.5, 0, 0.5], hull_opacity=0.8,
                            store_normals=True,
                            mode=init_mode)
        #self.scintillator_structure = ScintillatorStructure(self.data_manager)
        self.scintillator_structure = ScintillatorBlocks(self.data_manager)
        self.xyz_axes = Axes(l=250)


        self.cam_shader.make_shader_program()
        self.cam_shader.setup_opengl()


        self.pt_selected = None
        self.show_axes = True



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
            self.cam_shader.width, self.cam_shader.height = width, height
            self.cam_shader.zoom = self.cam_shader.zoom*self.cam_shader.aspect_ratio*self.cam_shader.height/self.cam_shader.width
            self.cam_shader.aspect_ratio = width/height

            glViewport(0, 0, width, height)
            # will be changed to double viewport later


    def scroll_callbacks(self, window, xoffset, yoffset):
        scroll_amount = self.cam_shader.zoom/27.5 if self.cam_shader.zoom/27.5 > 0.24 else 0.24

        if ((self.cam_shader.zoom-scroll_amount*yoffset != 0)
                and not
            ((self.cam_shader.zoom-scroll_amount*yoffset > -0.1)
                and
             (self.cam_shader.zoom-scroll_amount*yoffset < 0.1))):
            self.cam_shader.zoom -= scroll_amount*yoffset
    
    def cursor_pos_callbacks(self, window, xpos, ypos):
        if self.cam_shader.panning:
            dx = xpos - self.cam_shader.last_x
            dy = ypos - self.cam_shader.last_y
            self.cam_shader.pan_x += dx * self.cam_shader.pan_sensitivity * self.cam_shader.zoom
            self.cam_shader.pan_y -= dy * self.cam_shader.pan_sensitivity * self.cam_shader.zoom

        if self.cam_shader.angling:
            dx = xpos - self.cam_shader.last_x
            dy = ypos - self.cam_shader.last_y
            self.cam_shader.angle_x += dy * self.cam_shader.angle_sensitivity * self.cam_shader.zoom
            self.cam_shader.angle_y += dx * self.cam_shader.angle_sensitivity * self.cam_shader.zoom

            self.cam_shader.angle_x %= 360
            self.cam_shader.angle_y %= 360
            self.cam_shader.angle_z %= 360


        self.cam_shader.last_x, self.cam_shader.last_y = xpos, ypos
    
    def mouse_callbacks(self, window, button, action, mods):

        if action == glfw.PRESS:
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.cam_shader.panning = True
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                self.cam_shader.angling = True
        if action == glfw.RELEASE:
            if button == glfw.MOUSE_BUTTON_LEFT:
                self.cam_shader.panning = False
            elif button == glfw.MOUSE_BUTTON_RIGHT:
                self.cam_shader.angling = False


    def render_loop(self, paused):

        self.cam_shader.begin_render_gl_actions()




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