import glfw
import imgui

from OpenGL.GL import glViewport, glEnable, GL_SCISSOR_TEST, glScissor, glDisable
from scintillator_display.compat.imgui_manager import ImguiManager

import time


class ViewportManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ViewportManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.pause_time = time.time()
        self.paused = False
        self.done = False

        self.width, self.height = (1280, 720)
        self.window = self.create_window((self.width, self.height), "Scintillating Chamber")

        self.viewports: list[Viewport] = []
        self.vp_current = 0

        self.vp_focus = 0
        self.vp_focused = False

        self._intersect_regions = []

        self.imgui = ImguiManager(self.window)

    def render_loop(self):
        self.vp_resize(vp_resize_callback=True)
        glEnable(GL_SCISSOR_TEST)

        while (not glfw.window_should_close(self.window)) and (not self.done):
            imgui.new_frame()


            for i, vp in enumerate(self.viewports):
                glViewport(vp.xpos, vp.ypos, vp.width, vp.height)
                glScissor(vp.xpos, vp.ypos, vp.width, vp.height)
                vp.on_render(self.paused)

            imgui.render()
            self.imgui.impl.process_inputs()
            self.imgui.impl.render(imgui.get_draw_data())

            glfw.swap_buffers(self.window)
            glfw.poll_events()

        if self.generate_csv:
            self.end_csv()

        glDisable(GL_SCISSOR_TEST)
        glfw.terminate()

    def create_window(self, window_size, name):
        # throw exception if glfw failed to init
        if not glfw.init():
            raise Exception("GLFW could not be initialized.")

        # enable multisampling (antialiasing) on glfw window
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # create window and context
        # window = glfw.create_window(*window_size, name, glfw.get_primary_monitor(), None) # for full screen
        window = glfw.create_window(*window_size, name, None, None)
        if not window:
            glfw.terminate()
            raise Exception("GLFW window could not be created.")
        glfw.make_context_current(window)

        glfw.set_cursor_pos_callback(window, self._cursor_pos_callback)
        glfw.set_mouse_button_callback(window, self._mouse_button_callback)
        glfw.set_scroll_callback(window, self._scroll_callback)
        glfw.set_window_size_callback(window, self._window_size_callback)

        glfw.set_key_callback(window, self._key_callback)
        glfw.set_char_callback(window, self._char_callback)

        def pause_and_escape(window, key, scancode, action, mods):
            if action == glfw.PRESS:
                if key == glfw.KEY_ESCAPE:
                    self.done = True
                if (key == glfw.KEY_SPACE) and (not self.paused):
                    self.paused = True
                    self.pause_time = time.time()
                if (key == glfw.KEY_SPACE) and (self.paused) and (time.time() - self.pause_time > 0.01):
                    self.paused = False

        # pause button
        glfw.set_key_callback(window, pause_and_escape)

        return window
    
    def get_focused_vp(self):
        return self.vp_focus if self.vp_focused else self.vp_current

    def _cursor_pos_callback(self, window, xpos, ypos):
        self.vp_current = self.vp_intersect(xpos, ypos)

        if self.imgui.want_mouse:
            return

        vp = self.viewports[self.get_focused_vp()]
        vp.cursor_pos_callback(vp, xpos, ypos)

    def _mouse_button_callback(self, window, button, action, mods):        
        if self.imgui.want_mouse:
            return
        
        self.vp_focused = action == glfw.PRESS
        if not self.vp_focused:
            deselect_vp = self.viewports[self.vp_focus]
            deselect_vp.mouse_button_callback(deselect_vp, button, glfw.RELEASE, mods)

        self.vp_focus = self.vp_current

        vp = self.viewports[self.get_focused_vp()]
        vp.mouse_button_callback(vp, button, action, mods)

    def _scroll_callback(self, window, xoffset, yoffset):
        if self.imgui.want_mouse:
            return
        
        vp = self.viewports[self.get_focused_vp()]
        vp.scroll_callback(vp, xoffset, yoffset)

    def _window_size_callback(self, window, width, height):
        self.width = width
        self.height = height
        self.vp_resize(vp_resize_callback=True)

    def _key_callback(self, *args, **kwargs):
        if self.imgui.want_keyboard:
            self.ui.impl.keyboard_callback(*args, **kwargs)
            return

        vp = self.viewports[self.get_focused_vp()]
        vp.key_callback(*args, **kwargs)

    def _char_callback(self, *args, **kwargs):
        if self.imgui.want_keyboard:
            self.ui.impl.keyboard_callback(*args, **kwargs)
            return

        vp = self.viewports[self.get_focused_vp()]
        vp.char_callback(*args, **kwargs)

    def add_viewport(self, width, height):
        vp_new = Viewport()
        self.viewports.append(vp_new)

        return vp_new
    
    def vp_resize(self, vp_resize_callback=False):
        for i, vp in enumerate(self.viewports):

            x_depth = self.width  * (vp.x_ratio[1]-vp.x_ratio[0])/vp.x_ratio[2]
            y_depth = self.height * (vp.y_ratio[1]-vp.y_ratio[0])/vp.y_ratio[2]

            x_start = self.width * vp.x_ratio[0]/vp.x_ratio[2]
            y_start = self.width * vp.y_ratio[0]/vp.y_ratio[2]

            vp.xpos   = int(x_start)
            vp.ypos   = int(y_start)
            if i ==0:
                vp.width  = int(x_depth)# if int(x_depth) > 200 else 200
            else:
                vp.width = int(x_depth)
            vp.height = int(y_depth)
        
            if vp_resize_callback:
                vp.window_size_callback(vp, vp.width, vp.height)
    
    def vp_intersect(self, xpos, ypos):
        for i, vp in enumerate(self.viewports):
            if (vp.xpos <= xpos <= vp.xpos+vp.width) and (vp.ypos <= ypos <= vp.ypos+vp.height):
                return i
        return 0

class Viewport:
    def __init__(self):#, idx):
        self.xpos = None
        self.ypos = None
        self.width = None
        self.height = None

        self.x_ratio = None
        self.y_ratio = None

        self.mouse_button_callback = self.null
        self.cursor_pos_callback = self.null
        self.scroll_callback = self.null
        self.window_size_callback = self.null
        self.char_callback = self.null
        self.key_callback = self.null
        self.on_render = self.null

    def null(self, *args):
        pass