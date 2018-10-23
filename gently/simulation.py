from .physics import check_los
from .network import gen_sim_network
from .geometry import Point
import random
import itertools
import copy
import numpy as np
import scipy as sp

class SimStage:
    """Object that holds necessary information and methods for 3D network simulation"""

    _delta_h = 0.0025 # This is added so that nodes are not within walls when buildings are added.

    def __init__(self,coordinates,radii,costs):
    #coordinates,radii,costs for different types of nodes, as a dictionary keyed by node type. (this way there could be an arbitrary number of types)
    #!WARNING: Right now, gen_sim_network function only supports 2 types.
        #@TODO: Check to make sure keys are matching
        self.coordinates_dict = coordinates
        self.coordinates_dict_base = copy.deepcopy(coordinates)
        self.radii_dict = radii
        self.costs_dict = costs
        self.node_types = coordinates.keys() # This returns an iterable, cast it to a list if need be.
        self.perturbation_list = None
        self.terrain_function = None
        self.terrain_params = None
        self._connected_node_keys = [] # @TODO This isn't properly kept up to date, look into that. Added here as a hack so online opimization can be done.
        self.update_connections()


    def update_connections(self):
    # Update the network edges based on current coordinates
        #!WARNING: This is a hacky solution until I implement the arbitrary numbers of node types in the future
        n_coordinates = self.coordinates_dict['node']
        bs_coordinates = self.coordinates_dict['basestation']
        d_node = self.radii_dict['node']
        d_basestation = self.radii_dict['basestation']
        cost_n2n = self.costs_dict['node']
        cost_bs2n = self.costs_dict['basestation']
        #!WARNING: This is a hacky solution until I implement the arbitrary numbers of node types in the future
        self.G_dict = gen_sim_network(n_coordinates,bs_coordinates,d_node,d_basestation,self.perturbation_list, cost_n2n,cost_bs2n)

    # Think about where to put the movement_model harder
    movement_model = None #!@TODO: Check this inside functions to make sure its set.
    rwp_variables = None # movement_model function should initialize this first call when noticing it's empty

    def network_connected_count(self, radius, basestation_keys, node_keys=[], r_n2n = 0.001, hop_count=1, p=2):
    # This function essentially implements the objective function from the paper, this is a separate function from update_connections to avoid
    # unnecessary computations for calculating the whole network during simulation iterations.
    # basestation_dict = {i:(x,y,z)}
    # 'Inspired' by networkx _slow_edges function
    #G = self.G_dict['nodes']
        # I need the union so I will start removing the connected ones.

        # Find the keys for nodes that are still disconnected
        disconnected_keys =  set(self.coordinates_dict['node'].keys()) - set(node_keys)

        # Only use those disconnected nodes for calculation of the goal function, thus optimization
        # This implements the independence assumption.
        node_dict = { k: self.coordinates_dict['node'][k] for k in disconnected_keys }
        # @TODO: this is a shit implementation as well, I will have to refactor the hell out of these after the paper deadline.
        n2n_node_dict =  { k: self.coordinates_dict['node'][k] for k in disconnected_keys }
        #print(node_dict)
        basestation_dict = self.coordinates_dict['basestation']
        connected_nodes = []
        #for (u, pu), (v, pv) in itertools.product((basestations),G.nodes(data='pos')):
        #print(basestation_keys)
        for idx_bs in basestation_keys:
            c_bs = basestation_dict[idx_bs]
            bs_connected_nodes = []
            for idx_node,c_node in node_dict.items():
