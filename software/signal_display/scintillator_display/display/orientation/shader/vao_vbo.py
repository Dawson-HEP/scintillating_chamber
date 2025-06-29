from OpenGL.GL import *


def create_vao(
        data,
        n_per_vertice=3,
        n_per_colour=4,
        n_per_normal=3,
        n_per_uv=2,
        return_vbo=False,
        store_normals=False,
        store_uvs=False,
    ):

    len_ptr = n_per_vertice + n_per_colour
    if store_normals:
        len_ptr += n_per_normal
    if store_uvs:
        len_ptr += n_per_uv

    stride = len_ptr * data.itemsize

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)

    # Position
    offset = 0
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, n_per_vertice, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
    offset += n_per_vertice * data.itemsize

    # Color
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, n_per_colour, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
    offset += n_per_colour * data.itemsize

    # Normal (optional)
    if store_normals:
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, n_per_normal, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        offset += n_per_normal * data.itemsize

    # UV (optional)
    if store_uvs:
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, n_per_uv, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        offset += n_per_uv * data.itemsize

    # Cleanup
    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    if return_vbo:
        return vao, vbo

    return vao



def update_vbo(vbo, data):
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, data.nbytes, data)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


def draw_vao(vao, draw_type, n):
    glBindVertexArray(vao)
    glPointSize(10)
    glDrawArrays(draw_type, 0, n)
    glBindVertexArray(0)
