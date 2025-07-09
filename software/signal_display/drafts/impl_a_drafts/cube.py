import numpy as np
from OpenGL.GL import GL_TRIANGLES

from software.signal_display.scintillator_display.display.vao_vbo import create_vao, draw_vao, update_vbo



class Cube:
    def __init__(self, initial_color, size=1.0):
        """
        Cube: Cube render element
        """
        vertices = self.generate_plane_vertices(size)
        self.n = len(vertices)
        
        # Preallocate data buffer for position, color, and normals
        self.data = np.ones((len(vertices), 9), dtype=np.float32)
        self.data[:, :3] = vertices  # Position
        self.data[:, 3:6] = initial_color  # Color
        self.data[0, 3:6] = [1,0,0]
        self.data[:, 6:9] = vertices  # Normals (approximated)
        
        # Build VAO and VBO
        self.vao, self.vbo = create_vao(self.data, return_vbo=True, store_normals=True)

    def generate_plane_vertices(self,size):
        """
        Generate vertices for a cube centered at the origin with a given size.
        """
        s = size / 2.0  # Half-size
        z = 0.1
        vertices = np.array([
            # Front face
            [-s, -s,  z*s], [s, -s,  z*s], [s,  s,  z*s],
            [-s, -s,  z*s], [s,  s,  z*s], [-s,  s,  z*s],
            # Back face
            [-s, -s, -z*s], [-s,  s, -z*s], [s,  s, -z*s],
            [-s, -s, -z*s], [s,  s, -z*s], [s, -s, -z*s],
            # Left face
            [-s, -s, -z*s], [-s, -s,  z*s], [-s,  s,  z*s],
            [-s, -s, -z*s], [-s,  s,  z*s], [-s,  s, -z*s],
            # Right face
            [s, -s, -z*s], [s,  s, -z*s], [s,  s,  z*s],
            [s, -s, -z*s], [s,  s,  z*s], [s, -s,  z*s],
            # Top face
            [-s,  s, -z*s], [-s,  s,  z*s], [s,  s,  z*s],
            [-s,  s, -z*s], [s,  s,  z*s], [s,  s, -z*s],
            # Bottom face
            [-s, -s, -z*s], [s, -s, -z*s], [s, -s,  z*s],
            [-s, -s, -z*s], [s, -s,  z*s], [-s, -s,  z*s]
        ], dtype=np.float32)
        return vertices
    
    def _draw_cube(self, s, pos):
        """
        Draw a cube of size s at position pos.
        """
        data = np.copy(self.data)
        data[:, :3] = data[:, :3] * s + pos  # Scale and translate cube
        update_vbo(self.vbo, data)
        draw_vao(self.vao, GL_TRIANGLES, self.n)

    def set_color(self, new_color):
        """
        Update cube color.
        """
        self.data[:, 3:6] = new_color
        update_vbo(self.vbo, self.data)

    def draw(self, positions, sizes):
        """
        Draw multiple cubes.
        """
        if not len(positions):
            return
        
        for pos, size in zip(positions, sizes):
            self._draw_cube(size, pos)