#                c_node = node_dict[idx_node]
                #print(c_node)
                if sum(abs(a - b) ** p for a, b in zip(c_bs, c_node)) <= radius ** p:
                    #check LoS here too
                    #print('checking_LoS')
                    if check_los(self.perturbation_list,Point(c_bs[0],c_bs[1],c_bs[2]),Point(c_node[0],c_node[1],c_node[2])) is True:
                        continue
                    bs_connected_nodes.append(idx_node)
                    # @TODO Can remove the connected nodes from the node_dict but it may not improve speed that much so not bothering yet.
            connected_nodes = connected_nodes + bs_connected_nodes

            # pop nodes connected to current AP out of the dictionary
            # This has two benefits: 1. subsequents loops are shorter, thus faster. 2. Result is union, there can be no double counting.
            for k in bs_connected_nodes:
                node_dict.pop(k, None)

        n2n_connected = []
        #print(connected_nodes)

        # @TODO RIGHT NOW: d_node isn't changing anything, debug and figure out.
        if hop_count == 2:
            for u in np.arange(len(connected_nodes)):
                #not using itertools because node_dict changes in size. There might be a nice solution but deadline is at hand.
                pu = n2n_node_dict[connected_nodes[u]]
                #print(pu)
                node_n2n_connected = []
                for v,pv in node_dict.items():
                    pv = node_dict[v]
                    #print(pv)
                    if sum(abs(a - b) ** p for a, b in zip(pu, pv)) <= r_n2n ** p:
                        node_n2n_connected.append(v)

                n2n_connected = n2n_connected + node_n2n_connected
                n2n_connected = list(set(n2n_connected)) # get rid of duplicates.
                #print(node_n2n_connected)
                for k in set(node_n2n_connected):
                    node_dict.pop(k, None)
        elif hop_count > 2:
            print('MORE THAN 2 HOPS IS NOT SUPPORTED YET')

        connected_nodes = list(set(connected_nodes).union(set(n2n_connected)))
        #self._connected_node_keys = self._connected_node_keys + connected_nodes

        return connected_nodes


    def _network_connected_count_kd(self, radius, basestation_keys, node_keys=[], r_n2n = 0.001, hop_count=1, p=2):
    # This function essentially implements the objective function from the paper, this is a separate function from update_connections to avoid
    # unnecessary computations for calculating the whole network during simulation iterations.
    # basestation_dict = {i:(x,y,z)}
    # This is the second implementation with kD trees. Should speed up multihop.

        # Find the keys for nodes that are still disconnected
        disconnected_keys =  set(self.coordinates_dict['node'].keys()) - set(node_keys)

        # Only use those disconnected nodes for calculation of the goal function, thus optimization
        # This implements the independence assumption.
        node_dict = { k: self.coordinates_dict['node'][k] for k in disconnected_keys }
        node_array = np.array(list(node_dict.values()))
        # @TODO: this is a shit implementation as well, I will have to refactor the hell out of these after the paper deadline.
        n2n_node_dict =  { k: self.coordinates_dict['node'][k] for k in disconnected_keys }
        n2n_node_array = np.array(list(n2n_node_dict.values()))
        n2n_node_keys = np.array(list(n2n_node_dict.keys()))
        basestation_dict = { k: self.coordinates_dict['basestation'][k] for k in basestation_keys }
        basestation_array = np.array(list(basestation_dict.values()))

        # !! DOES A SINGLE PASS that gets smaller after each placement SO DOING A k-D tree is actually slower
        # !! ALSO THIS ISNT CHECKING LoS, d'oH DUMMY!
        # n2n_kdtree = sp.spatial.KDTree(n2n_node_array)
        # bs_kdtree = sp.spatial.KDTree(basestation_array)
        #
        #
        # #This one may actually be slower than passing through, because set gets smaller with each AP passself.
        # # @TODO maybe make this part as the old one, and just kdtree the multihop n2n connections.
        # con_nodes_ap_array = bs_kdtree.query_ball_tree(n2n_kdtree, r=radius, p=2.0, eps=0)
        #
        # bs_connected_keys = set()
        # for _ap_array in con_nodes_ap_array:
        #     bs_connected_keys = bs_connected_keys.union(set(_ap_array))
        bs_connected_nodes = []
        for idx_bs,c_bs in basestation_dict.items():
            #c_bs = basestation_dict[idx_bs]
            _connected_keys = []
            for idx_node,c_node in node_dict.items():
