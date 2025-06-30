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


from scintillator_display.display.impl_compatibility.camera_controls import CameraControls
from scintillator_display.display.impl_compatibility.shader_manager import ShaderManager

from OpenGL.GL import *

from scintillator_display.compat.universal_values import MathDisplayValues


class App(MathDisplayValues):
    def __init__(self, init_mode=('data', 'debug', 'demo'), x_ratio=(1, 3, 5), y_ratio=(0, 1, 1)):

        self.x_ratio, self.y_ratio = x_ratio, y_ratio


        if init_mode not in ('data', 'debug', 'demo'):
            init_mode='debug'


        self.true_scaler = 0.1
        #self.true_scaler = 1
        scale = self.SQUARE_LEN * self.true_scaler

        self.zeroes_offset = np.array([
            0, 0, self.SPACE_BETWEEN_STRUCTURES * self.true_scaler / 2
            ])
        
        self.zeroes_offset = np.array([0, 0, 0])


        self.arduino = ArduinoData()

        self.camera = CameraControls(angle_sensitivity=0.1,zoom=5, clear_colour=(0.87,)*3, offset=self.zeroes_offset)
        self.shaders = ShaderManager(self.camera,
                                     shader_names=[
                                         ("vertex_shader.glsl", "fragment_shader.glsl"),
                                         ("texture_vertex_shader.glsl", "texture_fragment_shader.glsl")
                                     ])
        



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


        self.shaders.setup_opengl()
        self.normal_shader, self.texture_shader = self.shaders.shader_programs


        self.show_colour = True



    def viewport_shenanigans(self, vm):
        vp_a = vm.add_viewport(None, None)

        vp_a.mouse_button_callback = self.mouse_button_callback
        vp_a.cursor_pos_callback = self.cursor_pos_callback
        vp_a.scroll_callback = self.scroll_callback
        vp_a.window_size_callback = self.resize_callback

        vp_a.x_ratio, vp_a.y_ratio = self.x_ratio, self.y_ratio
        vp_a.on_render = self.on_render_frame

    
    def mouse_button_callback(self, window, button, action, mods):
        # filter for right clicks which are
        # for camera movements
        if button != glfw.MOUSE_BUTTON_RIGHT:
            return

        # dragging when: right mouse button held
        self.camera.mouse_dragging = action == glfw.PRESS

        # panning when: ctrl + right mouse button held
        self.camera.panning = glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS

    def cursor_pos_callback(self, window, xpos, ypos):
        if self.camera.mouse_dragging:

            # change in mouse position over one frame
            dx = xpos - self.camera.last_x
            dy = ypos - self.camera.last_y

            if self.camera.panning:
                # adjust pan according to zoom
                # so that translation is always constant,
                # independent of zoom
                zoomed_pan = self.camera.pan_sensitivity * self.camera.zoom

                # updates translation vector
                # [1, -1] flips the y position as OpenGL's origin
                # is at the bottom left corner instead of top left
                self.camera.pan_x += dx * zoomed_pan
                self.camera.pan_y -= dy * zoomed_pan
            else:

                # updates rotation vector
                # [::-1] reverses the order, effectively mapping the
                # x screen position onto the OpenGL's x rotation and
                # y screen position onto the OpenGL's y rotation
                self.camera.angle_x += dy * self.camera.angle_sensitivity
                self.camera.angle_y += dx * self.camera.angle_sensitivity

        # save previous to calculate the next delta
        self.camera.last_x, self.camera.last_y = xpos, ypos

    def scroll_callback(self, window, xoffset, yoffset):
        scroll_amount = self.camera.zoom/27.5 if self.camera.zoom/27.5 > 0.24 else 0.24

        if ((self.camera.zoom-scroll_amount*yoffset != 0)
                and not
            ((self.camera.zoom-scroll_amount*yoffset > -0.1)
                and
             (self.camera.zoom-scroll_amount*yoffset < 0.1))):
            self.camera.zoom -= scroll_amount*yoffset

    def resize_callback(self, window, width, height):
        # update rendering shape
        glViewport(0, 0, width, height)
        self.camera.width, self.camera.height = width, height

        # compute aspect ratio, so that the render
        # is not stretched if the window is stretched
        # bugfix: on X11 Ubuntu 20.04, the height starts
        # at zero when the window is first rendered, so we
        # prevent a zero division error
        self.camera.aspect_ratio = width / height if height > 0 else 1.0


    
    def on_render_frame(self, paused):
        """
        Render frame event callback
        """

        self.shaders.begin_render_gl_actions()



        self.shaders.set_shader(self.normal_shader)        
        if self.show_axes:
            self.xyz_axes.draw()

        # if not paused:
        #     self.data_manager.update_data(self.arduino)

        #if self.data_manager.mode == "debug":
        #    print("app", len(self.data_manager.impl_data_is_checked))


        
        #draw elements
        #self.data_manager.draw_active_hulls(self.data_manager.data, self.data_manager.impl_data_is_checked)
        

        # use shader
        self.shaders.set_shader(self.texture_shader)        
        self.cube.draw()
