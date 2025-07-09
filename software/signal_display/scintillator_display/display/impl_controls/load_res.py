import importlib
import importlib.resources

import software.signal_display.scintillator_display.compat.imgui as imgui
import software.signal_display.scintillator_display.display.impl_controls.res as res

import OpenGL.GL as gl
from PIL import Image

from software.signal_display.scintillator_display.compat.viewport_manager import ViewportManager


def bind_texture(file):
    image = Image.open(file).convert("RGBA")
    image_data = image.tobytes()
    width, height = image.size

    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    gl.glTexImage2D(
        gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
        gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_data
    )

    return texture_id, width, height

def load_texture(filename):
    with importlib.resources.open_binary(res, filename) as f:
        tex = bind_texture(f)

    return tex


def load_font(filename, font_size):
    path = importlib.resources.files(res).joinpath(filename)
    io = imgui.get_io()
    custom_font = io.fonts.add_font_from_file_ttf(str(path), font_size)

    ViewportManager().imgui.refresh_font_texture()

    return custom_font