#                c_node = node_dict[idx_node]
                #print(c_node)
                if sum(abs(a - b) ** p for a, b in zip(c_bs, c_node)) <= radius ** p:
                    #check LoS here too
                    #print('checking_LoS')
                    if check_los(self.perturbation_list,Point(c_bs[0],c_bs[1],c_bs[2]),Point(c_node[0],c_node[1],c_node[2])) is True:
                        continue
                    _connected_keys.append(idx_node)
                    # @TODO Can remove the connected nodes from the node_dict but it may not improve speed that much so not bothering yet.
            bs_connected_nodes = bs_connected_nodes + _connected_keys # I don't need the individual ap connections, but if I need it in the future, this is the place to look.
            # pop nodes connected to current AP out of the dictionary
            # This has two benefits: 1. subsequents loops are shorter, thus faster. 2. Result is union, there can be no double counting.
            for k in bs_connected_nodes:
                node_dict.pop(k, None)

        #if len(bs_connected_keys) == 0:
        if len(bs_connected_nodes) == 0:
            # If nothing is connected to bs, the code below will explode
            n2n_connected_nodes = np.array([])
            bs_connected_nodes = np.array([])
        else:
            # @TODO: This won't work if node idx are not 1:N uninterrupted range... Or will it? Maybe...
            # Nodes connected to aps directly list and tree
            #bs_connected_keys = np.array(list(bs_connected_keys)) #this is disconnected subset keys
            #bs_connected_nodes = n2n_node_keys[bs_connected_keys] #this is real-life out of 400 keys
            #bs_con_array = n2n_node_array[bs_connected_keys]
            bs_con_array = np.array([ self.coordinates_dict['node'][k] for k in bs_connected_nodes ])
            bs_con_kdtree = sp.spatial.KDTree(bs_con_array)

            # Get the updated disconnected nodes list
            #mask = np.ones_like(n2n_node_keys, bool)

            #mask[bs_connected_keys] = False
            #bs_discon_array = n2n_node_array[mask]
            bs_discon_array = np.array([ k for k in node_dict.values() ])
            bs_discon_keys = np.array([ k for k in node_dict.keys() ])
            # Get the indices for that as well

            #bs_discon_keys = n2n_node_keys[mask]
            if len(bs_discon_array) == 0:
                con_nodes_n2n_array = np.array([])
            else:
                bs_discon_kdtree = sp.spatial.KDTree(bs_discon_array)
                con_nodes_n2n_array = bs_con_kdtree.query_ball_tree(bs_discon_kdtree, r=r_n2n, p=2.0, eps=0)

            n2n_connected_keys = set()
            for _n_array in con_nodes_n2n_array:
                n2n_connected_keys = n2n_connected_keys.union(set(_n_array))

            # Translate the  id's of subset to ids in the original list.
            if len(n2n_connected_keys) == 0:
                n2n_connected_nodes = np.array([])
            else:
                n2n_connected_keys = np.array(list(n2n_connected_keys))
                #n2n_connected_keys_translated = bs_discon_keys[n2n_connected_keys]#these are the for real keys?
                n2n_connected_nodes = bs_discon_keys[n2n_connected_keys]
                #n2n_connected_nodes = n2n_node_keys[n2n_connected_keys_translated]

        return list(n2n_connected_nodes) + list(bs_connected_nodes)

    # Call conform_perturbation_heights first because this checks perts. too.
    def update_node_heights(self,h_list,n_type='basestation'):
        node_keys = self.coordinates_dict_base[n_type]

        idx = 0;
        for key in node_keys:
            # first check if the given point is contained by any of the perturbations.
            node = self.coordinates_dict_base[n_type][key]
            #node_coord_dict = {'x':node[0],'y':node[1],'z':node[2]} # Set a dictionary
            h_new = h_list[idx]
            node = (node[0],node[1],h_new) # update in the temp tuple
            # Put that tuple back in the dictionary
            self.coordinates_dict[n_type][key] = node
            idx = idx + 1

    # @TODO This is separate from update_node_heights mostly because of legacy reasons, I will remove it at some point.
    def update_node_coordinates(self, x_list = None, y_list = None, h_list = None,n_type='basestation',node_keys = None):
        # Pass none for the coordinate you don't want to update. Can get pass a dictionary for it but no matter what people on stackoverflow says, I don't think that's useful here.
        if node_keys is None:
            node_keys = self.coordinates_dict_base[n_type].keys()

        idx = 0;
        for key in node_keys:
            # first check if the given point is contained by any of the perturbations.
            node = self.coordinates_dict_base[n_type][key]
            #node_coord_dict = {'x':node[0],'y':node[1],'z':node[2]} # Set a dictionary
            if h_list is None:
                h_new = node[2]
            else:
                h_new = h_list[idx]

            if y_list is None:
                y_new = node[1]
            else:
                y_new = y_list[idx]

            if x_list is None:
                x_new = node[0]
            else:
                x_new = x_list[idx]

            node = (x_new,y_new,h_new) # update in the temp tuple
            # Put that tuple back in the dictionary
            self.coordinates_dict[n_type][key] = node
            idx = idx + 1

    def move_nodes(self,movement_model,tick_length):
        #the movement model is an outside function here so it can't update object (?I think?),
        #return values and update it yourself.
        movement_dict = movement_model(self.coordinates_dict_base['node'],self.rwp_variables,tick_length)

        #self.node_coordinates = movement_dict['coordinates']
        self.coordinates_dict_base['node'] = movement_dict['coordinates']
        self.rwp_variables = movement_dict['rwp_variables']
        self.conform_node_heights(); # so the moved nodes conform to surface, I think this is the place for this.

    def tick_time(self,tick_length=1):
    # Make time pass for the movement model and update locations.
        self.move_nodes(self.movement_model, tick_length) # move the nodes and update the coordinates
        self.update_connections() # Update the edge connections with the new layout

    def update_perturbations(self,perturbation_list=None):
    # Don't forget to get the center heights from terrain so perturbations confor to the terrain
    # If no perturbation list is passed, just update the heights for a new terrain.
        if perturbation_list is None:
            # Update the heights of perturbations here
            # Conform perturbation heights is temporarily cancelled because it messes a lot of thing up...
            hacker_osman = 1 # doing this so I won't have to refactor again...
            #self.conform_perturbation_heights()
        else:
            self.perturbation_list = perturbation_list
            # Conform perturbation heights is temporarily cancelled because it messes a lot of thing up...
            #self.conform_perturbation_heights()

    # @AuthorsNote moved this to initial population generation, this way doesn't really work...
    # def fill_all_buildings(self,N):
    # # This is used to randomly place N number of nodes in all buildings.
    #     # Choose a building to fill, randomly
    #     node_keys = self.coordinates_dict['node'].keys() # Maybe these shouldn't be dicts :/
    #     last_key = max(list(node_keys))
    #     for key in range((last_key+1),(last_key+1)+N):
    #         pert = random.choice(self.perturbation_list)
    #         node_coodinates = self.place_in_building(pert)
    #         self.coordinates_dict['node'][key] = node_coodinates # probably base needs to be updated too...
    #         self.coordinates_dict_base['node'][key] = node_coodinates #@TODO not sure about this, think about it.... Tuples are immutable so no need to copy.

    def update_terrain(self,terrain_function, terrain_params = None):
    # Call a conform heights function here to have nodes conform to the terrain.
        # Pass params in a dictionary
        self.terrain_params = terrain_params
        self.terrain_function = terrain_function
