# import imgui
# from imgui.integrations.glfw import GlfwRenderer

import software.signal_display.scintillator_display.compat.imgui as imgui
from software.signal_display.scintillator_display.compat.imgui.integrations.glfw import GlfwRenderer

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

import time

class ImguiStuff:
    def __init__(self):
        pass
        self.data_boxes_checked = []
        self.data_points = []




    def in_use(self):
        if self.imgui_use != None and imgui.get_io().want_capture_mouse:
            return True


    def initiate_imgui(self, window, appname):
        self.appname = appname
        imgui.create_context()
        imgui.get_io().display_size = 100,100
        self.imgui_use = GlfwRenderer(window, attach_callbacks=False)


    def imgui_box(self, dt, window, opengl):
        imgui.new_frame()
        imgui.begin(self.appname)

        if not window.paused:
            if dt != 0:
                imgui.text(f'{1/dt:.4g} fps')
        else:
            imgui.text(f"paused ({1/dt:.4g} fps)")

        imgui.text(f'{window.angle_x:.3g}, {window.angle_y:.3g}, {window.angle_z:.3g} : angles x, y, z')
        imgui.text(f'{window.pan_x:.3g}, {window.pan_y:.3g}, {window.pan_z:.3g} : pan x, y, z')
        imgui.text(f'{window.zoom:.3g} : zoom level')
        imgui.text(f'{window.aspect_ratio:.3g} : aspect ratio')


        #imgui.show_demo_window()

        if self.data_boxes_checked != []:
            for i, point in enumerate(self.data_points):
                _, self.data_boxes_checked[i] = imgui.checkbox(f"{point[-1]}##L{i}", self.data_boxes_checked[i])
                #if _:
                #    print(i, _, self.data_boxes_checked[i])
                #    print()
                #if change_state:
                #    self.data_boxes_checked[i] = checkbox_enabled

        #if self.data_boxes_checked == True:
        #    print(self.data_boxes_checked)
        #print(len(self.data_boxes_checked))

        imgui.end()

    def render_box(self):
        imgui.render()
        self.imgui_use.process_inputs()
        self.imgui_use.render(imgui.get_draw_data())