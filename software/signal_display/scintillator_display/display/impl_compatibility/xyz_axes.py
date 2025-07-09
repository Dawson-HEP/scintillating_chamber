import numpy as np

from OpenGL.GL import *


from software.signal_display.scintillator_display.display.impl_compatibility.vao_vbo import create_vao, draw_vao

class Axes:
    def __init__(self, l):
        self.data = np.array([
            [0, 0, 0, 1, 0, 0, 1],
            [l, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 1, 0, 1],
            [0, l, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 1, 1],
            [0, 0, l, 0, 0, 1, 1],
        ]).astype(np.float32)
        self.vao = create_vao(self.data)

    def draw(self):
        draw_vao(self.vao, GL_LINES, self.data.shape[0])