#        self.conform_perturbation_heights();
#        self.conform_node_heights();

    def place_in_building(self,pert):
        #@TODO This can be prettier but I'm running out of time so it will have to do.
        # first choose a surface out of the perturbation
        surface_list = pert.get_surfaces()
        # 5th surface from top is bottom (floor), skip that.
        # @TODO This 5th surface is a MAGIC NUMBER, deal with this better.
        del surface_list[4]
        surface_idx = random.randint(0,len(surface_list)-1) # 5 surfaces are left
        surface = surface_list[surface_idx]
        # selected a random surface, now select a random point on that surface
        x_range = (min(surface.p1.x,surface.p2.x,surface.p3.x),max(surface.p1.x,surface.p2.x,surface.p3.x))
        y_range = (min(surface.p1.y,surface.p2.y,surface.p3.y),max(surface.p1.y,surface.p2.y,surface.p3.y))
        # when the roof is extended, z here does not get updated, thus I have to use the height.
        z_range = (min(surface.p1.z,surface.p2.z,surface.p3.z),max(surface.p1.z,surface.p2.z,surface.p3.z,pert.height))

        x = random.uniform(x_range[0],x_range[1])
        y = random.uniform(y_range[0],y_range[1])

        # do not sample from underground
        h_new = self.terrain_function(Point(x,y,0), self.terrain_params)
        z = random.uniform((h_new + self._delta_h),z_range[1])



        # z is a bit more tricky
        # if z_range[0] == z_range[1]: # this practically means if on the roof since floor is removed from list.
        #     z = z_range[0] + self._delta_h # on the roof, delta is always added. nowhere else to go, son.
        # else:
        #     h_new = self.terrain_function(Point(x,y,0), self.terrain_params)
        #     # making the minimum height the height of surface at new coordinates + delta
        #     z = random.uniform(z_range[0],z_range[1]) # if not the roof, then the min height can only be the ground surface height.
        #     if z <= h_new: # If z turned out to be underground, bring it up...
        #         z = z + h_new + self._delta_h

        if x_range[0] == x_range[1]:
            # If you don't check for this, you are pushing the node deep inside the building half of the time.
            if x_range[0] == pert.base_origin.x:
                x = x - self._delta_h
            else:
                x = x + self._delta_h

        elif y_range[0] == y_range[1]:
            if y_range[0] == pert.base_origin.y:
                y = y - self._delta_h
            else:
                y = y + self._delta_h

        elif z_range[0] == z_range[1]:
            # when the roof is extended, z here does not get updated, thus I have to use the height.
            z = pert.height + self._delta_h # if on the roof, defo +, because floor is deleted from the list.

        # After everyting is done, check if it is underground
        # h_new = self.terrain_function(Point(x,y,0), self.terrain_params)
        # if z <= h_new: # if z is underground
        #     z = z + h_new # raise z above ground @TODO This is not same as unifrom sampling from available surface, figure why that didn't work and go back to that ASAP


        new_coordinates = (x,y,z)

        return new_coordinates

    # Call conform_perturbation_heights first because this checks perts. too.
    def conform_node_heights(self,types=['node']):
    # Make this input agnostic, just receive terrain and perturbation list, as well as xyz coordinates, and hand out updated z coordinates.
    # If there is a node under a building, it will be shot up to the roof, because we are taking LoS to be 0-1 now, otherwise it can't communicate.

        # Doing it for all kinds of nodes !Scratch that, skip basestations. smushes basestations on the ground.
        for n_type in types: #self.node_types:
            node_keys = self.coordinates_dict_base[n_type]
            for key in node_keys:
                # first check if the given point is contained by any of the perturbations.
                node = self.coordinates_dict_base[n_type][key]
                #node_coord_dict = {'x':node[0],'y':node[1],'z':node[2]} # Set a dictionary
                node_point = Point(node[0],node[1],node[2])
                node_contained_flag = False
                for pert in self.perturbation_list:
                    node_contained_flag = pert.contains_point(node_point)
                    if node_contained_flag == True :
                        if n_type is 'node':
                            node = self.place_in_building(pert)
                            # print('placing in building: ' + str(key) + 'pheight: ' + str(pert.height))
                        else: # else is only basestation for now
                            h_new = pert.base_origin.z + pert.height + 2*self._delta_h
                            node = (node[0],node[1],h_new) #this is where node coordinate is updated
                        break

                # If not contained by any perturbations, it's just the height
                if node_contained_flag == False:
                    # height gets added and added when called multiple times, solution would be to store two parts
                    # separately and add on getting time, however for now just call it once!
                    h_new = self.terrain_function(node_point, self.terrain_params) + node[2] + self._delta_h;
                    #print('node not contained')
                    node = (node[0],node[1],h_new) #this is where node coordinate is updated
                    #print(h_new)

                # Put the updated tuple back in the dictionary
                self.coordinates_dict[n_type][key] = node

    def conform_perturbation_heights(self):
    # Maybe combine this with node one?
        for pert in self.perturbation_list:
            # Just check the height of base origin, no need to be more precise
            base_origin = pert.base_origin
            h_new = self.terrain_function(base_origin, self.terrain_params) + pert.height
            #base_origin['z'] = base_origin['z'] + h_new
            # Keep the z same but change the height so there are no nodes between pert floor and slope surface.
            #pert.base_origin = base_origin
            pert.height = h_new
            pert.update_mesh()


    def check_los(self,p1,p2,epsilon=1e-6):
    # This is moved under physics module within this package, call from there
        los_obstruction_flag = check_los(p1,p2,epsilon)
        return los_obstruction_flag
