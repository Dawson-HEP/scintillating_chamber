import numpy as np
from OpenGL.GL import GL_TRIANGLES

from software.signal_display.scintillator_display.display.impl_compatibility.vao_vbo import create_vao, draw_vao, update_vbo

from software.signal_display.scintillator_display.compat.universal_values import MathDisplayValues



class Plane(MathDisplayValues):
    def __init__(self, data_manager, scale=1.0, true_scaler=0.1):

        self.data_manager = data_manager
        self.scale = scale
        self.true_scaler = true_scaler

        self.number_of_layers = self.NUM_SCINTILLATORS_PER_STRUCTURE
        
        #generate the vertices
        self.vertices = self.generate_plane_vertices(size=self.scale)
        self.n = len(self.vertices)
        
        # Preallocate data buffer for position, color, and normals
        self.data = np.ones((len(self.vertices), 10), dtype=np.float32)

        #Set Positions
        self.data[:, :3] = self.vertices 

        # #Set colour
        self.set_colour_default()


        #Set normals
        self.data[:, 7:10] = self.vertices  
        
        # Build VAO and VBO
        self.vao, self.vbo = create_vao(self.data, return_vbo=True, store_normals=True)

    def generate_plane_vertices(self,size):
        """
        Generate vertices for the plane
        """

        x_i, y_i, z_i = 0, 0, 0

        unit = size / 2
        
        vertices = []

        relative_plate_thickness = self.SCINTILLATOR_THICKNESS * self.true_scaler

        relative_layer_gap = self.SPACE_BETWEEN_SCINTILLATORS * self.true_scaler 

        middle_gap = self.SPACE_BETWEEN_STRUCTURES * self.true_scaler
    

        #Lower plane
        for i, layer in enumerate(range(2,2+self.number_of_layers)):
            number_of_strips = 2**(layer//2)
            strip_length = size / number_of_strips


            z1 = z_i - relative_plate_thickness * (i+0) - relative_layer_gap * i
            z2 = z_i - relative_plate_thickness * (i+1) - relative_layer_gap * i

            for i in range(number_of_strips):
                if layer % 2 == 1:   #axis = y
                    x1 = x_i-unit       #s
                    x2 = x_i+unit      #-s
                    y1 = y_i-unit + (i+1) * strip_length       #-s
                    y2 = y_i-unit + (i) * strip_length      #s        #-z
                    
                else: #axis = x
                    x1 = x_i-unit + (i+1) * strip_length       #s
                    x2 = x_i-unit + i * strip_length       #-s
                    y1 = y_i-unit      #-s
                    y2 = y_i+unit    #s

                points = self.data_manager.make_points_from_high_low(
                    x1, x2, y1, y2, z1, z2)

                vertices.extend(self.data_manager.make_prism_triangles(*points, show_top_bottom=True))


        #Up plane
        for i, layer in enumerate(range(2,2+self.number_of_layers)):
            number_of_strips = 2** (layer//2)

            strip_length = size / number_of_strips


            z1 = z_i + middle_gap + relative_plate_thickness * (i+0) + relative_layer_gap * i
            z2 = z_i + middle_gap + relative_plate_thickness * (i+1) + relative_layer_gap * i


            for i in range(number_of_strips):
                if layer % 2 == 0:   #axis = y
                    x1 = x_i-unit       #s
                    x2 = x_i+unit      #-s
                    y1 = y_i-unit + (i) * strip_length      #s        #-z
                    y2 = y_i-unit + (i+1) * strip_length       #-s
                    
                else: #axis = x
                    x1 = x_i-unit + (i+1) * strip_length       #s
                    x2 = x_i-unit + i * strip_length       #-s
                    y1 = y_i-unit      #-s
                    y2 = y_i+unit    #s
                    

                points = self.data_manager.make_points_from_high_low(
                    x1, x2, y1, y2, z1, z2)

                vertices.extend(self.data_manager.make_prism_triangles(*points, show_top_bottom=True))

        vertices = np.array(vertices, dtype = np.float32)

        return vertices
    
    def set_colour(self, pt_selected):
        if pt_selected == None:
            x_white = -1
            y_white = -1
            x_grey = -1
            y_grey = -1
            self.set_colour_default()
        else:
                cooked_data = pt_selected.scintillator_binary
                x_scintillators = cooked_data[0]
                y_scintillators = cooked_data[1]
        
        #In here 111111 means that all of the positives light up(more towards positive x or y, white)
        #000000 means that all of the negative(more towards the negative x or y, grey)

        #More towards the positive has a white strip, more towards the negative has a gray strip

            #Top
                x_white = x_scintillators[3][0] * 4 + x_scintillators[4][0] * 2 + x_scintillators[5][0]
                y_white = y_scintillators[3][0] * 4 + y_scintillators[4][0] * 2 + y_scintillators[5][0]
                x_grey  = x_scintillators[3][1] * 4 + x_scintillators[4][1] * 2 + x_scintillators[5][1]
                y_grey  = y_scintillators[3][1] * 4 + y_scintillators[4][1] * 2 + y_scintillators[5][1]


                    

                for layer in range(self.number_of_layers):
                    number_of_strips = 2 ** ((layer + 2)//2)    #calculate the number of strips per layer


                    for i in range(number_of_strips):
                        reverse_number = 2** ((5-layer)//2)    #This means that the binary is read from left to right

                        k = 0  #apply offset so when it comes to top, it correctly displays
                        for j in range(layer + 1):  #Find the number of the strip we are on. This is counting by 2^x
                            if j != 0:
                                k += 2**((j+1)//2)

                        k = (k + i) * 36    #+i since it is the number of the strip in that layer. 36 is for each prism has 36 vertices

                        if layer % 2 == 0:  #x - axis
                            if i % 2 == 1:  #white strips
                                if x_white & reverse_number != 0 and x_white != -1: #If x in that spot is 1
                                    
                                    self.data[k : k + 36, 3:6] = [1,1,0]    #light up
                                else: 
                                    self.data[k : k + 36, 3:6] = [1,1,1]    #default colour(white)
                            else:   #second strip (grey)
                                if x_grey & reverse_number != 0 and x_grey != -1: #If x in that spot is 0
                                    self.data[k : k + 36, 3:6] = [1,1,0]    #light up
                                else: 
                                    self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]  #default colour: gray
                        else:
                            if i % 2 == 1:  #white strips
                                if y_white & reverse_number != 0 and y_white != -1: 
                                    
                                    self.data[k : k + 36, 3:6] = [1,1,0]
                                else: 
                                    self.data[k : k + 36, 3:6] = [1,1,1]
                            else: 
                                if y_grey & reverse_number != 0 and y_grey != -1: 
                                    self.data[k : k + 36, 3:6] = [1,1,0]
                                else: 
                                    self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]

            # bottom

                x_white = x_scintillators[2][0] * 4 + x_scintillators[1][0] * 2 + x_scintillators[0][0]
                y_white = y_scintillators[2][0] * 4 + y_scintillators[1][0] * 2 + y_scintillators[0][0]
                x_grey  = x_scintillators[2][1] * 4 + x_scintillators[1][1] * 2 + x_scintillators[0][1]
                y_grey  = y_scintillators[2][1] * 4 + y_scintillators[1][1] * 2 + y_scintillators[0][1]
                    

                for layer in range(self.number_of_layers):
                    number_of_strips = 2 ** ((layer + 2)//2)    #calculate the number of strips per layer


                    for i in range(number_of_strips):
                        reverse_number = 2** ((5-layer)//2)    #This means that the binary is read from left to right

                        k = 28  #apply offset so when it comes to top, it correctly displays
                        for j in range(layer + 1):  #Find the number of the strip we are on. This is counting by 2^x
                            if j != 0:
                                k += 2**((j+1)//2)

                        k = (k + i) * 36    #+i since it is the number of the strip in that layer. 36 is for each prism has 36 vertices

                        if layer % 2 == 0:  #y - axis
                            if i % 2 == 1:  #white strips
                                if y_white & reverse_number != 0 and y_white != -1: #If x in that spot is 1
                                    
                                    self.data[k : k + 36, 3:6] = [1,1,0]    #light up
                                else: 
                                    self.data[k : k + 36, 3:6] = [1,1,1]    #default colour(white)
                            else:   #second strip (grey)
                                if y_grey & reverse_number != 0 and y_white != -1: #If x in that spot is 0
                                    self.data[k : k + 36, 3:6] = [1,1,0]    #light up
                                else: 
                                    self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]  #default colour: gray
                        else:   #x-axis
                            if i % 2 == 1:  #white strips
                                if x_white & reverse_number != 0 and x_white != -1: 
                                    
                                    self.data[k : k + 36, 3:6] = [1,1,0]
                                else: 
                                    self.data[k : k + 36, 3:6] = [1,1,1]
                            else: 
                                if x_grey & reverse_number != 0 and x_grey != -1: 
                                    self.data[k : k + 36, 3:6] = [1,1,0]
                                else: 
                                    self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]
    
    def set_colour_default(self):
        for i in range(len(self.vertices)):
            if i %2 ==  0 :
                self.data[i*36:(i+1)*36,3:7] = [1,1,1,0.5]  #white
                #self.data[i*36:(i+1)*36,3:7] = [1,0,0,0.5] 
            else:
                self.data[i*36:(i+1)*36,3:7] = [211/256,211/256,211/256,0.5]   #gray
                #self.data[i*36:(i+1)*36,3:7] = [0,1,0,0.5]





    def draw(self, pt_selected, show_colour):
        """
        Draw the planes
        """
        
        if show_colour:
            self.set_colour(pt_selected)
        else:
            self.set_colour_default()
        update_vbo(self.vbo, self.data)
        draw_vao(self.vao, GL_TRIANGLES, self.n)