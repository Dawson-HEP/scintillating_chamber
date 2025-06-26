import scintillator_display.compat.glfw as glfw
import scintillator_display.compat.imgui as imgui

from OpenGL.GL import glClearColor, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

from .load_res import load_texture, load_font

import time

import numpy as np

from scintillator_display.display.impl_compatibility.data_manager import DataPoint


class Controls:
    def __init__(self, impl_a, impl_b, vm, x_ratio=(0, 1, 5), y_ratio=(0, 1, 1)):

        self.x_ratio, self.y_ratio = x_ratio, y_ratio

        self.vm = vm

        self.activate_data_connection(impl_a, impl_b)

        self.width, self.height = 0, 0

        self.show_only_last_data_a = True
        self.show_only_last_data_b = True
        self.open_state = False

        # ffmpeg -i sc_bw.png -vf "scale=-1:48" hep_48.png
        self.hep = load_texture("hep_48.png")
        # ffmpeg -i sc_bw.png -vf "scale=-1:64" sc_64.png
        self.sc = load_texture("sc_64.png")

        self.font = load_font("Poppins-Regular.ttf", 24)

        self.current = time.time()
        self.dt = 0


        initial_state = {
            'data':0,
            'debug':1,
            'demo':2,
        }
        self.drop_downs = [
            ['##m2', initial_state[self.impl_a.data_manager.mode], self.impl_a],
            ['##m3', initial_state[self.impl_b.data_manager.mode], self.impl_b],
        ]
        self.xyz_axes = [
            ['##xyz1', not self.show_a_axes, self.impl_a], # "not" needed to begin on show
            ['##xyz2', not self.show_b_axes, self.impl_b], # "not" needed to begin on show
        ]
        self.data_shown = [
            ['##state1', 0, 'newest'],
            ['##state2', 0, 'newest'],
        ]
        self.colours_shown = [
            ['##cl1', 0, False],
            ['##cl2', 1, True]
        ]
        self.checked_data = [self.impl_a_checked, self.impl_b_checked]
        self.point_info = [self.data_points_a, self.data_points_b]

        self.impls = [self.impl_a, self.impl_b]


    def null(self, *args):
        pass
    
    def viewport_shenanigans(self, vm):
        vp_c = vm.add_viewport(None, None)

        vp_c.on_render = self.on_render

        vp_c.window_size_callback = self.window_size_callback

        vp_c.x_ratio, vp_c.y_ratio = self.x_ratio, self.y_ratio

    def window_size_callback(self, window, width, height):
        self.width = width# if width > 256 else 256
        self.height = height

    def activate_data_connection(self, impl_a, impl_b):
        self.impl_a, self.impl_b = impl_a, impl_b
        self.data_points_a  = self.impl_a.data_manager.data
        self.data_points_b  = self.impl_b.data_manager.data
        self.impl_a_checked = self.impl_a.data_manager.impl_data_is_checked
        self.impl_b_checked = self.impl_b.data_manager.impl_data_is_checked

        self.mode_a = self.impl_a.data_manager.mode
        self.mode_b = self.impl_b.data_manager.mode

        self.show_a_axes = self.impl_a.show_axes
        self.show_b_axes = self.impl_b.show_axes
    
    def space_lines(self, n=1):
        for i in range(n):
            imgui.spacing()

    def on_render(self, paused):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        imgui.set_next_window_position(0, 0, condition=imgui.ONCE)
        imgui.set_next_window_size(self.width, self.height, condition=imgui.ALWAYS)
        imgui.begin(
            " ",
            flags=imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_COLLAPSE
            | imgui.WINDOW_HORIZONTAL_SCROLLING_BAR
            | imgui.TABLE_COLUMN_NO_CLIP # FIX SIZE SO IT IS ALWAYS SAME
            | imgui.TABLE_NO_CLIP # FIX SIZE SO IT IS ALWAYS SAME
        )

        imgui.separator()

        imgui.push_font(self.font)
        imgui.text("The Scintillating Chamber")
        imgui.pop_font()

        imgui.separator()

        imgui.image(*self.hep)
        imgui.same_line()
        imgui.image(*self.sc)

        imgui.separator()

        self.space_lines(2)
        fps = 1/self.dt if self.dt != 0 else 0
        imgui.text(f'{fps:.1f} fps')
        pause_text = 'paused' if paused else 'not paused'
        clicked = imgui.button(f'{pause_text}')
        if clicked:
            self.vm.paused = not paused

        #expanded, _ = imgui.collapsing_header("view window info", True)
        #if expanded:
        #    imgui.text("2")


        self.space_lines(4)



        self.space_lines(4)


        def set_static_choices(row, column):
            impl_boxes = ["    ", "impl a        ", "impl_b        "]
            modes = ['data', 'debug', 'demo']
            xyz = ['show', 'hide']
            #xyz = ['hide', 'show']
            xy2 = [False, True]
            #xy2 = [True, False]
            data_shown_types = ['newest', 'any', 'none', 'middle']
            colours = ['on', 'off']
            

            if row==0:
                imgui.text(impl_boxes[column])
                pass

            elif row==1:
                if column==0:
                    pass
                    imgui.text("mode")
                else:
                    column-=1

                    initial_mode = modes[self.drop_downs[column][1]]


                    clicked, self.drop_downs[column][1] = imgui.combo(
                        self.drop_downs[column][0], self.drop_downs[column][1], modes)
                    self.drop_downs[column][2].data_manager.mode = modes[self.drop_downs[column][1]]

                    new_mode = modes[self.drop_downs[column][1]]

                    if initial_mode != new_mode:
                        self.drop_downs[column][2].data_manager.reset_data_checks()
                        self.checked_data[column] = self.drop_downs[column][2].data_manager.impl_data_is_checked
                        self.point_info[column] = self.drop_downs[column][2].data_manager.data

            elif row==2:
                if column==0:
                    imgui.text("xyz")
                else:
                    column-=1
                    clicked, self.xyz_axes[column][1] = imgui.combo(
                        self.xyz_axes[column][0], self.xyz_axes[column][1], xyz)
                    self.xyz_axes[column][2].show_axes = not xy2[self.xyz_axes[column][1]]

            elif row==3:
                if column==0:
                    imgui.text("data")
                else:
                    column -= 1
                    clicked, self.data_shown[column][1] = imgui.combo(
                        self.data_shown[column][0], self.data_shown[column][1], data_shown_types)
                    self.data_shown[column][2] = data_shown_types[self.data_shown[column][1]]

            elif row==4:
                if column==0:
                    imgui.text("hits")
                else:
                    column -= 1
                    clicked, self.colours_shown[column][1] = imgui.combo(
                        self.colours_shown[column][0], self.colours_shown[column][1], colours)
                    self.colours_shown[column][2] = not bool(self.colours_shown[column][1])
                    self.impls[column].show_colour = self.colours_shown[column][2]





            if self.drop_downs[column-1][2].data_manager.mode == 'demo':
                # locks demo into middle row
                self.data_shown[column-1][1:] = [3, 'middle']
            

        imgui.separator()
        num_columns = 3
        num_rows = 5

        with imgui.begin_table("test", num_columns,
                                imgui.TABLE_BORDERS_INNER_VERTICAL
                               |imgui.TABLE_NO_KEEP_COLUMNS_VISIBLE
                               |imgui.TABLE_NO_CLIP):
            imgui.table_setup_column("item", imgui.TABLE_COLUMN_WIDTH_FIXED)
            imgui.table_setup_column("a", imgui.TABLE_COLUMN_WIDTH_FIXED)
            imgui.table_setup_column("b", imgui.TABLE_COLUMN_WIDTH_FIXED)
            for r in range(num_rows):
                imgui.table_next_row()
                for c in range(num_columns):
                    imgui.table_set_column_index(c)

                    set_static_choices(r, c)

                    

        self.space_lines(4)
        self.space_lines(4)
        
        def set_data_choices(row, column):

            #print(f"c1_01 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))


            self.checked_data = [self.impl_a.data_manager.impl_data_is_checked,
                                 self.impl_b.data_manager.impl_data_is_checked]
            self.point_info   = [self.impl_a.data_manager.data,
                                 self.impl_b.data_manager.data]


            len_info = [len(self.point_info[0]), len(self.point_info[1])]

            #print(f"c1_02 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))


            #if row-1<=len_info[column//2]:
            if c%2==0: # checkbox
                _, self.checked_data[column//2][row-1] = imgui.checkbox(
                    f"##{row}{column}", self.checked_data[column//2][row-1])
            else: # point info
                imgui.text(f'{self.point_info[column//2][row-1].int_number}')

            #print(f"c1_03 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))


            if self.data_shown[column//2][-1] == 'newest':
                if row==len_info[column//2]: # -1 to zero index it
                    self.checked_data[column//2][row-1] = True
                else:
                    self.checked_data[column//2][row-1] = False

                #print(f"c1_04 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))


            elif self.data_shown[column//2][-1] == 'middle':
                #self.checked_data[column//2] = [
                #    *(False,)*4, True, *(False,)*4]
                num_items = len(self.checked_data[column//2])
                #if num_items == 10:
                #    raise Exception
                
                if num_items%2==0 :
                    # even
                    self.checked_data[column//2] = [
                        *(False,)*(num_items//2), True, *(False,)*(num_items - num_items//2 - 1)]
                    pass
                else:
                    # odd
                    self.checked_data[column//2] = [
                        *(False,)*(num_items//2), True, *(False,)*(num_items//2)]
                    pass

                #print(f"c1_05 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))


            elif self.data_shown[column//2][-1] == 'none':
                self.checked_data[column//2][row-1] = False

                #print(f"c1_06 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))


            self.impls[column//2].data_manager.impl_data_is_checked = self.checked_data[column//2]

            #print(f"c1_07 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))

            
                
            if any(self.checked_data[column//2]):
                i = max(i for i, v in enumerate(self.checked_data[column//2]) if v == True)
                self.impls[column//2].pt_selected = self.point_info[column//2][i]
            else:
                self.impls[column//2].pt_selected = None


            #print(f"c1_07 {start_idx_012}", len(self.checked_data[0]), len(self.checked_data[1]))



            pass

        header = ['impl_a', 'point_a', 'impl_b', 'point_b']
        
        
        self.checked_data = [self.impl_a.data_manager.impl_data_is_checked,
                             self.impl_b.data_manager.impl_data_is_checked]
        self.point_info   = [self.impl_a.data_manager.data,
                             self.impl_b.data_manager.data]


        start_idx_012 = 0

        #table_height = np.maximum(len(self.impl_a_checked), len(self.impl_b_checked))
        table_height = np.maximum(len(self.checked_data[0]), len(self.checked_data[1]))+1
        #print("c", len(self.checked_data[0]), len(self.checked_data[1]))
        if table_height != 0:
            imgui.text("shown data points")
            imgui.separator()
        with imgui.begin_table("data_points", len(header), 
                                imgui.TABLE_BORDERS_INNER_VERTICAL
                               |imgui.TABLE_NO_KEEP_COLUMNS_VISIBLE
                               |imgui.TABLE_NO_CLIP):
            #imgui.table_setup_column("d_a",  imgui.TABLE_COLUMN_WIDTH_STRETCH)
            #imgui.table_setup_column("ip_b", imgui.TABLE_COLUMN_WIDTH_STRETCH)
            #imgui.table_setup_column("d_b",  imgui.TABLE_COLUMN_WIDTH_STRETCH)
            #imgui.table_setup_column("ip_b", imgui.TABLE_COLUMN_WIDTH_STRETCH)
            imgui.table_setup_column("d_a",  imgui.TABLE_COLUMN_WIDTH_FIXED)
            imgui.table_setup_column("ip_b", imgui.TABLE_COLUMN_WIDTH_FIXED)
            imgui.table_setup_column("d_b",  imgui.TABLE_COLUMN_WIDTH_FIXED)
            imgui.table_setup_column("ip_b", imgui.TABLE_COLUMN_WIDTH_FIXED)
            for r in range(table_height):
                imgui.table_next_row()
                for c in range(len(header)):
                    imgui.table_set_column_index(c)

                    if r==0:
                        imgui.text(header[c])
                    else:
                        if r-1 < len(self.checked_data[c//2]):
                            set_data_choices(r, c) # IT HAPPENS HERE (turning 10 into 9)

                    start_idx_012 += 1

        #print("c2", len(self.checked_data[0]), len(self.checked_data[1]))
        #if self.impls[1].data_manager.mode == "debug" and len(self.checked_data[0])==10:
        #    raise Exception

        imgui.end()

        end = time.time()
        self.dt = end-self.current
        self.current = end

