import numpy as np
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import glGenTextures
from scintillator_display.display.impl_compatibility.vao_vbo import create_vao, draw_vao, update_vbo

from OpenGL.GL import *

from PIL import Image, ImageDraw, ImageFont

class Cube:
    def __init__(self):
        self.data = self.generate_vertices()
        self.vao, self.vbo = create_vao(self.data, return_vbo=True,
                                        store_normals=True, store_texcoords=True)
                                        #store_normals=True, store_texcoords=False)


    
        self.img_data = self.generate_img_data("Front")
        self.texture_id = self.create_texture_from_image(self.img_data)


    def generate_img_data(self,text):
        self.size = (256, 256)
        #self.size = (1, 1)
        font_size = 32
        font_size = 64

        img = Image.new("RGBA", self.size, color = (0, 0, 0, 255))
        #img = Image.new("RGBA", self.size, color = (0,0,0,240))
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("arial.ttf", font_size)
        #font = ImageFont.load_default()

        #Centering
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(((self.size[0] - w) / 2, (self.size[1] - h) / 2), text, fill=(255,)*3, font=font)

        # swap to opengl y coords
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # this verifies the image is actually made
        #img.show()


        img_data = img.getdata()
        img_data = np.array(img_data, dtype=np.uint8)


        # img.show()
        #return np.array(img.getdata(), dtype=np.uint8)
        return img_data
    
    def create_texture_from_image(self,img_data):
        width, height = self.size

        tex_id = glGenTextures(1)                        # Generate a new texture ID
        glBindTexture(GL_TEXTURE_2D, tex_id)             # Bind it as a 2D texture


        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_MIRRORED_REPEAT)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        ## Set texture parameters
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # Upload the image to the GPU
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        
        return tex_id

    def generate_vertices(self):

        
        v1 = np.array([ 0.5,  0.5, 0.0,   1.0, 0.0, 0.0, 1,   0, 0, 1,   1.0, 1.0]) # top right
        v2 = np.array([ 0.5, -0.5, 0.0,   0.0, 1.0, 0.0, 1,   0, 0, 1,   1.0, 0.0]) # bottom right
        v3 = np.array([-0.5, -0.5, 0.0,   0.0, 0.0, 1.0, 1,   0, 0, 1,   0.0, 0.0]) # bottom left
        v4 = np.array([-0.5,  0.5, 0.0,   1.0, 1.0, 0.0, 1,   0, 0, 1,   0.0, 1.0]) # top left 
        
        #t1 = [v1, v2, v3]
        #t2 = [v2, v3, v4]

        ts = np.array([v1, v2, v3, v1, v3, v4], dtype=np.float32)
        #ts = np.array([v2, v3, v4], dtype=np.float32)
        return ts

    def draw(self):
        draw_vao(self.vao, GL_TRIANGLES, self.data.shape[0], texture=self.texture_id)