import importlib.resources

import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

import software.signal_display.scintillator_display.display.impl_a.graphics.shaders as shaders

import numpy as np


class ShaderRenderer:
    def __init__(self, **kwargs):
        """
        Shader Renderer: Accelerates via GPU lighting computations
        and rendering of frames, and sets up the drawing context
        necessary for OpenGL to function
        """

        super().__init__(**kwargs)

        # self._transform is this 4x4 matrix
        # that transforms between the physics coordinate
        # system and the OpenGL coordinate system
        # physics:
        #   +X towards right
        #   +Y into screen
        #   +Z towards up
        # OpenGL:
        #   +X towards right
        #   +Y towards up
        #   +Z into screen
        #
        # this matrix swaps Y->Z and Z->Y
        # so that the physics engine's computations can
        # be displayed in their correct orientation in
        # OpenGL
        #
        # 1.0, 0.0, 0.0, 0.0
        # 0.0, 0.0, 1.0, 0.0
        # 0.0, 1.0, 0.0, 0.0
        # 0.0, 0.0, 0.0, 1.0

        self._transform = glm.mat4x4(
            1.0,0.0,0.0,0.0,
            0.0,0.0,1.0,0.0,
            0.0,1.0,0.0,0.0,
            0.0,0.0,0.0,1.0,
        )

        # camera view vector in OpenGL coordinate system
        # camera is looking 32 units into Z (screen)
        self._view_vec = glm.vec4(0, 0, 32, 1)

    def get_right_handed(self):
        """
        Return conversion transformation matrix from the
        right-handed physics coordinate system

        :return: Matrix of shape (4, 4)
        """

        return self._transform

    def _load_shader_source(self, file, type):
        """
        Load a shader from source that is contained within the
        joule.graphics.shaders namespace

        :param file: File name of shader
        :param type: Type of shader: GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
        :return: OpenGL compiled shader
        """

        # read source code as text
        source = importlib.resources.read_text(shaders, file)

        # return compiled
        return compileShader(source, type)

    def _load_shader(self):
        """
        Load main renderer shaders from source, and compile as
        program for rendering pipeline

        :return: OpenGL compiled shader program
        """

        # load vertex shader (for transforming vertices)
        v_shader = self._load_shader_source("vertex.glsl", GL_VERTEX_SHADER)

        # load fragment shader (for computing lighting)
        f_shader = self._load_shader_source("fragment.glsl", GL_FRAGMENT_SHADER)

        # return combined OpenGL shader pipeline
        return compileProgram(v_shader, f_shader)

    def _uniform_float(self, name, value):
        """
        Set float shader uniform value

        :param name: Name of uniform
        :param value: New value of uniform
        """

        location = glGetUniformLocation(self._shader, name)
        glUniform1f(location, value)

    def _uniform_vec3(self, name, glm_vec3):
        """
        Set vec3 shader uniform value

        :param name: Name of uniform
        :param value: New vec3 of uniform
        """

        location = glGetUniformLocation(self._shader, name)
        try:
            glUniform3fv(location, 1, glm.value_ptr(glm_vec3))
        except:
            glUniform3fv(location, 1, glm_vec3)


    def _uniform_mat4(self, name, glm_mat4):
        """
        Set matrix 4x4 shader uniform value

        :param name: Name of uniform
        :param value: New matrix 4x4 of uniform
        """

        location = glGetUniformLocation(self._shader, name)
        try:
            glUniformMatrix4fv(location, 1, GL_TRUE, glm.value_ptr(glm_mat4))
        except:
            glUniformMatrix4fv(location, 1, GL_TRUE, glm_mat4)


    def render_setup(self):
        """
        Setup rendering pipeline on program initialize
        """


        # load shader pipeline
        self._shader = self._load_shader()

        # enable depth to compute visual occlusion of objects
        glEnable(GL_DEPTH_TEST)

        # enable antialiasing (smooth lines)
        glEnable(GL_MULTISAMPLE)
        # glEnable(GL_POINT_SMOOTH)

        # enable opacity (transparency)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def frame_setup(self, background_color):
        """
        Setup rendering pipeline on each frame

        :param background_color: Screen background color as vector of shape (3,)
        """

        # set background color
        glClearColor(*background_color, 1.0)

        # Dual-viewports: Clear bufferbit after clear color
        # clear color and depth cache from previous frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # use shader
        glUseProgram(self._shader)

    def set_matrix_uniforms(
        self,
        cam_projection,
        cam_transform,
    ):
        """
        Supply camera and world matrix transforms to shader to
        project 3D coordinates onto screen using GPU acceleration

        :param cam_projection: Orthographic projection matrix of shape (4, 4)
        :param cam_transform: Camera view transformation matrix of shape (4, 4)
        """

        # pass values into shader
        # see joule/graphics/shaders/vertex.glsl
        # the values are plugged into the shader as constants
        #   uniform mat4 world_transform;
        #   uniform mat4 cam_projection;
        #   uniform mat4 cam_transform;
        #
        # all subsequent dot products are done with these values,
        # which accelerates 3D point transformation with GPU

        self._uniform_mat4("world_transform", self.get_right_handed())
        self._uniform_mat4("cam_transform", cam_transform)
        self._uniform_mat4("cam_projection", cam_projection)

        # if cam_transform transforms points into the camera's view
        # then the inverse of cam_transform describes the camera's
        # position with respect to the points
        #cam_transform_inv = glm.inverse(cam_transform)

        # compute the camera's view position
        #view_pos = glm.vec3(cam_transform_inv * self._view_vec)

        view_pos = np.linalg.inv(cam_transform) * self._view_vec

        # see joule/graphics/shaders/fragment.glsl
        #   uniform vec3 view_pos;
        #   uniform vec3 light_pos;
        #
        # for light reflection computation
        self._uniform_vec3("view_pos", view_pos)
        self._uniform_vec3("light_pos", view_pos)

    def set_lighting_uniforms(
        self,
        light_color,
        ambient_strength=0.2,
        diffuse_strength=0.2,
        diffuse_base=0.3,
        specular_strength=0.1,
        specular_reflection=64.0,
    ):
        """
        Lighting constants to shader for lighting graphics calculations
        by GPU acceleration

        Using the Phong Reflection Model

        :param light_color: Light color vector of shape (3,)
        :param ambient_strength: Ambient light strength
        :param diffuse_strength: Diffuse light strength
        :param diffuse_base: Diffuse light offset
        :param specular_strength: Specular light strength
        :param specular_reflection: Specular reflection strength
        """

        # see joule/graphics/shaders/fragment.glsl
        #   uniform vec3 light_color;
        #   uniform float ambient_strength;
        #   uniform float diffuse_strength;
        #   uniform float diffuse_base;
        #   uniform float specular_strength;
        #   uniform float specular_reflection;
        #
        # for light reflection computation
        self._uniform_vec3("light_color", light_color)

        self._uniform_float("ambient_strength", ambient_strength)
        self._uniform_float("diffuse_strength", diffuse_strength)
        self._uniform_float("diffuse_base", diffuse_base)
        self._uniform_float("specular_strength", specular_strength)
        self._uniform_float("specular_reflection", specular_reflection)
