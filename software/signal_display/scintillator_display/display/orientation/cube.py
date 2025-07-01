import numpy as np
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import glGenTextures
from scintillator_display.display.impl_compatibility.vao_vbo import create_vao, draw_vao, update_vbo

from OpenGL.GL import *

from PIL import Image, ImageDraw, ImageFont

class Cube:
    def __init__(self):
        self.data = self.generate_textured_cube_data()
        self.vao, self.vbo = create_vao(self.data, return_vbo=True,
                                        store_normals=True, store_texcoords=True)
                                        #store_normals=True, store_texcoords=False)


        
        # self.img_data = self.generate_img_data("Front")
        # self.texture_id = self.create_texture_from_image(self.img_data)

        self.img_size = (256, 256)
        self.img_data = self.generate_all_images()
    

    def generate_textured_cube_data(self):

        """
        Generates vertices for a 1x1x1 unit cube in a right-handed
        coordinate system where +Z is UP, +X is RIGHT, and +Y is INTO the screen.

        The UVs are configured for correctly oriented, upright text on each face.

        Format per vertex:
        [pos_x, pos_y, pos_z, r, g, b, a, norm_x, norm_y, norm_z, u, v]
        """
        l = 0.5  # half-length of the cube side

        # UV coordinates for a standard quad, mapping a texture correctly
        uv_bl = (0, 0) # Bottom-Left
        uv_br = (1, 0) # Bottom-Right
        uv_tr = (1, 1) # Top-Right
        uv_tl = (0, 1) # Top-Left

        # Placeholder for RGBA color, as requested
        color = (0, 0, 0, 0)

        v1 = (-l,-l,l)
        v2 = (l,-l,l)
        v3 = (-l,l,l)
        v4 = (l,l,l)
        v5 = (-l,-l,-l)
        v6 = (l,-l,-l)
        v7 = (-l,l,-l)
        v8 = (l,l,-l)
        cube_vertices = [
            # == Front Face (normal = vertex pos) ==
            *v5,  *color,  *v5,  *uv_bl,
            *v6,  *color,  *v6,  *uv_br,
            *v2,  *color,  *v2,  *uv_tr,

            *v5,  *color,  *v5,  *uv_bl,
            *v2,  *color,  *v2,  *uv_tr,
            *v1,  *color,  *v1,  *uv_tl,

            # == Back Face ==
            *v8,  *color,  *v8,  *uv_bl,
            *v7,  *color,  *v7,  *uv_br,
            *v3,  *color,  *v3,  *uv_tr,

            *v8,  *color,  *v8,  *uv_bl,
            *v3,  *color,  *v3,  *uv_tr,
            *v4,  *color,  *v4,  *uv_tl,

            # == Left Face ==
            *v7,  *color,  *v7,  *uv_bl,
            *v5,  *color,  *v5,  *uv_br,
            *v1,  *color,  *v1,  *uv_tr,

            *v7,  *color,  *v7,  *uv_bl,
            *v1,  *color,  *v1,  *uv_tr,
            *v3,  *color,  *v3,  *uv_tl,

            # == Right Face ==
            *v6,  *color,  *v6,  *uv_bl,
            *v8,  *color,  *v8,  *uv_br,
            *v4,  *color,  *v4,  *uv_tr,

            *v6,  *color,  *v6,  *uv_bl,
            *v4,  *color,  *v4,  *uv_tr,
            *v2,  *color,  *v2,  *uv_tl,

            # == Top Face ==
            *v1,  *color,  *v1,  *uv_bl,
            *v2,  *color,  *v2,  *uv_br,
            *v4,  *color,  *v4,  *uv_tr,

            *v1,  *color,  *v1,  *uv_bl,
            *v4,  *color,  *v4,  *uv_tr,
            *v3,  *color,  *v3,  *uv_tl,

            # == Bottom Face ==
            *v6,  *color,  *v6,  *uv_bl,
            *v5,  *color,  *v5,  *uv_br,
            *v7,  *color,  *v7,  *uv_tr,

            *v6,  *color,  *v6,  *uv_bl,
            *v7,  *color,  *v7,  *uv_tr,
            *v8,  *color,  *v8,  *uv_tl,
        ]

        return np.array(cube_vertices, dtype=np.float32)


    def generate_img_data(self,text,size):

        #self.size = (1, 1)
        font_size = 64

        #img = Image.new("RGBA", self.size, color = (0, 0, 0, 255))
        img = Image.new("RGBA", size, color = (255,255,255,255))
        draw = ImageDraw.Draw(img)

        try:
            ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", font_size)


        #Centering
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, fill=(0,)*3, font=font)

        # swap to opengl y coords
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # this verifies the image is actually made
        #img.show()


        img_data = img.getdata()
        img_data = np.array(img_data, dtype=np.uint8)


        # img.show()
        #return np.array(img.getdata(), dtype=np.uint8)
        return img_data
    
    def generate_all_images(self):
        text = [
            "Front",
            "Back",
            "Left",
            "Right",
            "Top",
            "Bottom"
        ]
        
        image_data = []
        for t in text:
            image_data.append(self.generate_img_data(t,self.img_size))
        
        return image_data
    
    
    def create_texture_from_image(self,img_data):
        width, height = self.img_size

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



    def draw(self):
        for i, img in enumerate(self.img_data):
            glActiveTexture(GL_TEXTURE0)    
            glBindTexture(GL_TEXTURE_2D, self.create_texture_from_image(img))  

            glBindVertexArray(self.vao)  
            glPointSize(10) 
            glDrawArrays(GL_TRIANGLES, i * 6, 6)   
            glBindVertexArray(0)    

            glBindTexture(GL_TEXTURE_2D, 0)

