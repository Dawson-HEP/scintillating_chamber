import numpy as np

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

import os

from scintillator_display.compat.universal_values import MathDisplayValues

class CubeShaderLoader:
    def __init__(self):
        pass
    
    def setup_opengl(self):

        self.make_shader_program()

        # enable depth to compute visual occlusion of objects
        glEnable(GL_DEPTH_TEST)

        # enable antialiasing (smooth lines)
        glEnable(GL_MULTISAMPLE)
        # glEnable(GL_POINT_SMOOTH)

        # enable opacity (transparency)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def get_vertex_shader_text(self):
            this_file_path = os.path.abspath(__file__)
            lst_f_path = this_file_path.split(os.sep)

            vertex_path = lst_f_path.copy()
            vertex_path[-1] = "cube_vertex_shader.glsl"
            vertex_path   = os.sep.join(vertex_path)
            
            with open(vertex_path, "r") as f:
                vertex_shader_text = f.read()
            
            return vertex_shader_text

    def get_fragment_shader_text(self):
        
        this_file_path = os.path.abspath(__file__)
        lst_f_path = this_file_path.split(os.sep)

        fragment_path = lst_f_path.copy()
        fragment_path[-1] = "cube_fragment_shader.glsl"
        fragment_path   = os.sep.join(fragment_path)
        
        with open(fragment_path, "r") as f:
            fragment_shader_text = f.read()
        
        return fragment_shader_text

    def make_shader_program(self):
        vertex_text = self.get_vertex_shader_text()
        vertex_shader = compileShader(vertex_text, GL_VERTEX_SHADER)

        fragment_text = self.get_fragment_shader_text()
        fragment_shader = compileShader(fragment_text, GL_FRAGMENT_SHADER)
        
        self.shader_program = compileProgram(vertex_shader, fragment_shader, validate=False)

    def begin_render_gl_actions(self):
        # set background color
        # glClearColor(*self.clear_colour, 1.0)

        # Dual-viewports: Clear bufferbit after clear color
        # clear color and depth cache from previous frame
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # use shader
        glUseProgram(self.shader_program)
            


        #self.set_uniforms()