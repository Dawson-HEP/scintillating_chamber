import numpy as np
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import glGenTextures
from scintillator_display.display.orientation.shader.vao_vbo import create_vao, draw_vao, update_vbo

from OpenGL.GL import *

from PIL import Image, ImageDraw, ImageFont

class Cube:
    def __init__(self):
        self.data = self.generate_vertices()

    
        self.img_data = self.generate_text("Front")
        self.texture_id = self.create_texture_from_image(self.img_data)

        self.vao, self.vbo = create_vao(self.data, return_vbo=True, store_normals=True, store_uvs = True)

    def generate_text(self,text):
        self.size = (256, 256)
        font_size = 32

        img = Image.new("RGBA", self.size, color = (255,255,255,240))
        draw = ImageDraw.Draw(img)

        #font = ImageFont.truetype("arial.ttf", font_size)
        font = ImageFont.load_default()

        #Centering
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(((self.size[0] - w) / 2, (self.size[1] - h) / 2), text, fill=(0, 0, 0), font=font)

        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # img.show()
        return np.array(img.getdata(), dtype=np.uint8)
    
    def create_texture_from_image(self,img_data):
        width, height = self.size
        tex_id = glGenTextures(1)                        # Generate a new texture ID
        glBindTexture(GL_TEXTURE_2D, tex_id)             # Bind it as a 2D texture


        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # Upload the image to the GPU
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            width, height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, img_data
        )

        return tex_id

    def generate_vertices(self):
        face_vertices = np.array([
            #  pos         color         normal       uv
            -1, -1, 0,   1,1,1,1,      0,0,1,     0,0,
            1, -1, 0,   1,1,1,1,      0,0,1,     1,0,
            1,  1, 0,   1,1,1,1,      0,0,1,     1,1,

            -1, -1, 0,   1,1,1,1,      0,0,1,     0,0,
            1,  1, 0,   1,1,1,1,      0,0,1,     1,1,
            -1,  1, 0,   1,1,1,1,      0,0,1,     0,1,
        ], dtype=np.float32)

        return face_vertices


    # def generate_cube(self):
    #     s = 0.5  # half-size of the cube
    #     # Define 6 faces, 2 triangles per face, 3 vertices per triangle
    #     faces = [
    #         # front
    #         [[-s, -s,  s], [ s, -s,  s], [ s,  s,  s],
    #          [-s, -s,  s], [ s,  s,  s], [-s,  s,  s]],

    #         # back
    #         [[ s, -s, -s], [-s, -s, -s], [-s,  s, -s],
    #          [ s, -s, -s], [-s,  s, -s], [ s,  s, -s]],

    #         # left
    #         [[-s, -s, -s], [-s, -s,  s], [-s,  s,  s],
    #          [-s, -s, -s], [-s,  s,  s], [-s,  s, -s]],

    #         # right
    #         [[ s, -s,  s], [ s, -s, -s], [ s,  s, -s],
    #          [ s, -s,  s], [ s,  s, -s], [ s,  s,  s]],

    #         # top
    #         [[-s,  s,  s], [ s,  s,  s], [ s,  s, -s],
    #          [-s,  s,  s], [ s,  s, -s], [-s,  s, -s]],

    #         # bottom
    #         [[-s, -s, -s], [ s, -s, -s], [ s, -s,  s],
    #          [-s, -s, -s], [ s, -s,  s], [-s, -s,  s]],
    #     ]

    #     return np.array([v for face in faces for v in face], dtype=np.float32)

    # def draw(self):
    #     update_vbo(self.vbo, self.data)
    #     draw_vao(self.vao, GL_TRIANGLES, self.n)

    def draw(self,shader_program):
        # glUseProgram(shader_program)
        # Bind the texture
        texture_location = glGetUniformLocation(shader_program, "tex")
        glUniform1i(texture_location, 0)  # Use texture unit 0
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        # Bind the VAO
        glBindVertexArray(self.vao)

        # Draw the face
        glDrawArrays(GL_TRIANGLES, 0, 6)

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)