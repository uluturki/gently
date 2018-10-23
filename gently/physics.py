from .geometry import Point,Surface2D

def check_los(pert_list,p1,p2,epsilon=1e-6):
#p1 and p2 are two points in 3D space, and this function will check if there is a perturbation in between. tuples(x,y,z)
#epsilon is the accuracy
    los_obstruction_flag = False
    for pert in pert_list:
        surface_list = pert.get_surfaces()

        for surface in surface_list:
            # first check if the surface is relevant
            # it is done by creating the bounding box of two nodes(points) on x-y
            # then collusion between perturbations and that boundings box is checked
            # @TODO This bounding box stuff costs more than its worth, I'll leave it to its grave for now. There probably is a more efficient way to do this,
            # probably by refactoring how I store data, will come back to this in the future.
            #bounding_box = Surface2D(p1,p2,normal_vector=False)
            #if bounding_box.check_collision_rect(surface) is False:
            #    continue

            # if surface is not skipped, that means it's in the DANGER ZONE and should be checked.
            col_result = surface.check_collision_line(p1,p2,epsilon)
            if col_result is not None:
                los_obstruction_flag = True
                #print('LoS Obstruction Detected')
                #print(col_result)
                return los_obstruction_flag # If colludes even with a single thing, no need to check further

    return los_obstruction_flag
