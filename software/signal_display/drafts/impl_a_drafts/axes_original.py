import numpy as np

from software.signal_display.scintillator_display.display.vao_vbo import create_vao, draw_vao, update_vbo

from OpenGL.GL import *


class Axes:
    def __init__(
        self,
        initial_x_domain,
        initial_y_domain,
    ):
        """
        Axes: XY grid render element with colored XYZ axis lines

        :param initial_x_domain: Initial x domain to draw grid on (min, max)
        :param initial_y_domain: Initial y domain to draw grid on (min, max)
        """

        ranges = self.compute_ranges(initial_x_domain/2, initial_y_domain/2)
        self.update_domain(*ranges)

    def compute_ranges(self, function_x_domain, function_y_domain):
        """
        Compute axes range from user selected domain

        :param function_x_domain: User x domain (min, max)
        :param function_y_domain: User y domain (min, max)
        :return: x range, y range, z range, divisions
        """

        # round to nearest integer
        rounded = np.round(np.abs([function_x_domain, function_y_domain]))

        # find largest value in x and y axes
        range_max = np.max(rounded)

        # build domains
        domain = (-range_max, range_max)

        # a division at every unit
        divs = (0.1 * range_max, 0.1 * range_max)

        return domain, domain, domain, divs

    def update_domain(self, x_range, y_range, z_range, divs):
        """
        Update domain of gridlines

        :param x_range: x domain to draw grid on (min, max)
        :param y_range: y domain to draw grid on (min, max)
        :param z_range: z domain to draw grid on (min, max)
        """

        x_div, y_div = divs

        # build gridlines
        offset = [np.min(x_range), np.min(y_range), 0]
        self.x_vao, self.x_n = self._build_gridline_vao(
            [1, 0, 2], offset, x_div, *x_range
        ) 
        self.y_vao, self.y_n = self._build_gridline_vao(
            [0, 1, 2], offset, y_div, *y_range
        )

        # build XYZ axes lines
        self.axes_vao, self.axes_n = self._build_axes_vao(*x_range, *y_range, *z_range)

    def _build_axes_vao(self, x_min, x_max, y_min, y_max, z_min, z_max):
        """
        Build XYZ axes colored lines VAO

        :param x_min: x range min
        :param x_max: x range max
        :param y_min: y range min
        :param y_max: y range max
        :param z_min: z range min
        :param z_max: z range max
        :return: VAO, number of vertices
        """

        # red line for x-axis
        # blue line for y-axis
        # green line for z-axis

        # data = np.array(
        #     [
        #         #x-axis
        #         [0, 0, 0],  #min
        #         [1, 0, 0],
        #         [x_max, 0, 0],  #max
        #         [1, 0, 0],

        #         #y-axis
        #         [0, 0, 0],  #min
        #         [0, 1, 0],
        #         [0, y_max, 0],  #max
        #         [0, 1, 0],

        #         #z-axis
        #         [0, 0, 0],    #min
        #         [0, 0, 1],
        #         [0, 0, z_max],    #max
        #         [0, 0, 1],
        #     ],
        #     dtype=np.float32,
        # )

        #fixed to be compatible with opacity
        data = np.array([
            [0, 0, 0, 1, 0, 0, 1],  # x-axis start (red, alpha=1)
            [x_max, 0, 0, 1, 0, 0, 1],

            [0, 0, 0, 0, 1, 0, 1],  # y-axis start (green)
            [0, y_max, 0, 0, 1, 0, 1],

            [0, 0, 0, 0, 0, 1, 1],  # z-axis start (blue)
            [0, 0, z_max, 0, 0, 1, 1],
        ], dtype=np.float32)
        return create_vao(data), 6

    def _build_scaled_gridlines(self, s_div, s_min, s_max):
        """
        Build gridlines in specified axis

        :param s_div: Divisions in direction s
        :param s_min: Minimum range in direction s
        :param s_max: Maximum range in direction s

        :return: Gridline vertices of shape (n, 3)
        """

        # create a grid of lines in the specified direction
        grid = np.mgrid[0:2, 0 : 1 : (s_div + 1) * 1j, 0:1].T

        # delete the lines at the center that interfere with the
        # XYZ colored lines
        lines = grid.squeeze(0)
        lines = np.delete(lines, len(lines) // 2, axis=0)

        # reshape vertices into (n, 3) for drawing
        vertices = lines.reshape((-1, 3))
        
        # rescale vertices with respect to range
        return vertices * (s_max - s_min ) 

    def _build_gridline_color(self, vertices, color=[0.6, 0.6, 0.6,1]):
        """
        Build colors of gridline

        :param vertices: Gridline vertices of shape (n, 3)
        :param color: Gridline color
        :return: Gridline vertices with color of shape (n, 6)
        """

        # build colors
        colors = np.ones((vertices.shape[0],4), dtype=np.float32) * color

        # stack colors to coordinates
        return np.hstack((vertices, colors)).astype(np.float32)

    def _build_gridline_vao(self, axis_index, offset, s_div, s_min, s_max):
        """
        Build gridline VAO

        :param axis_index: Axis to draw, x:0, y:1
        :param offset: Translation offset in axis
        :param s_div: Divisions in direction s
        :param s_min: Minimum range in direction s
        :param s_max: Maximum range in direction s
        :return: VAO, number of vertices
        """

        axes_s = self._build_scaled_gridlines(s_div, s_min, s_max)[:, axis_index]
        axes_s += offset
        vao_data = self._build_gridline_color(axes_s)

        return create_vao(vao_data), len(axes_s)

    def draw(self):
        """
        Draw gridlines and axes
        """

        # glLineWidth(0.25)
        draw_vao(self.x_vao, GL_LINES, self.x_n)
        draw_vao(self.y_vao, GL_LINES, self.y_n)

        # glLineWidth(2.0)
        draw_vao(self.axes_vao, GL_LINES, self.axes_n)
