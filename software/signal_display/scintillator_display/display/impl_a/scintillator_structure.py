import numpy as np
from OpenGL.GL import GL_TRIANGLES

from scintillator_display.display.impl_compatibility.vao_vbo import create_vao, draw_vao, update_vbo

from scintillator_display.compat.universal_values import MathDisplayValues



class Plane(MathDisplayValues):
    def __init__(self, data_manager, scale=1.0, true_scaler=0.1):

        self.data_manager = data_manager
        self.scale = scale
        self.true_scaler = true_scaler

        self.number_of_layers = self.NUM_SCINTILLATORS_PER_STRUCTURE

        self.square_length = self.SQUARE_LEN * self.true_scaler

        self.interlayer_space = self.SPACE_BETWEEN_SCINTILLATORS * self.true_scaler

        self.structure_gap = self.SPACE_BETWEEN_STRUCTURES * self.true_scaler

        self.thickness = self.SCINTILLATOR_THICKNESS * self.true_scaler
        
        #generate the vertices
        # self.vertices = self.generate_plane_vertices(size=self.scale)
        # self.n = len(self.vertices)
        
        # # Preallocate data buffer for position, color, and normals
        # self.data = np.ones((len(self.vertices), 10), dtype=np.float32)

        # #Set Positions
        # self.data[:, :3] = self.vertices 

        # # #Set colour
        # self.set_colour_default()


        # #Set normals
        # self.data[:, 7:10] = self.vertices  
        
        self.data = self.generate_scintillators()
        self.data_copy = self.data.copy()
        self.n = len(self.data)

        # Build VAO and VBO
        self.vao, self.vbo = create_vao(self.data, return_vbo=True, store_normals=True)

    # def generate_plane_vertices(self,size):
    #     """
    #     Generate vertices for the plane
    #     """

    #     x_i, y_i, z_i = 0, 0, 0

    #     unit = size / 2
        
    #     vertices = []

    #     relative_plate_thickness = self.SCINTILLATOR_THICKNESS * self.true_scaler

    #     relative_layer_gap = self.SPACE_BETWEEN_SCINTILLATORS * self.true_scaler 

    #     middle_gap = self.SPACE_BETWEEN_STRUCTURES * self.true_scaler
    

    #     #Lower plane
    #     for i, layer in enumerate(range(2,2+self.number_of_layers)):
    #         number_of_strips = 2**(layer//2)
    #         strip_length = size / number_of_strips


    #         z1 = z_i - relative_plate_thickness * (i+0) - relative_layer_gap * i
    #         z2 = z_i - relative_plate_thickness * (i+1) - relative_layer_gap * i

    #         for i in range(number_of_strips):
    #             if layer % 2 == 1:   #axis = y
    #                 x1 = x_i-unit       #s
    #                 x2 = x_i+unit      #-s
    #                 y1 = y_i-unit + (i+1) * strip_length       #-s
    #                 y2 = y_i-unit + (i) * strip_length      #s        #-z
                    
    #             else: #axis = x
    #                 x1 = x_i-unit + (i+1) * strip_length       #s
    #                 x2 = x_i-unit + i * strip_length       #-s
    #                 y1 = y_i-unit      #-s
    #                 y2 = y_i+unit    #s

    #             points = self.data_manager.make_points_from_high_low(
    #                 x1, x2, y1, y2, z1, z2)

    #             vertices.extend(self.data_manager.make_prism_triangles(*points, show_top_bottom=True))


    #     #Up plane
    #     for i, layer in enumerate(range(2,2+self.number_of_layers)):
    #         number_of_strips = 2** (layer//2)

    #         strip_length = size / number_of_strips


    #         z1 = z_i + middle_gap + relative_plate_thickness * (i+0) + relative_layer_gap * i
    #         z2 = z_i + middle_gap + relative_plate_thickness * (i+1) + relative_layer_gap * i


    #         for i in range(number_of_strips):
    #             if layer % 2 == 0:   #axis = y
    #                 x1 = x_i-unit       #s
    #                 x2 = x_i+unit      #-s
    #                 y1 = y_i-unit + (i) * strip_length      #s        #-z
    #                 y2 = y_i-unit + (i+1) * strip_length       #-s
                    
    #             else: #axis = x
    #                 x1 = x_i-unit + (i+1) * strip_length       #s
    #                 x2 = x_i-unit + i * strip_length       #-s
    #                 y1 = y_i-unit      #-s
    #                 y2 = y_i+unit    #s
                    

    #             points = self.data_manager.make_points_from_high_low(
    #                 x1, x2, y1, y2, z1, z2)

    #             vertices.extend(self.data_manager.make_prism_triangles(*points, show_top_bottom=True))

    #     vertices = np.array(vertices, dtype = np.float32)

    #     return vertices
    
    # def set_colour(self, pt_selected):
    #     if pt_selected == None:
    #         x_white = -1
    #         y_white = -1
    #         x_grey = -1
    #         y_grey = -1
    #         self.set_colour_default()
    #     else:
    #             cooked_data = pt_selected.scintillator_binary
    #             print(cooked_data)
    #             x_scintillators = cooked_data[0]
    #             y_scintillators = cooked_data[1]
        
    #     #In here 111111 means that all of the positives light up(more towards positive x or y, white)
    #     #000000 means that all of the negative(more towards the negative x or y, grey)

    #     #More towards the positive has a white strip, more towards the negative has a gray strip

    #         #Top
    #             x_white = x_scintillators[3][0] * 4 + x_scintillators[4][0] * 2 + x_scintillators[5][0]
    #             y_white = y_scintillators[3][0] * 4 + y_scintillators[4][0] * 2 + y_scintillators[5][0]
    #             x_grey  = x_scintillators[3][1] * 4 + x_scintillators[4][1] * 2 + x_scintillators[5][1]
    #             y_grey  = y_scintillators[3][1] * 4 + y_scintillators[4][1] * 2 + y_scintillators[5][1]


                    

    #             for layer in range(self.number_of_layers):
    #                 number_of_strips = 2 ** ((layer + 2)//2)    #calculate the number of strips per layer


    #                 for i in range(number_of_strips):
    #                     reverse_number = 2** ((5-layer)//2)    #This means that the binary is read from left to right

    #                     k = 0  #apply offset so when it comes to top, it correctly displays
    #                     for j in range(layer + 1):  #Find the number of the strip we are on. This is counting by 2^x
    #                         if j != 0:
    #                             k += 2**((j+1)//2)

    #                     k = (k + i) * 36    #+i since it is the number of the strip in that layer. 36 is for each prism has 36 vertices

    #                     if layer % 2 == 0:  #x - axis
    #                         if i % 2 == 1:  #white strips
    #                             if x_white & reverse_number != 0 and x_white != -1: #If x in that spot is 1
                                    
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]    #light up
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [1,1,1]    #default colour(white)
    #                         else:   #second strip (grey)
    #                             if x_grey & reverse_number != 0 and x_grey != -1: #If x in that spot is 0
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]    #light up
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]  #default colour: gray
    #                     else:
    #                         if i % 2 == 1:  #white strips
    #                             if y_white & reverse_number != 0 and y_white != -1: 
                                    
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [1,1,1]
    #                         else: 
    #                             if y_grey & reverse_number != 0 and y_grey != -1: 
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]

    #         # bottom

    #             x_white = x_scintillators[2][0] * 4 + x_scintillators[1][0] * 2 + x_scintillators[0][0]
    #             y_white = y_scintillators[2][0] * 4 + y_scintillators[1][0] * 2 + y_scintillators[0][0]
    #             x_grey  = x_scintillators[2][1] * 4 + x_scintillators[1][1] * 2 + x_scintillators[0][1]
    #             y_grey  = y_scintillators[2][1] * 4 + y_scintillators[1][1] * 2 + y_scintillators[0][1]
                    

    #             for layer in range(self.number_of_layers):
    #                 number_of_strips = 2 ** ((layer + 2)//2)    #calculate the number of strips per layer


    #                 for i in range(number_of_strips):
    #                     reverse_number = 2** ((5-layer)//2)    #This means that the binary is read from left to right

    #                     k = 28  #apply offset so when it comes to top, it correctly displays
    #                     for j in range(layer + 1):  #Find the number of the strip we are on. This is counting by 2^x
    #                         if j != 0:
    #                             k += 2**((j+1)//2)

    #                     k = (k + i) * 36    #+i since it is the number of the strip in that layer. 36 is for each prism has 36 vertices

    #                     if layer % 2 == 0:  #y - axis
    #                         if i % 2 == 1:  #white strips
    #                             if y_white & reverse_number != 0 and y_white != -1: #If x in that spot is 1
                                    
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]    #light up
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [1,1,1]    #default colour(white)
    #                         else:   #second strip (grey)
    #                             if y_grey & reverse_number != 0 and y_white != -1: #If x in that spot is 0
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]    #light up
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]  #default colour: gray
    #                     else:   #x-axis
    #                         if i % 2 == 1:  #white strips
    #                             if x_white & reverse_number != 0 and x_white != -1: 
                                    
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [1,1,1]
    #                         else: 
    #                             if x_grey & reverse_number != 0 and x_grey != -1: 
    #                                 self.data[k : k + 36, 3:6] = [1,1,0]
    #                             else: 
    #                                 self.data[k : k + 36, 3:6] = [211/256,211/256,211/256]
    
    # def set_colour_default(self):
    #     for i in range(len(self.vertices)):
    #         if i %2 ==  0 :
    #             self.data[i*36:(i+1)*36,3:7] = [1,1,1,0.5]  #white
    #             #self.data[i*36:(i+1)*36,3:7] = [1,0,0,0.5] 
    #         else:
    #             self.data[i*36:(i+1)*36,3:7] = [211/256,211/256,211/256,0.5]   #gray
    #             #self.data[i*36:(i+1)*36,3:7] = [0,1,0,0.5]





    # def draw(self, pt_selected, show_colour):
    #     """
    #     Draw the planes
    #     """
        
    #     if show_colour:
    #         self.set_colour(pt_selected)
    #     else:
    #         self.set_colour_default()
    #     update_vbo(self.vbo, self.data)
    #     draw_vao(self.vao, GL_TRIANGLES, self.n)


    def generate_layer(self, structure, layer_number, direction, strip_colour):
        """
        generates layer
        :param structure: top or bottom
        :param layer_number: layer nmber(starts from 0)
        :param direction: perpendicular to x or y axis
        :param strip_colour: white or gray
        :return: list of list of vertices
        """

        #The origin is situated at the center of the surface of the bottom structure

        #Gray strip is negative, white is positive

        #Setting values
        
        n_strip = 2 ** (layer_number + 1)
        length = self.square_length / n_strip

        if direction == "x":
            #Since the plates or perpendicular to the x axis, all the values are the same, except x values which would be looped through
            
            x_0 = - self.square_length / 2

            y_i = - self.square_length / 2
            y_f = self.square_length / 2

            if strip_colour == "white":

                x_0 += length

        else:
            #Since the plates or perpendicular to the y axis, all the values are the same, except y values which would be looped through
            y_0 = - self.square_length / 2

            x_i = - self.square_length / 2
            x_f = self.square_length / 2

            if strip_colour == "white":

                y_0 += length

        if structure == "bottom":
            #Bottom structure has x plates on top
            if direction == "x":

                true_layer = 2 * layer_number
            
            else:

                true_layer = 2 * layer_number + 1
            
            z_f = 0 - self.thickness * true_layer - (self.interlayer_space * true_layer)
            z_i = z_f - self.thickness


        else:
            #top structure has x plates on top
            if direction == "x":

                true_layer = 2 * layer_number + 1
            
            else:
                
                true_layer = 2 * layer_number

            z_i = self.structure_gap + self.thickness * true_layer + self.interlayer_space * true_layer

            z_f = z_i + self.thickness

        
        #Verticies

        #This creates prisms from the vertices
        all_prisms = []

        if direction == "x":

            for i in range(n_strip // 2):
                x_i = x_0 + i  * length * 2
                x_f = x_i + length
                all_prisms.extend(self.create_prism(x_i, x_f, y_i, y_f, z_i, z_f, strip_colour))
        else:

            for i in range(n_strip // 2):
                y_i = y_0 + i * length * 2
                y_f = y_i + length
                all_prisms.extend(self.create_prism(x_i, x_f, y_i, y_f, z_i, z_f, strip_colour))


        return all_prisms


    
    def create_prism(self, x_i, x_f, y_i, y_f, z_i, z_f, strip_colour):

        v1 = (x_i, y_i, z_f)
        v2 = (x_f, y_i, z_f)
        v3 = (x_i, y_f, z_f)
        v4 = (x_f, y_f, z_f)
        v5 = (x_i, y_i, z_i)
        v6 = (x_f, y_i, z_i)
        v7 = (x_i, y_f, z_i)
        v8 = (x_f, y_f, z_i)

        if strip_colour == "white":
            color = (255/255, 255/255, 255/255, 0.5) #place holder
        elif strip_colour == "gray":
            color = (211/255, 211/255, 211/255, 0.5)




        cube_vertices = [
            # == Front Face ==
            [*v5,  *color,  *v5],
            [*v6,  *color,  *v6],
            [*v2,  *color,  *v2],

            [*v5,  *color,  *v5],
            [*v2,  *color,  *v2],
            [*v1,  *color,  *v1],

            # == Back Face ==
            [*v8,  *color,  *v8],
            [*v7,  *color,  *v7],
            [*v3,  *color,  *v3],

            [*v8,  *color,  *v8],
            [*v3,  *color,  *v3],
            [*v4,  *color,  *v4],

            # == Left Face ==
            [*v7,  *color,  *v7],
            [*v5,  *color,  *v5],
            [*v1,  *color,  *v1],

            [*v7,  *color,  *v7],
            [*v1,  *color,  *v1],
            [*v3,  *color,  *v3],

            # == Right Face ==
            [*v6,  *color,  *v6],
            [*v8,  *color,  *v8],
            [*v4,  *color,  *v4],

            [*v6,  *color,  *v6],
            [*v4,  *color,  *v4],
            [*v2,  *color,  *v2],

            # == Top Face ==
            [*v1,  *color,  *v1],
            [*v2,  *color,  *v2],
            [*v4,  *color,  *v4],

            [*v1,  *color,  *v1],
            [*v4,  *color,  *v4],
            [*v3,  *color,  *v3],

            # == Bottom Face ==
            [*v7,  *color,  *v6],
            [*v8,  *color,  *v5],
            [*v6,  *color,  *v7],

            [*v7,  *color,  *v6],
            [*v6,  *color,  *v7],
            [*v5,  *color,  *v8],
        ]

        return cube_vertices

    def generate_scintillators(self):

        bottom_layer_number = list(range(self.NUM_SCINTILLATOR_XY_PER_STRUCTURE))
        
        top_layer_number = bottom_layer_number.copy()
        top_layer_number.sort(reverse = True)

        top_layer_number.extend(bottom_layer_number)

        self.layer_numbers = top_layer_number

        self.directions = ["x","y"]
        self.strip_colours = ["white","gray"]

        #First generate the x direction. 
        #generate layers from top to bottom
        #for each layer, first generate the white rods, then the gray ones
        #The order is exactly as Aljoscha's input code
        all_data = []
        for d in self.directions:

            for i, n in enumerate(self.layer_numbers):

                if i <= (self.NUM_SCINTILLATOR_XY_PER_STRUCTURE - 1):
                    st = "top"
                else:
                    st = "bottom"


                for c in self.strip_colours: 

                    all_data.extend(self.generate_layer(st, n, d, c))   

        arr = np.array(all_data, dtype = np.float32)

        return arr

    def set_colour(self, pt_selected):

        #first loop through x, then y
        #Then loop through each layer
        #For each layer, loop through white, then gray

        if pt_selected == None:
            return

        for d in range(len(self.directions)):

            for n in range(len(self.layer_numbers)):

                for c in range(len(self.strip_colours)): 

                    if pt_selected.scintillator_binary[d][n][c] == 1:

                        #basically if d = 0, it is x, no offset needed
                        #if d = 1, it is y, it starts with the number of rods generated from x
                        index = d * 2 * (2 * (1 - 2 ** self.NUM_SCINTILLATOR_XY_PER_STRUCTURE) // (1 - 2)) #sum of geometric series formula

                        #See which layer you are on, and then add all of the previous layers to loop to there
                        for i in range(n):
                            index += 2 ** self.layer_numbers[i] * 2
                        
                        #If it is white, no offset needed(c = 0)
                        #If it is gray, offset by the number of white rods in the layer(c = 1)
                        index += c *  2 ** self.layer_numbers[n]

                        #Tiems 36 because each prisim consists of 36 triangles
                        index *= 36

                        #Calculate the number of rods of the same colour to be set to yellow
                        n_vertices = 2 ** self.layer_numbers[n] * 36

                        #change it to yellow
                        self.data[index:(index + n_vertices), 3:6] = 255/255, 255/255, 0/255

    def set_colour_default(self):
        self.data = self.data_copy.copy()

    def draw(self, pt_selected, show_colour):
        """
        Draw the planes
        """
        self.set_colour_default()

        if show_colour:
            self.set_colour(pt_selected)

        #draw
        update_vbo(self.vbo, self.data)
        draw_vao(self.vao, GL_TRIANGLES, self.n)

        
                        

                            


        