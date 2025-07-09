# import imgui
# from imgui.integrations.glfw import GlfwRenderer

import software.signal_display.scintillator_display.compat.imgui as imgui
from software.signal_display.scintillator_display.compat.imgui.integrations.glfw import GlfwRenderer


import software.signal_display.scintillator_display.display.impl_a.graphics as graphics


def ui_spacing():
    """
    Creates a blank space in the user interface
    """

    for _ in range(5):
        imgui.spacing()


def ui_section(section_name, top_margin=True):
    """
    Decorator constructor to wrap a user interface
    section with a title: reduce the repetition
    of creating a separation for every section
    """

    # constructed decorator
    def decorator(func):
        # wrap the method, building the title
        # of the section first, before drawing
        # the rest of the section

        def wrapper(*args, **kwargs):
            if top_margin:
                ui_spacing()

            # display section title
            imgui.text(section_name)
            imgui.separator()

            # draw the rest of the section
            func(*args, **kwargs)

        return wrapper

    return decorator


class ParameterInterface:
    def __init__(
        self,
        window,
    ):
        """
        Parameter Interface: Manages the state of the parameters
        controlled by the user, and draws the interface

        :param window: glfw window
        :param on_evaluate: Callback for a new user function's evaluation call
        :param on_change_ball_color: Callback to change ball color
        :param on_change_surface_color: Callback to change surface color
        """

        # create DearImGui instance for ui drawing
        imgui.create_context()

        # create bindings to Glfw rendering backend
        # the application manages its own callbacks
        self._imgui_impl = GlfwRenderer(window, attach_callbacks=False)



        # camera data
        self.camera = graphics.orbit_controls.CameraOrbitControls()

        self.light_color = [1.0, 1.0, 1.0]
        self.background_color = [0.86, 0.87, 0.87]

        self.ambient_strength = 0.2
        self.diffuse_strength = 0.2
        self.diffuse_base = 0.3
        self.specular_strength = 0.1
        self.specular_reflection = 16.0

        self.input_data = []



        self.show_axes = True
        #self.latest = True
        self.latest = False

        self.pt_selected = None

        self.dataset_active = []
        for i in range(len(self.input_data)):
            self.dataset_active.append(False)







    @property
    def want_keyboard(self):
        return imgui.get_io().want_capture_keyboard

    @property
    def want_mouse(self):
        return imgui.get_io().want_capture_mouse

    @property
    def impl(self):
        return self._imgui_impl
    
    
    @ui_section("Status", top_margin=False)
    def status(self):
        """
        show xyz axis, show latest
        """
        
        _, self.show_axes = imgui.checkbox("show xy axes", self.show_axes)
        imgui.text("x-axis: red, y-axis: green, z-axis:blue")


        _, self.latest = imgui.checkbox("Only show last data", self.latest)

        if self.latest and self.dataset_active != []:
            self.dataset_active = []
            for i in range(len(self.input_data)):
                self.dataset_active.append(False)

            self.dataset_active[-1] = True



    @ui_section("Point data")
    def point_data(self):
        """
        Data about the point
        """
        if self.pt_selected == None:
            imgui.text(f"No data point selected")

        else:
            for i in range(len(self.dataset_active)):
                #To prevent the selected point of previous data set which is no longer showing
                if self.pt_selected in self.input_data[i] and not self.dataset_active[i]:
                    self.pt_selected = None   #This thing tells app.py to change back the pt_selected 
                    imgui.text(f"No data point selected")
                    return 


            imgui.text(f"{self.pt_selected[3]}")
            imgui.text(f"Coordinates: ({self.pt_selected[0]})")
            imgui.text(f"Coordinates in Binary:{self.pt_selected[1]}")
            imgui.text(f"Binary:{self.pt_selected[2]}")

            double = False
            #for xylist in self.pt_selected[2]:
            for xylist in self.pt_selected[1]:
                for pair in xylist:
                    if pair == (1,1):
                        double = True
            if double:
                imgui.text(f"Note: the data point contains coordinate(s) (1,1), the calculations of the trajectory may be inaccurate")
            

        


    @ui_section("Tests")
    def tests(self):
        """
        Options to select which datasets are chosen
        """
        for i in range(len(self.input_data)):
            _, self.dataset_active[i] = imgui.checkbox(f"Datatest {i + 1}: {self.input_data[i][3]}", self.dataset_active[i])

        


    def update_variables(self):
        """
        Update the variables every loop
        """
        for i in range(len(self.input_data)-len(self.dataset_active)):
            self.dataset_active.append(False)

        for i in range(len(self.dataset_active)):
            if self.dataset_active[i]:
                self.pt_selected = self.input_data[i]


    def on_render_ui(self,window,pt_selected):
        """
        Renders full user interface on frame
        """

        self.pt_selected = pt_selected

        imgui.new_frame()
        imgui.begin("Code 'borrowed' from Joule")

        self.update_variables()
        self.status()
        self.point_data()
        self.tests()


        imgui.end()
        imgui.render()
