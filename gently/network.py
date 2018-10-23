import networkx as nx
# gently.physics, maybe this is not the right way to import this...
from .physics import check_los
from .geometry import Point

# Define network creation as a function
# @TODO BIG BIG @TODO: Add a single node that is connected to every basestation, that is the backhaul. It's existence
# can be passed down as a parameter.
def gen_sim_network(node_coordinates,basestation_coordinates,d_node,d_basestation,pert_list,cost_n2n = 1,cost_bs2n = 1):
# node_coordinates, basetation_coordinates: dictionary of cartesian coordinates in a 1x1x1 unit cube
# @TODO: Figure if I want this to have Point objects as well, networkx doesn't like it, so dunno, not dealing with that right now.
# d_node,d_basestation: connection radius for node2node and basetation2node connections.
# cost_n2n, cost_bs2n: power cost of a single hop, node to node or basestation to node (bidirectional)
# Returns a dictionary of networks for combined, nodes and basestations.

    # Generate the graph
    # There is no default function that lets me do 2 different radii, however what I can do is:
    #      - 1.First generate the bottom layer network with node radius
    #      - 2.Then generate a second network with all the vertices, nodes and basestations, with basestation radius
    #      - 3.add the basestations and their edges to the first network. Since connections are bidirectional, this will work.


    # 1.Node network (On the ~ground)
    N = len(node_coordinates)
    N_b = len(basestation_coordinates)

    G_nodes = nx.random_geometric_graph(N,d_node,pos=node_coordinates)
    nx.set_edge_attributes(G_nodes,'power_cost',cost_n2n)

    # Concatanate dictionaries (! Apparently there are faster ways but I don't care yet)
    combined_coordinates_list = dict(node_coordinates)
    combined_coordinates_list.update(basestation_coordinates)
    # 2.Full network with basestation radius
    G_combined = nx.random_geometric_graph((N+N_b),d_basestation,pos=combined_coordinates_list)
    # Now iterate through each edge and delete the ones that lack LoS
    node_keys = range(N)
    basestation_keys = range(N,N+N_b)

    if pert_list != None:
        edge_list = G_combined.edges(basestation_keys) #@TODO Ignoring LoS checks for node2node connections, because they are very high, due to all building ones being piled on a single spot (20-30x higher than it should be)
        edges_to_remove = []
        for edge in edge_list:
            p_1 = combined_coordinates_list[edge[0]]
            p_2 = combined_coordinates_list[edge[1]]
            p_1 = Point(p_1[0],p_1[1],p_1[2])
            p_2 = Point(p_2[0],p_2[1],p_2[2])
            if check_los(pert_list,p_1,p_2) == True:
                edges_to_remove.append(edge)
        #print(edges_to_remove)
        G_combined.remove_edges_from(edges_to_remove)

    # 2. Now remove all the edges between nodes and preserve only the edges between basestations and nodes.
    # Get all the edges related to nodes
    combined_edges = G_combined.edges(node_keys)
    # Get the edges that are connected to at least one basestation
    # !There may be better/faster ways for this but it looks kawaii and I learned list comprehension for this so I'll keep it.
    bs_edges = [edge for edge in combined_edges if any(e_d in basestation_keys for e_d in edge)]
    # Now get the edges that are only between nodes
    node_edges = [edge for edge in combined_edges if edge not in bs_edges ]
    # Now remove all the edges between nodes, do this in a new instance of network
    G_addition = nx.Graph(G_combined)
    G_addition.remove_edges_from(node_edges)
    nx.set_edge_attributes(G_addition,'power_cost',cost_bs2n) # This is the network with only basestation to node edges.
    # Now combine two networks
    G = nx.algorithms.operators.binary.compose(G_nodes,G_addition) # attributes of nodes take precedent here, be careful.
    #nx.set_node_attributes(G,'type',)
    # Also generate a basestation only network, mostly for visualization purposes
    G_basestations = nx.Graph(G_combined)
    G_basestations.remove_nodes_from(node_keys)

    return {'combined': G, 'nodes': G_nodes, 'basestations': G_basestations, 'b2n': G_addition } # b2n is the network that only has edges between basestations and nodes
