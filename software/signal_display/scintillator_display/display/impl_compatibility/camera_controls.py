import numpy as np

from scintillator_display.compat.universal_values import MathDisplayValues

class CameraControls(MathDisplayValues):
    def __init__(self,
                 angle_sensitivity=0.001,
                 zoom=50,
                 clear_colour=(0.5,)*3,
                 offset=np.array([0,0,0])):
        
        self.zero_offset = offset


        self.right_handed = np.array([
            [1,0,0,0],
            [0,0,1,0],
            [0,1,0,0],
            [0,0,0,1],
        ])
        
        
        self.set_initial_camera_values(angle_sensitivity, zoom, clear_colour)

    def set_initial_camera_values(self, angle_sensitivity, zoom, clear_colour):

        self.pan_sensitivity   = 0.001
        self.angle_sensitivity = angle_sensitivity

        self.pan_x, self.pan_y, self.pan_z = 0, 0, 0
        self.angle_x, self.angle_y, self.angle_z = 0, 0, 0
        self.zoom = zoom

        self.mouse_dragging = False
        self.panning, self.angling = False, False
        self.last_x, self.last_y = 0,0

        self.width, self.height = 1924, 1080
        self.aspect_ratio = self.width/self.height
        self.render_distance = 512

        self.view_vec = (0, 0, 32, 1)

        self.clear_colour = clear_colour

        self.light_color = (1, 1, 1)

        self.ambient_strength = 0.2
        self.diffuse_strength = 0.2
        self.diffuse_base = 0.3
        self.specular_strength = 0.1
        self.specular_reflection = 16.0




    
    def translate(self, x, y, z):

        translation = np.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]])
        
        return translation
    
    def rotate(self, r):

        rrx, rry, rrz = np.radians(r[0]), np.radians(r[1]), np.radians(r[2])
        
        rot_x = np.array([
            [1,            0,           0, 0],
            [0,  np.cos(rrx), np.sin(rrx), 0],
            [0, -np.sin(rrx), np.cos(rrx), 0],
            [0,            0,           0, 1]])

        rot_y = np.array([
            [np.cos(rry), 0, -np.sin(rry), 0],
            [          0, 1,            0, 0],
            [np.sin(rry), 0,  np.cos(rry), 0],
            [          0, 0,            0, 1]])

        rot_z = np.array([
            [np.cos(rrz), -np.sin(rrz), 0, 0],
            [np.sin(rrz),  np.cos(rrz), 0, 0],
            [          0,            0, 1, 0],
            [          0,            0, 0, 1],])

        
        return rot_x @ rot_y @ rot_z
    
    
        

    
    def rotate_around_p(self, p=(0,0,0), r=(0,0,0)):

        # p in form (x_offset, y_offset, z_offset)
        # NOTE : for some reason, y and z switch in calculations
        # thus, p gets deconstructed as :
        px, pz, py = p

        #re_translate =   self.translate(px, py, pz) @ self.right_handed
        #anti_translate = self.translate(-px, -py, -pz) @ self.right_handed

        return_to_pos =   self.translate(px, py, pz)
        translate_to_zero = self.translate(-px, -py, -pz)

        rotate = self.rotate(r)

        k = return_to_pos @ rotate @ translate_to_zero

        return k


    def get_orthographic_projection(self):
        
        (l, r, b, t, n, f) = (-self.aspect_ratio * self.zoom,
                               self.aspect_ratio * self.zoom,
                              -self.zoom,
                               self.zoom,
                              -self.render_distance,
                               self.render_distance)
        orthographic_projection = np.array([
            [2/(r-l), 0, 0, 0],
            [0, 2/(t-b), 0, 0],
            [0, 0, 2/(f-n), 0],
            [-(r+l)/(r-l), -(t+b)/(t-b), -(f+n)/(f-n), 1],
        ])

        return orthographic_projection

    def get_camera_tranform(self, is_orientation):
        

        if not is_orientation:    
            camera_pan = self.translate(self.pan_x, self.pan_y, self.pan_z)
            camera_rotation = self.rotate_around_p(p=self.zero_offset, r=(self.angle_x, self.angle_y, self.angle_z))
        else:
            camera_pan = self.translate(0, 0, 0)
            camera_rotation = self.rotate_around_p(p=(0,0,self.zero_offset[-1]), r=(self.angle_x, self.angle_y, self.angle_z))

        return camera_pan @ camera_rotation

    def get_world_transform(self):
        world_transform = self.right_handed
        return world_transform