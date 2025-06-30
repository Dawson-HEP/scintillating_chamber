from OpenGL.GL import *





def create_vao(
                data,
                n_per_vertice=3,
                n_per_colour=4,
                n_per_normal=3,
                n_per_tex=2,
                return_vbo=False,
                store_normals=False,
                store_texcoords=False,
                ):

    len_ptr = n_per_vertice + n_per_colour + (n_per_normal if store_normals else 0) 
    len_ptr = n_per_vertice + n_per_colour + (n_per_normal if store_normals else 0) + (n_per_tex if store_texcoords else 0) 
    stride = len_ptr * data.itemsize    

    vao = glGenVertexArrays(1)  
    glBindVertexArray(vao)  

    vbo = glGenBuffers(1)   
    glBindBuffer(GL_ARRAY_BUFFER, vbo)  
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)   

    glEnableVertexAttribArray(0)    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0)) 
    glVertexAttribPointer(0, n_per_vertice, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0)) 

    c_offset = n_per_vertice * data.itemsize    
    glEnableVertexAttribArray(1)    
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(c_offset))  
    glVertexAttribPointer(1, n_per_colour, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(c_offset))   

    if store_normals:   
        n_offset = (n_per_vertice + n_per_colour) * data.itemsize   
        glEnableVertexAttribArray(2)    
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(n_offset))  
        glVertexAttribPointer(2, n_per_normal, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(n_offset)) 

    # UV (optional) 
    if store_texcoords: 
        t_offset = (n_per_vertice + n_per_colour + n_per_normal) * data.itemsize    
        glEnableVertexAttribArray(3)    
        glVertexAttribPointer(3, n_per_tex, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(t_offset))  

    glBindVertexArray(0)    
    glBindBuffer(GL_ARRAY_BUFFER, 0)   

    if return_vbo:  
        return vao, vbo 
    
    return vao  

def update_vbo(vbo, data):   
    glBindBuffer(GL_ARRAY_BUFFER, vbo)  
    glBufferSubData(GL_ARRAY_BUFFER, 0, data.nbytes, data)  
    glBindBuffer(GL_ARRAY_BUFFER, 0)    

def draw_vao(vao, draw_type, n, texture=None):       
    if texture: 
        glActiveTexture(GL_TEXTURE0)    
        glBindTexture(GL_TEXTURE_2D, texture)  

    glBindVertexArray(vao)  
    glPointSize(10) 
    glDrawArrays(draw_type, 0, n)   
    glBindVertexArray(0)    

    glBindTexture(GL_TEXTURE_2D, 0)