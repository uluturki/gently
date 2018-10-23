import numpy as np
import copy

class Point:
    # storing as np_array because : 1. Not a very large number of points are used 2. There is plenty of memory so no need to avoid duplication 3. Profiling showed array casting eats a lot of time.
    np_array = {} #maybe name this just array...
    x = {}
    y = {}
    z = {}
    # learn how to overload this and have it receive a np.array as well maybe.
    def __init__(self,x,y,z):
        self.x = x # dict('x','y','z')
        self.y = y # dict('width','length')
        self.z = z
        self.update_array()

    def update_array(self):
        self.np_array = np.array((self.x,self.y,self.z))

    def update_coordinate(self,x=None,y=None,z=None):
    # Pass None for coordinates that will stay the same.
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z
        # After updating coordinates, update the array.
        self.update_array();

class RectPrism:
    '''Object that is used to store a 3D rect prism, and its 3D mesh. It's not supported to mess with the prism after it's created yet, so create a new one if you need to change anything!'''

    # Prism's lowermost-leftmost (lower left of the base) edge is on (0,0,0)
    mesh = {}
    base_origin = {}
    base_size = {}
    height = {}
    surface_list = {}
    range_list = {}

    # @TODO: overload this for different definitions of prisms, not necessary right now.
    # base_origin is a dictionary {'x','y','z'}, it is the lower left vertex of the base ! Update: This is now Point class defined above.
    # base_size is a dictionary {'width','length'}, it defines the lengts of the base edges.
        # length is added to 'x' and width is added to 'y' dimensions.
    # height is a scalar, it is the height of the prism
    def __init__(self,base_origin,base_size,height):
        self.base_origin = base_origin # This is now Point class
        self.base_size = base_size # dict('width','length')
        self.height = height
        # Saving these to save some calculations in the future.
        self.range_list = list()
        self.range_list.append((self.base_origin.x,self.base_origin.x + self.base_size['length'])) #x
        self.range_list.append((self.base_origin.y,self.base_origin.y + self.base_size['width']))  #y
        self.range_list.append((self.base_origin.z,self.base_origin.z + self.height))              #z

        self.update_surfaces()
        self.update_mesh()

        #self.update_surfaces() # it's not really comp. difficult so no harm doing it in the init.

    # This is done by creating a unit cube on web interface and applying transforms to it.
    def update_mesh(self):
        self.mesh = { 'x': np.array([0, 1, 1, 0, 0, 1, 1, 0])*self.base_size['length'] + self.base_origin.x,
                      'y': np.array([0, 0, 1, 1, 0, 0, 1, 1])*self.base_size['width'] + self.base_origin.y,
                      'z': np.array([0, 0, 0, 0, 1, 1, 1, 1])*self.height + self.base_origin.z,
                      'i': np.array([0, 1, 1, 2, 2, 3, 3, 0, 5, 4, 0, 1]),
                      'j': np.array([1, 2, 5, 5, 6, 6, 7, 7, 6, 6, 1, 4]),
                      'k': np.array([3, 3, 2, 6, 3, 7, 0, 4, 7, 7, 4, 5])
                    }
    # This may calculate triangular meshes or actual surfaces of the prism, whichever is easier I guess.
    #def update_surfaces(self):


    # @TODO This is here for legacy reasons, get rid of in the next refactoring and just access the variable.
    def get_surfaces(self):
        # need to return a new instace, because pointers, that's why.
        return list(self.surface_list)

    # https://stackoverflow.com/questions/5666222/3d-line-plane-intersection
    def update_surfaces(self):
        # How I want to define surface is 3 corner points. I will also need a normal vector
        # but that can be computed from 3 points as well.
        # Maybe do a 2D surface object?
        x0,y0,z0 = self.base_origin.x,self.base_origin.y,self.base_origin.z
        l,w = self.base_size['length'], self.base_size['width']
        h = self.height
        # @TODO These surfaces should be stored so they are not computed every time (normal vector takes a bit of time even if its not much)
        self.surface_list = [
            Surface2D(Point(x0,y0,z0),Point(x0+l,y0,z0),Point(x0,y0,z0+h)),
            Surface2D(Point(x0+l,y0,z0),Point(x0+l,y0,z0+h),Point(x0+l,y0+w,z0)),
            Surface2D(Point(x0+l,y0+w,z0),Point(x0+l,y0+w,z0+h),Point(x0,y0+w,z0)),
            Surface2D(Point(x0,y0,z0),Point(x0,y0+w,z0),Point(x0,y0+w,z0+h)),
            Surface2D(Point(x0,y0,z0),Point(x0+l,y0,z0),Point(x0,y0+w,z0)),
            Surface2D(Point(x0,y0,z0+h),Point(x0+l,y0,z0+h),Point(x0,y0+w,z0+h))
        ]

    # https://stackoverflow.com/questions/29720910/fastest-way-to-search-if-a-coordinate-is-inside-a-cube
    def contains_point(self,point): # point = Point Object
#        return all([self.x_range[0] <= point.x <= self.x_range[1],
#                    self.y_range[0] <= point.y <= self.y_range[1],
#                    self.z_range[0] <= point.z <= self.z_range[1]])
        return all( self.range_list[idx][0] <= point.np_array[idx] <= self.range_list[idx][1]
                    for idx in np.arange(len(self.range_list)) ) # wrapped in generator expression so it will short-circuit properly.



