from software.signal_display.scintillator_display.compat.universal_values import MathDisplayValues
'''

Algorithm that takes in which scintillators lit up and returns a convex hull to bound the muon path

Input type : List containing tuples representing the activation states of each level from top to bottom
                     (0, 1) means every second scintillator lights up
                     (1, 0) means every first scintillator lights up
                     (1, 1) All the scintillator lit up
                     (0, 0) No scintillator lit up
            -- > See display software, contains a function that converts the 32 bit number 
                 that the detector outputs to the above formatting

Output type: Prism vertices and 2 points per fan out line
Current output type : For the moment 2 lines creating 

UPCOMING CHANGES : (In order of importance)
- Take advantage of (1, 1) type levels
- Write code in a class to permit scailability
- Efficiency review, current code is O(n), but all cases could be simulated and stored for lookup for O(log(n))

Unit x is mm
'''   

class ConvexHullDetection(MathDisplayValues):
    def __init__(self, impl_constant=1):
        pass

        # constant multiplication from each impl
        self.impl_constant = impl_constant

        self.reset_to_initial_values()

    def reset_to_initial_values(self):
        # Global variables
        self.level_count = 1
        self.n = self.SQUARE_LEN * self.impl_constant # Sideview length of scintillator in unit x

        # These values are used for x perspective
        self.upper_side_views = [(0, self.n)] # (start, end) coordinates for each level 
        self.lower_side_views = [(0, self.n)]

        self.plate_thickness = self.SCINTILLATOR_THICKNESS * self.impl_constant # In unit x
        self.intra_level_gap = self.SPACE_BETWEEN_SCINTILLATORS * self.impl_constant #Actual physical gap between each level, in unit x
        self.inter_level_gap = self.plate_thickness + self.intra_level_gap # Adjusted inter level gap for computation 

        self.half_gap_size =  self.SPACE_BETWEEN_STRUCTURES / 2 *self.impl_constant# In unit x
        self.top_half_gap = self.half_gap_size + self.plate_thickness + self.intra_level_gap
        self.bottom_half_gap = self.half_gap_size
        self.gap_line = 0
        self.highest_point = self.half_gap_size + self.NUM_SMALL_SPACES*self.intra_level_gap + self.NUM_SCINTILLATORS_PER_STRUCTURE*self.plate_thickness # Values custom set to this detector
        self.lowest_point = -self.highest_point

    def update_perspective_values(self):

        self.upper_side_views = [(0, self.n)] # (start, end) coordinates for each level 
        self.lower_side_views = [(0, self.n)]

        self.top_half_gap = self.half_gap_size
        self.bottom_half_gap = self.half_gap_size + self.plate_thickness + self.intra_level_gap

        # Update level count
        self.level_count = 1


    # Functions
    def find_intersection(self, line1, line2):
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2

        # Calculate the determinants
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if denominator == 0:  # Lines are parallel
            return (-100, -100) #Point out of the detector

        x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
        y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator

        return (x, y)


    def find_points_on_line(self, line, target_y):
        '''
        Takes in a line and computes 2 points on the line for the line coordinate.
        '''
        x1, y1 = line[0]
        x2, y2 = line[1]

        # Find the x-coordinate for the given target y-coordinate
        def find_x_for_y(y):
            # Using the line equation: y - y1 = m(x - x1) -> solving for x
            return x1 + (y - y1) / m
        
        if x1 != x2: # Avoid division by zero
            # Calculate the slope (m)
            m = (y2 - y1) / (x2 - x1)

            # Find the x-coordinates for the target_y and -target_y
            x_pos = find_x_for_y(target_y)
            x_neg = find_x_for_y(-target_y)
        else : # If vertical line
            x_pos = x1
            x_neg = x2
        
        # Return the points
        return (x_pos, x_neg)




    def hull_coordinates(self, x_bound, z_bound):
        '''
        Returns the 8 points that bound the rectangular prism (which is extended up in the rendering)
        [((0, 10), (0.25, -9)), ((0.25, 9), (0.5 -10))]
        '''

        x_left_bound = x_bound[0]
        x_right_bound = x_bound[1]
        z_left_bound = z_bound[0]
        z_right_bound = z_bound[1]

        # Recalculate bounds for another y value
        x_left_bound = self.find_points_on_line(x_left_bound, self.highest_point)
        x_right_bound = self.find_points_on_line(x_right_bound, self.highest_point)
        z_left_bound = self.find_points_on_line(z_left_bound, self.highest_point)
        z_right_bound = self.find_points_on_line(z_right_bound, self.highest_point)

        # Match correspongind bounds (x, z, y) 
        bounding_points = [(x_left_bound[0], z_right_bound[0], self.highest_point), (x_left_bound[0], z_left_bound[0], self.highest_point),
                        (x_right_bound[0], z_right_bound[0], self.highest_point), (x_right_bound[0], z_left_bound[0], self.highest_point),
                        (x_left_bound[1], z_right_bound[1], self.lowest_point), (x_left_bound[1], z_left_bound[1], self.lowest_point),
                        (x_right_bound[1], z_right_bound[1], self.lowest_point), (x_right_bound[1], z_left_bound[1], self.lowest_point)]
        
        return bounding_points

    def group_corresponding_levels(self, levels):
        '''
        Reorders the initial list of scintillators 
        '''
        # Group first with last, second with second to last, etc
        k = len(levels)
        grouped_levels = []
        
        # Pair up levels from outside moving inward
        for i in range(k // 2):
            grouped_levels.append((levels[i], levels[k-1-i]))
            
        return grouped_levels[::-1] # Put the elements in the middle first and the ones on the edges last


    def draw_bounds(self, level_pair, previous_bounds):
        '''
        Takes the scintillators that were activated at corresponding levels and draws better bounds 
        according to previous bounds. 
        :param previous_bounds: 4 points, 2 points per old tightest line.
                                ((p1, p2), (p3, p4)) where (left_bound, right_bound)
        :return new_bounds: 4 points, 2 points per new tightest line. 
        '''

        # Will implement a version with classes to avoid this horror :
        # Default point (0, n)
        # Ajusted point (side_view[level_count-1][0], side_view[level_count-1][1])

        upper_level = level_pair[0]
        lower_level = level_pair[1]

        upper_level_points = []
        lower_level_points = []
        
        # Adjust upper side view points
        interval = self.n / 2**self.level_count

        if upper_level == (1, 0):
            self.upper_side_views.append((self.upper_side_views[self.level_count-1][0], self.upper_side_views[self.level_count-1][0]+interval))
        elif upper_level == (0, 1):
            self.upper_side_views.append((self.upper_side_views[self.level_count-1][1]-interval, self.upper_side_views[self.level_count-1][1]))
        elif upper_level == (1, 1):
            # An implementation of this case will be made later to take full advantage of this unique situation
            return previous_bounds
            
        else :
            return None

        # Adjust lower side view points
        if lower_level == (1, 0):
            self.lower_side_views.append((self.lower_side_views[self.level_count-1][0], self.lower_side_views[self.level_count-1][0] + interval ))
        elif lower_level == (0, 1):
            self.lower_side_views.append((self.lower_side_views[self.level_count-1][1]-interval, self.lower_side_views[self.level_count-1][1]))
        elif lower_level == (1, 1):
            # An implementation of this case will be made later to take full advantage of this unique situation
            return previous_bounds
            
        else :
            return None
            
        
        # Increase counters
        self.level_count += 1

        # Set coordinate points for the rod on each level 
        upper_level_points.extend([(self.upper_side_views[self.level_count-1][0], self.top_half_gap + self.plate_thickness*(self.level_count-2) + self.inter_level_gap*(self.level_count-2)), # Lower left point
                                    (self.upper_side_views[self.level_count-1][1], self.top_half_gap + self.plate_thickness*(self.level_count-2) + self.inter_level_gap*(self.level_count-2)), # Lower right point
                                    (self.upper_side_views[self.level_count-1][0], self.top_half_gap + self.plate_thickness*(self.level_count-1) + self.inter_level_gap*(self.level_count-2)), # Upper left point
                                    (self.upper_side_views[self.level_count-1][1], self.top_half_gap + self.plate_thickness*(self.level_count-1) + self.inter_level_gap*(self.level_count-2))]) # Upper right point
        
        lower_level_points.extend([(self.lower_side_views[self.level_count-1][0], -(self.bottom_half_gap + self.plate_thickness*(self.level_count-2) + self.inter_level_gap*(self.level_count-2))), # Upper left point
                                    (self.lower_side_views[self.level_count-1][1], -(self.bottom_half_gap + self.plate_thickness*(self.level_count-2) + self.inter_level_gap*(self.level_count-2))), # Upper right point
                                    (self.lower_side_views[self.level_count-1][0], -(self.bottom_half_gap + self.plate_thickness*(self.level_count-1) + self.inter_level_gap*(self.level_count-2))), # Lower left point
                                    (self.lower_side_views[self.level_count-1][1], -(self.bottom_half_gap + self.plate_thickness*(self.level_count-1) + self.inter_level_gap*(self.level_count-2)))]) # Lower right point


        # Create level lines $ DPONT FORGET THIS
        upper_line_y = self.top_half_gap + (self.inter_level_gap+self.plate_thickness)*(self.level_count-2)
        lower_line_y = self.bottom_half_gap + (self.inter_level_gap+self.plate_thickness)*(self.level_count-2)
        upper_line = ((0, upper_line_y), (1, upper_line_y))
        lower_line = ((0, -lower_line_y), (1, -lower_line_y))

        # Create new potential lines
        left_bound = (upper_level_points[2], lower_level_points[2])
        right_bound = (upper_level_points[3], lower_level_points[3])

    # Check if bounds are valid 
    # Check this section it seems to mess things up
        # Check left_bound potential line intersections
        x, y = self.find_intersection(left_bound, previous_bounds[0])

        if left_bound[0][0] < x < left_bound[1][0]: # Check for intersection with a previous bound
            if y >= 0 : # Check gap side
                # print('Left upper previous bound intersection')
                left_bound = (previous_bounds[0][0], left_bound[1])
            else :
                # print('Left lower previous bound intersection')
                left_bound = (left_bound[0], previous_bounds[0][1])
        # Check left_bound potential scintillator non-valid overlap
        else:
            x, y = self.find_intersection(left_bound, upper_line)
            if not upper_level_points[0][0] < x < upper_level_points[1][0]:
                # print('detector line intersection upper left')
                left_bound = (upper_level_points[0], left_bound[1])

            x, y = self.find_intersection(left_bound, lower_line)
            if not lower_level_points[0][0] < x < lower_level_points[1][0]:
                # print('detector line intersection lower left')
                left_bound = (left_bound[0], lower_level_points[0])

        # Check right_bound potential line intersections

        x, y = self.find_intersection(right_bound, previous_bounds[1])
        if right_bound[0][0] < x < right_bound[1][0]: # Check for intersection with a previous bound
            if y >= 0 : # Check gap side
                # print('Right upper previous bound intersection')
                right_bound = (previous_bounds[1][0], right_bound[1])
            else :
                # print('Right lower previous bound intersection')
                right_bound = (right_bound[0], previous_bounds[1][1])
        # Check right_bound potential scintillator non-valid overlap
        else:
            x, y = self.find_intersection(right_bound, upper_line)
            if not upper_level_points[0][0] < x < upper_level_points[1][0]:
                # print('detector line intersection upper right')
                right_bound = (upper_level_points[1], right_bound[1])

            x, y = self.find_intersection(right_bound, lower_line)
            if not lower_level_points[0][0] < x < lower_level_points[1][0]:
                # print('detector line intersection lower right')
                right_bound = (right_bound[0], lower_level_points[1])

        return [left_bound, right_bound]

        

        

    def detect_side_view(self, scintillators):
        '''
        Executes detection for 1 path
        :param path: List of scintillators that were activated according to input type (see document docstring above)
        :return bounds: List containing bounds (see output type above)
        '''
        corresponding_levels = self.group_corresponding_levels(scintillators)
        best_bounds = [((0, 10), (0, -10)), ((self.n, 10), (self.n, -10))] # 2 points per best bounding line. 

        for level_pair in corresponding_levels:

            best_bounds = self.draw_bounds(level_pair, best_bounds)
            if best_bounds == None:
                return None
            
        return best_bounds


    def scintillators_to_bounds(self, scintillators):
        '''
        :param scintillators: tuple containing two lists, one for each side view
        :return bounds: tuple containing two lists each containing the points that bound the muon path
        '''

        x_view = scintillators[0]
        z_view = scintillators[1]

        x_bounds = self.detect_side_view(x_view)
        self.update_perspective_values()
        z_bounds = self.detect_side_view(z_view)

        if x_bounds == None or z_bounds == None:
            return None
        
        # Transform z-bounds to correct coordinate system
        for i in range(2):
            z_bounds[i] = ((self.n - z_bounds[i][0][0], z_bounds[i][0][1]), (self.n - z_bounds[i][1][0], z_bounds[i][1][1]))

        hull_bounds = self.hull_coordinates(x_bounds, z_bounds)

        # Reset initial values before next use
        self.reset_to_initial_values()

        return hull_bounds

