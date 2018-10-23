import networkx as nx

# @TODO pass is_connected to each function that needs it as an optional parameter, that way it won't have to get computed again and again for multiple metrics of a single stage. Or maybe have a single function that receives a list of metrics to calculate.
# Make this a submodule of network

# Now computing performance metrics for the final network G
# Doing parameters here like this so it would be easy to functionize them in the future

# I don't know this is good practice, but it might change in the future and I don't want to hunt nx calls.
def is_connected(G):
    is_conn = nx.is_connected(G)
    return is_conn

# Check giant component connected fraction
# @TODO add bs or node labels into the G as node labels, so that won't have to pass bs_indices in the future.
def connected_fraction(G,backhaul=True,bs_indices = None):
    is_conn = is_connected(G)
    if  is_conn == True:
        conn_per = 1.00
    elif is_conn == False:
        if backhaul is True:
            connected_set = set()
            for idx in bs_indices:
                connected_set.update(G.neighbors(idx))
            conn_per = len(connected_set)/(len(G)-len(bs_indices))
        else:
            Gcc=sorted(nx.connected_component_subgraphs(G), key = len, reverse=True)
            G0=Gcc[0]
            gc_size = len(G0) # Gives the number of nodes
            conn_per = gc_size/len(G)

    return conn_per


# k-connectedness
# First check if the network is connected, if not calculate for the giant component

# @TODO Think about what to return with this, to designate connected or not with it.
def k_connectedness(G):
# returns (is_conn,k_connectivity) where is_conn (boolean) says if the network is fully connected,
# if is_conn = False, then k_connectivity is the k value for the GIANT COMPONENT, not the whole thing, whole thing is obviously 0 because it's not connected.
    is_conn = is_connected(G) # is_conn is boolean

    if is_conn == True:
        k_connectivity = nx.node_connectivity(G)
        return (is_conn,k_connectivity)
    else:
        Gcc=sorted(nx.connected_component_subgraphs(G), key = len, reverse=True)
        G0=Gcc[0] # Got the giant component
        k_connectivity = nx.node_connectivity(G0)

    return (is_conn,k_connectivity)



# avg length of shortest paths
# @TODO: After doing backhaul, might want to represent data to/from backhaul vs. node2node in some way.
# First check if the network is connected
def avg_shortest_path_length(G, weight = None):
# G is nx network
# weight is the string key for the edge parameter to be used as weights, None computes unweighted.
    is_conn = is_connected(G)
    # If the graph is not connected, check it for the giant component
    if is_conn == True:
        avg_sp_length = nx.average_shortest_path_length(G, weight)
    else:
        Gcc=sorted(nx.connected_component_subgraphs(G), key = len, reverse=True)
        G0=Gcc[0] # Got the giant component
        avg_sp_length = nx.average_shortest_path_length(G0, weight)

    return(is_conn,avg_sp_length)

# @TODO: Minimum radius to fully connect / max connect is already implemented but isn't added here yet. Do that.

# # Minimum basestation transmit power (radius) to have a connected network
# n_decimals = 3 # number of decimals to stop the search at.
# d_nodes = 0.05 # this can also be added to the sweep at some point
# delta = 0.00001
#
# d_basestation = 0.3
# increment_list = [math.pow(10,-1*i) for i in np.arange(1,1+n_decimals)]
# node_coordinates = S.coordinates_dict['node']
# basestation_coordinates = S.coordinates_dict['basestation']
#
# for d_increment in increment_list:
#     #first_pass = True
#     is_conn = False
#     while is_conn == False:
#         #first_pass = False
#         d_basestation += d_increment
#         # Generate the network
#         print(d_nodes)
#         print(d_basestation)
#         minp_networks = gen_sim_network(node_coordinates,basestation_coordinates,d_nodes,d_basestation,S.perturbation_list)
#         G_minp = minp_networks['combined']
#         is_conn = nx.is_connected(G_minp)
#         #print('d_basestation: ' + str(d_basestation))
#         if d_basestation >= 1-delta:
#             break
#     if d_basestation >= 1-delta:
#         break
#
# if d_basestation >= 1-delta:
#     print('Connected network not possible, possibly due to LoS')
# else:
#     print('Minimum basestation transmit range for a connected network: ' + str(d_basestation))