class Surface2D:
    p1 = {}
    p2 = {}
    p3 = {}
    normal_vector = {}

    # x_range (left,right), y_range(bot,top) is also the bounding box, useful for all sorts of collusion detection stuff.

    range_list = {}

    def __init__(self,p1,p2,p3=None,normal_vector = True): # p1,p2,p3 are Point Objects
    # If only gets p1 and p2, then assumes then may not be on the same planes and projects it on xy plane, becaue its the only use case for now '''
        self.p1 = p1
        self.p2 = p2
        if p3 is not None:
            self.p3 = p3
        else:
            self.p3 = Point(p1.x,p2.y,0) # give the projection of the bounding box of p1,p2 on xy plane.
            # first find which plane surface lies
            # gets the index of the fixed axis
            #fixed_axis = np.where((p1.np_array - p2.np_array) == 0)
            # Actually not necessary because I only care about

        # store these instead of calculating every time for a tiny speed boost...
        self.range_list = list()
        self.range_list.append((min(self.p1.x,self.p2.x,self.p3.x),max(self.p1.x,self.p2.x,self.p3.x))) #x
        self.range_list.append((min(self.p1.y,self.p2.y,self.p3.y),max(self.p1.y,self.p2.y,self.p3.y)))  #y
        self.range_list.append((min(self.p1.z,self.p2.z,self.p3.z),max(self.p1.z,self.p2.z,self.p3.z)))              #z
        #self.x_range = (min(self.p1.x,self.p2.x,self.p3.x),max(self.p1.x,self.p2.x,self.p3.x))
        #self.y_range = (min(self.p1.y,self.p2.y,self.p3.y),max(self.p1.y,self.p2.y,self.p3.y))
        #self.z_range = (min(self.p1.z,self.p2.z,self.p3.z),max(self.p1.z,self.p2.z,self.p3.z))
        # calculate and store the normal vector, speeds up 10x. However, if not going to be used, then no reason to compute. It's slow.
        if normal_vector is True:
            self.update_normal_vector()



    def contains_point(self,point): # point = Point class
        # wrapped in a generator so it short-circuits properly.
        return all( self.range_list[idx][0] <= point.np_array[idx] <= self.range_list[idx][1]
                    for idx in np.arange(len(self.range_list)) )

    def check_collision_rect(self, rect):
    # Assumes axis aligned rectangles (no rotation ever.) Parallel to surface is assumed non-collusion.
    # Checks if rectangles are not colliding, then inverts it. http://devmag.org.za/2009/04/13/basic-collision-detection-in-2d-part-1/
        #Rectangle 1’s bottom edge is higher than Rectangle 2’s top edge.
        #Rectangle 1’s top edge is lower than Rectangle 2’s bottom edge.
        #Rectangle 1’s left edge is to the right of Rectangle 2’s right edge.
        #Rectangle 1’s right edge is to the left of Rectangle 2’s left edge.
        # @TODO Python practice: Wrap this in a generator. I failed my first attemp :')
        return not any([(self.range_list[1][0] > rect.range_list[1][1]),        # y_range
		                (self.range_list[1][1] < rect.range_list[1][0]),   # y_range
		                (self.range_list[0][0] > rect.range_list[0][1]), #x_range
		                (self.range_list[0][1] < rect.range_list[0][0])]) #x_range



    def get_normal_vector(self):
        # Source: http://math.mit.edu/classes/18.02/notes/lecture5compl-09.pdf
        #first get the direction vectors of P1P2 and P1P3
        #v1 = np.array(self.p2) - np.array(self.p1)
        #v2 = np.array(self.p3) - np.array(self.p1)
        v1 = self.p2.np_array - self.p1.np_array # casting to array no longer necessary, thanks to Point class
        v2 = self.p3.np_array - self.p1.np_array

        # cross product of the direction vectors of the surface will give the normal
        normal_vector = np.cross(v2,v1)

        # Normalize the normal vector to an amplitude of 1.
        normal_vector = normal_vector / np.linalg.norm(normal_vector)
        return normal_vector

    def update_normal_vector(self):
        self.normal_vector = self.get_normal_vector()
		
    def check_collision_line(self,l_p1,l_p2,epsilon=1e-6):
        """
            Source: https://stackoverflow.com/questions/5666222/3d-line-plane-intersection
            @TODO: Add checks for when surface contains the line

            l_p1 and l_p2 are Point objects that are the two point defining the ray
            p_co, p_no: define the plane:
            p_co is a point on the plane (plane coordinate).
            p_no is a normal vector defining the plane direction;
               (does not need to be normalized).
            epsilon is the desired precision
            return a Vector or None (when the intersection can't be found).
        """
        #u = np.array(l_p2) - np.array(l_p1)
        u = l_p2.np_array - l_p1.np_array
        denominator = np.dot(self.normal_vector, u)
        if abs(denominator) > epsilon:
            # the factor of the point between p0 -> p1 (0 - 1)
            # if 'fac' is between (0 - 1) the point intersects with the segment.
            # otherwise:
            #  < 0.0: behind p0.
            #  > 1.0: infront of p1.
            #w = np.array(l_p1) - np.array(self.p1)
            w = l_p1.np_array - self.p1.np_array
            nominator = -np.dot(self.normal_vector,w)
            sI = nominator / denominator

            #print(c_p)
            #print(fac)
            # Check if the point is within the line segment
            if 0 <= sI <= 1: #this is not working, figure out why or figure out a different way to implement this...
                # It is indeed on the segment, check if within the given plane window
                #c_p = np.array(l_p1) + u * sI # This is the collusion point
                c_p_temp = l_p1.np_array + u * sI # This is the collusion point
                c_p = Point(c_p_temp[0],c_p_temp[1],c_p_temp[2])

                if self.contains_point(c_p):
                    return c_p

            return None
        else:
            # The segment is parallel to plane
            # @TODO: Will need to check if the plane contains the segment!
            return None
