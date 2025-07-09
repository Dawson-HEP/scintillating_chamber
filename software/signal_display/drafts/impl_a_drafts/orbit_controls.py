import glm

# import glfw
import software.signal_display.scintillator_display.compat.glfw as glfw

import numpy as np


from OpenGL.GL import glViewport, glReadPixels, GL_DEPTH_COMPONENT, GL_FLOAT


class CameraOrbitControls:
    def __init__(
        self,
        zoom_sensitivity=0.1,
        pan_sensitvity=0.001,
        orbit_sensitivity=0.0025,
        initial_zoom=5,
        initial_view_angle=(np.pi / 6, np.pi / 4),
        clipping=[-512, 512],
        **kwargs,
    ):
        """
        Camera Orbit Controls: Manages mouse camera movement
        to translate, rotate, and scale current view with
        orthographic projection

        :param zoom_sensitivity: Mouse scroll to view scale ratio
        :param pan_sensitvity:  Mouse move to view translate ratio
        :param orbit_sensitivity: Mouse move to view rotate ratio
        :param initial_zoom: Initial view scale
        :param initial_view_angle: Initial X and Y view angle in radians
        :param clipping: Clipping planes for orthographic projection
        """
        super().__init__(**kwargs)

        # constants
        self._zoom_sensitivity = zoom_sensitivity
        self._pan_sensitivity = pan_sensitvity
        self._orbit_sensitivity = orbit_sensitivity

        self._zoom_level = initial_zoom
        self._clipping = clipping

        # vector states
        self._view_angle = np.array(initial_view_angle)
        self._view_pan = np.zeros(2)
        self._view_box = np.zeros(2)
        self._prev_mouse_pos = np.zeros(2)

        # store internal state
        # when dragging           -> rotation
        # when dragging + panning -> translation
        self._dragging, self._panning = False, False


    def get_camera_projection(self):
        """
        Computes a orthographic projection matrix
        with the internal view parameters

        :return: Orthographic projection matrix of shape (4, 4)
        """

        (l, r, b, t, n, f) = (self._view_box[0] * self._zoom_level,
                            self._view_box[1] * self._zoom_level,
                            -self._zoom_level,
                            self._zoom_level,
                            self._clipping[0],
                            self._clipping[1])
        orthographic_projection = np.array([
            [2/(r-l), 0, 0, 0],
            [0, 2/(t-b), 0, 0],
            [0, 0, 2/(f-n), 0],
            [-(r+l)/(r-l), -(t+b)/(t-b), -(f+n)/(f-n), 1],
        ])

        p = glm.ortho(
            *self._view_box * self._zoom_level,
            -self._zoom_level,
            self._zoom_level,
            *self._clipping,
        )

        return orthographic_projection

    def get_camera_transform(self):
        """
        Computes the view transformation matrix
        with the internal view parameters

        :return: Camera view transformation matrix of shape (4, 4)
        """

        def translation_rotation_scale_matrix(t=(0, 0, 0), r=(0, 0, 0)):
            tx, ty, tz = t
            drx, dry, drz = r # degrees
            rrx, rry, rrz = np.radians(drx), np.radians(dry), np.radians(drz),
            #rrx, rry, rrz = drx, dry, drz,

            translation = np.array([
                [1, 0, 0, tx],
                [0, 1, 0, ty],
                [0, 0, 1, tz],
                [0, 0, 0, 1]])
            
            rot_x = np.array([
                [1,            0,           0, 0],
                [0,  np.cos(rrx), np.sin(rrx), 0],
                [0, -np.sin(rrx), np.cos(rrx), 0],
                [0,            0,           0, 1]])

            rot_y = np.array([
                [np.cos(rry), 0, -np.sin(rry), 0],
                [          0, 1,            0, 0],
                [np.sin(rry), 0,  np.cos(rry), 0],
                [          0, 0,            0, 1]])

            rot_z = np.array([
                [np.cos(rrz), -np.sin(rrz), 0, 0],
                [np.sin(rrz),  np.cos(rrz), 0, 0],
                [          0,            0, 1, 0],
                [          0,            0, 0, 1],])

            
            transformation_matrix = translation @ rot_x @ rot_y @ rot_z
            #transformation_matrix = translation @ rot_z @ rot_y @ rot_x

            return transformation_matrix



        # compose matrix transformations
        # first translate for panning
        t = glm.translate(glm.vec3(*self._view_pan, 0.0))

        # then rotate on X and Y axes
        t = glm.rotate(t, self._view_angle[0], (1.0, 0.0, 0.0))
        t = glm.rotate(t, self._view_angle[1], (0.0, 1.0, 0.0))

        t2 = translation_rotation_scale_matrix(t=(*self._view_pan, 0), r=(*self._view_angle, 15))

        return t2

    #def get_click_point(self, window, world_transform):
    #    """
    #    Unprojects a 2D click on the window into 3D coordinates
    #    with respect to the internalal view parameters
#
    #    :param window: glfw window of click
    #    :param world_transform: Other transformation not included in view
#
    #    :return: Coordinates of click as vector of shape (3,)
    #    """
#
    #    # get current mouse click position on window
    #    xpos, ypos = glfw.get_cursor_pos(window)
    #    win_x, win_y = glfw.get_window_size(window)
#
    #    # transform window coordinates into OpenGL coordinates
    #    # by flipping y-axis (I found this out the hard way.)
    #    ypos = win_y - ypos
#
    #    # read depth component of current frame
    #    depth = glReadPixels(xpos, ypos, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
    #    # depth = self._zoom_level
    #    # vectorize the click
    #    click = glm.vec3(xpos, ypos, depth)
#
    #    # determine compounded projection from point to frame
    #    # can determine the click coordinates
    #    pos = self.get_camera_transform()
    #    modelview = pos * world_transform
    #    proj = self.get_camera_projection()
#
    #    # vectorize the viewport
    #    viewport = glm.vec4(0, 0, win_x, win_y)
#
    #    # unproject: send out a ray from where the window was clicked
    #    # that goes until it meets the depth from the depth buffer,
    #    # which is the ray's endpoint (the 3D coordinate of click)
    #    return glm.unProject(click, modelview, proj, viewport)
