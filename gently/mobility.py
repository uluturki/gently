import math
import random

# @TODO: this should probably take in at least a speed range parameter as well, for now I'm fixing it.
# @TODO: Think if it would be better to just return the displacement. If so update the implementation that way.
def rwp_2d_move(node_coordinates, rwp_variables, tick_length):
# node_coordinates and basetation_coordinates are dictionaries keyed by node id. tick_length is the number of
# time units to be advanced.
# this on x-y only, will implement a 3d one in the future if needed.
    s_range = (0.001,0.01)
    a_range = (0,math.radians(359))
    t_range = (0,9)

    node_keys = node_coordinates.keys()
    # If rwp_variables is not populated yet, this is the first call, go ahead and populate it randomly.
    # Keys of rwp_variables to match provided node_coordinates, which are unique node ids overall everywhere.
    if rwp_variables is None:
        rwp_variables = dict()
        # Assign every node a direction(angle), speed and duration in unit time
        rwp_variables = {n: (random.uniform(a_range[0],a_range[1]),
                             random.uniform(s_range[0],s_range[1]),
                             random.randint(t_range[0],t_range[1])) for n in node_keys}
    for t in range(tick_length):
        for n in node_keys:
            # if out of time, repopulate that row with a new waypoint.
            if rwp_variables[n][2] == 0:
                rwp_variables[n] = (random.uniform(a_range[0],a_range[1]),
                                    random.uniform(s_range[0],s_range[1]),
                                    random.randint(t_range[0],t_range[1]))

            angle = rwp_variables[n][0] # This should already be in radians
            speed = rwp_variables[n][1]

            # These should all be handled with iterables, list comprehension and such. Will get to it in the future.
            x_displacement = math.cos(angle) * speed
            y_displacement = math.sin(angle) * speed
            # If over the edges, just clamp it on the edges, this causes clumping on corners in long term.
            # @TODO: Implement bouncing and rolling edges, make it a parameter choice! Actually this function should just return displacements and another function should handle actual placements, under stage class so it always follows stage settings, implement this before starting to use movement models.
            clamp_max = 1
            clamp_min = 0
            node_coordinates[n] = (min(clamp_max,max(clamp_min,(node_coordinates[n][0] + x_displacement))),
                                   min(clamp_max,max(clamp_min,(node_coordinates[n][1] + y_displacement))),
                                   node_coordinates[n][2]) # Tuple, z axis is not modified

    return {'coordinates': node_coordinates, 'rwp_variables': rwp_variables}
