import time
from datetime import datetime

import scintillator_display.compat.glfw as glfw

import scintillator_display.compat.imgui as imgui

import pandas as pd

import numpy as np

from scintillator_display.display.impl_compatibility.data_manager import Data
from scintillator_display.compat.pyserial_singleton import ArduinoData


from scintillator_display.display.impl_compatibility.xyz_axes import Axes

import scintillator_display.display.orientation.cube as cube

from scintillator_display.display.impl_compatibility.camera_shader_controls import CameraShaderControls

from scintillator_display.display.orientation.shader.shader_loader import CubeShaderLoader

from OpenGL.GL import *

from scintillator_display.compat.universal_values import MathDisplayValues


class App(MathDisplayValues):
    def __init__(self, init_mode=('data', 'debug', 'demo')):

        if init_mode not in ('data', 'debug', 'demo'):
            init_mode='debug'


        self.true_scaler = 0.1
        #self.true_scaler = 1
        scale = self.SQUARE_LEN * self.true_scaler

        self.zeroes_offset = np.array([
            0, 0, self.SPACE_BETWEEN_STRUCTURES * self.true_scaler / 2
            ])


        self.arduino = ArduinoData()

        self.cam_shader = CameraShaderControls(angle_sensitivity=0.1,zoom=25, clear_colour=(0.87,)*3, offset=self.zeroes_offset)

        self.cube_shader = CubeShaderLoader()


        #setup elements

        self.data_manager = Data(impl_constant=self.true_scaler, impl="a",
                                 hull_colour=[1, 0, 0], hull_opacity=0.3,
                                 store_normals=True,
                                 mode=init_mode)
        
        self.cube = cube.Cube()
        #self.xyz_axes = Axes(l=scale/2)
        self.xyz_axes = Axes(l=4*scale)


        self.pt_selected = None
        self.dataset_active = None
        self.show_axes = True


        self.cam_shader.make_shader_program()
        self.cam_shader.setup_opengl()

        self.cube_shader.make_shader_program()
        self.cube_shader.setup_opengl()

        self.show_colour = True


    def viewport_shenanigans(self, vm, ratio_num):
        vp_a = vm.add_viewport(None, None)
        vm.set_mouse_button_callback(vp_a, self.mouse_button_callback)
        vm.set_cursor_pos_callback(  vp_a, self.cursor_pos_callback)
        vm.set_scroll_callback(      vp_a, self.scroll_callback)
        vm.set_window_size_callback( vp_a, self.resize_callback)

        vm.set_vp_ratio(vp_a, ratio_num)
        vm.set_on_render(vp_a, self.on_render_frame)

    
    def mouse_button_callback(self, window, button, action, mods):
        # filter for right clicks which are
        # for camera movements
        if button != glfw.MOUSE_BUTTON_RIGHT:
            return

        # dragging when: right mouse button held
        self.cam_shader.mouse_dragging = action == glfw.PRESS

        # panning when: ctrl + right mouse button held
        self.cam_shader.panning = glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS

    def cursor_pos_callback(self, window, xpos, ypos):
        if self.cam_shader.mouse_dragging:

            # change in mouse position over one frame
            dx = xpos - self.cam_shader.last_x
            dy = ypos - self.cam_shader.last_y

            if self.cam_shader.panning:
                # adjust pan according to zoom
                # so that translation is always constant,
                # independent of zoom
                zoomed_pan = self.cam_shader.pan_sensitivity * self.cam_shader.zoom

                # updates translation vector
                # [1, -1] flips the y position as OpenGL's origin
                # is at the bottom left corner instead of top left
                self.cam_shader.pan_x += dx * zoomed_pan
                self.cam_shader.pan_y -= dy * zoomed_pan
            else:

                # updates rotation vector
                # [::-1] reverses the order, effectively mapping the
                # x screen position onto the OpenGL's x rotation and
                # y screen position onto the OpenGL's y rotation
                self.cam_shader.angle_x += dy * self.cam_shader.angle_sensitivity
                self.cam_shader.angle_y += dx * self.cam_shader.angle_sensitivity

        # save previous to calculate the next delta
        self.cam_shader.last_x, self.cam_shader.last_y = xpos, ypos

    def scroll_callback(self, window, xoffset, yoffset):
        scroll_amount = self.cam_shader.zoom/27.5 if self.cam_shader.zoom/27.5 > 0.24 else 0.24

        if ((self.cam_shader.zoom-scroll_amount*yoffset != 0)
                and not
            ((self.cam_shader.zoom-scroll_amount*yoffset > -0.1)
                and
             (self.cam_shader.zoom-scroll_amount*yoffset < 0.1))):
            self.cam_shader.zoom -= scroll_amount*yoffset

    def resize_callback(self, window, width, height):
        # update rendering shape
        glViewport(0, 0, width, height)
        self.cam_shader.width, self.cam_shader.height = width, height

        # compute aspect ratio, so that the render
        # is not stretched if the window is stretched
        # bugfix: on X11 Ubuntu 20.04, the height starts
        # at zero when the window is first rendered, so we
        # prevent a zero division error
        self.cam_shader.aspect_ratio = width / height if height > 0 else 1.0


    
    def on_render_frame(self, paused):
        """
        Render frame event callback
        """

        self.cam_shader.begin_render_gl_actions()



        # if not paused:
        #     self.data_manager.update_data(self.arduino)

        #if self.data_manager.mode == "debug":
        #    print("app", len(self.data_manager.impl_data_is_checked))


        
        #draw elements
        #self.data_manager.draw_active_hulls(self.data_manager.data, self.data_manager.impl_data_is_checked)

        if self.show_axes:
            self.xyz_axes.draw()

        #switch shaders
        self.cube_shader.begin_render_gl_actions()
        
        self.cube.draw(self.cube_shader.shader_program)