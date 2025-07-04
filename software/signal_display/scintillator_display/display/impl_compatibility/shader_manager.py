import numpy as np

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

import os

from scintillator_display.display.impl_compatibility.camera_controls import CameraControls

class ShaderManager():
    def __init__(self, camera:CameraControls,
                 shader_names=[("vertex_shader.glsl", "fragment_shader.glsl")], is_orientation = False):
        self.camera = camera
        self.shader_names = shader_names

        self.is_orientation = is_orientation

    def get_shader_text(self, shader_file):
        this_file_path = os.path.abspath(__file__)
        lst_f_path = this_file_path.split(os.sep)

        vertex_path = lst_f_path.copy()
        vertex_path[-1] = shader_file
        vertex_path   = os.sep.join(vertex_path)
        
        with open(vertex_path, "r") as f:
            vertex_shader_text = f.read()
        
        return vertex_shader_text

    def make_shader_programs(self, glsl_paired_files:list[tuple]):
        self.shader_programs = []
        for vertex, fragment in glsl_paired_files:
            vertex_text = self.get_shader_text(vertex)
            fragment_text = self.get_shader_text(fragment)

            vertex_shader = compileShader(vertex_text, GL_VERTEX_SHADER)
            fragment_shader = compileShader(fragment_text, GL_FRAGMENT_SHADER)

            self.shader_programs.append(compileProgram(vertex_shader, fragment_shader, validate=False))



    def set_shader(self, shader_program):
        glUseProgram(shader_program)
        self.set_uniforms(shader_program)





    def set_uniform_float(self, uniform_name, num, shader_program):
        location = glGetUniformLocation(shader_program, uniform_name)
        glUniform1f(location, num)

    def set_uniform_vec3(self, uniform_name, vec3, shader_program):
        location = glGetUniformLocation(shader_program, uniform_name)
        glUniform3fv(location, 1, vec3)

    def set_uniform_mat4(self, uniform_name, mat4, shader_program):
        location = glGetUniformLocation(shader_program, uniform_name)
        glUniformMatrix4fv(location, 1, GL_TRUE, mat4)

    def set_uniform_int(self, uniform_name, num, shader_program):
        # for textures
        texture_location = glGetUniformLocation(shader_program, uniform_name)
        glUniform1i(texture_location, num)  # Use texture unit 0

    def setup_opengl(self):

        self.make_shader_programs(self.shader_names)

        # enable depth to compute visual occlusion of objects
        glEnable(GL_DEPTH_TEST)

        # enable antialiasing (smooth lines)
        glEnable(GL_MULTISAMPLE)
        # glEnable(GL_POINT_SMOOTH)

        # enable opacity (transparency)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        


    def begin_render_gl_actions(self):
        # set background color
        if not self.is_orientation:
            glClearColor(*self.camera.clear_colour, 1.0)
        else:
            glClearColor(*self.camera.clear_colour, 0)    #transparent background for orientation feature

        # Dual-viewports: Clear bufferbit after clear color
        # clear color and depth cache from previous frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def set_uniforms(self, shader_program):
        camera_transform = self.camera.get_camera_tranform(self.is_orientation)     #if self.is_orientation, then there is no panning

        self.set_uniform_mat4("world_transform" , self.camera.get_world_transform(), shader_program)
        self.set_uniform_mat4("cam_transform"   , camera_transform, shader_program)
        self.set_uniform_mat4("ortho_projection", self.camera.get_orthographic_projection(), shader_program)

        view_pos = np.linalg.inv(camera_transform) * self.camera.view_vec

        self.set_uniform_vec3("view_pos" , view_pos, shader_program)
        self.set_uniform_vec3("light_pos", view_pos, shader_program)

        self.set_uniform_vec3("light_color", self.camera.light_color, shader_program)

        self.set_uniform_float("ambient_strength"   , self.camera.ambient_strength, shader_program)
        self.set_uniform_float("diffuse_strength"   , self.camera.diffuse_strength, shader_program)
        self.set_uniform_float("diffuse_base"       , self.camera.diffuse_base, shader_program)
        self.set_uniform_float("specular_strength"  , self.camera.specular_strength, shader_program)
        self.set_uniform_float("specular_reflection", self.camera.specular_reflection, shader_program)

        # NOTE if multiple textures become used, change int per texture
        self.set_uniform_int("tex", 0, shader_program)