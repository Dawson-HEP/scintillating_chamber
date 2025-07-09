import glfw

from software.signal_display.scintillator_display.compat.viewport_manager import ViewportManager

def init():
    # glfw.init()

    return True

def window_hint(hint_str, value):
    ...

def create_window(width, height, name, monitor, shader):
    v = ViewportManager()
    return v.add_viewport(width, height)

def terminate():
    ...

def make_context_current(window):
    ...

def swap_buffers(window):
    ...

def poll_events():
    ...

def window_should_close(window):
    return True


def set_mouse_button_callback(window, fn):
    v = ViewportManager()
    v.set_mouse_button_callback(window, fn)

def set_cursor_pos_callback(window, fn):
    v = ViewportManager()
    v.set_cursor_pos_callback(window, fn)

def set_scroll_callback(window, fn):
    v = ViewportManager()
    v.set_scroll_callback(window, fn)

def set_framebuffer_size_callback(*args, **kwargs):
    set_window_size_callback(*args, **kwargs)

def set_window_size_callback(window, fn):
    v = ViewportManager()
    v.set_window_size_callback(window, fn)

def set_key_callback(window, fn):
    v = ViewportManager()
    v.set_key_callback(window, fn)

def set_char_callback(window, fn):
    v = ViewportManager()
    v.set_char_callback(window, fn)

def get_key(window, *args, **kwargs):
    v = ViewportManager()
    return glfw.get_key(v.window, *args, **kwargs)
