# @TODO: Name these properly?
# @TODO: Also think about a better way to implement this, maybe something modular with a surface object where I can pass a list of features to construct a surface or such. Think about it. Keeping a grid of surface handy will also probably speed up surface obstructed los checks.

# def surface_height_func(coordinates,flat_range,top_height):
#     """Return the ground surface height for given x,y coordinates"""
#     # Obviously RN implementing for just one func but in the future have parameters for
#     # this for different functions.
#
#     # This has two slopes on two sides and flat throughout
#     if coordinates['x'] < flat_range['low']:
#         return (top_height - top_height*(coordinates['x']/flat_range['low']))
#     elif coordinates['x'] > flat_range['high']:
#         return (top_height - (top_height*(1-coordinates['x'])/(1-flat_range['high'])))
#     else:
#         return 0
#
# # Make params (flat range and top height) a dictionary
# def surface_height_func2(coordinates,flat_range,top_height):
#     """Return the ground surface height for given x,y coordinates"""
#     # Obviously RN implementing for just one func but in the future have parameters for
#     # this for different functions. No safety checks either so sure be careful.
#
#     # This has two hills on two sides and flat throughout
#
#     x = coordinates['x']
#     y = coordinates['y']
#     l = flat_range['low']
#     h = flat_range['high']
#
#     # crop from y's a bit too
#
#     if y < 0.2:
#         return 0
#     elif y > 0.8:
#         return 0
#
#     if x < l:
#         return (top_height-0.025)*((l - x)/(l))
#     elif x > h and x < (h+(1-h)/2):
#         return (top_height+0.025)*((x - h)/((1 - h)/2))
#     elif x >= (h+(1-h)/2):
#         return (top_height+0.025)*((1 - x)/((1 - h)/2))
#     else:
#         return 0
#
# # Make params (flat range and top height) a dictionary
# def surface_height_func3(coordinates,params):
#     """Return the ground surface height for given x,y coordinates"""
#     # Obviously RN implementing for just one func but in the future have parameters for
#     # this for different functions. No safety checks either so sure be careful.
#
#     # This has two hills on two sides and flat throughout
#
#     # @TODO: have default values
#     flat_range = params['range']
#     top_height = params['height']
#
#     x = coordinates['x']
#     y = coordinates['y']
#     l = flat_range['low']
#     h = flat_range['high']
#
#     # crop from y's a bit too
#
#     if y < 0.2:
#         return 0
#     elif y > 0.8:
#         return 0
#
#     if x < l:
#         return (top_height-0.025)*((l - x)/(l))
#     elif x > h and x < (h+(1-h)/2):
#         return (top_height+0.025)*((x - h)/((1 - h)/2))
#     elif x >= (h+(1-h)/2):
#         return (top_height+0.025)*((1 - x)/((1 - h)/2))
#     else:
#         return 0

# Make params (flat range and top height) a dictionary
def surface_height_func4(coordinates,params):
    """Return the ground surface height for given x,y coordinates"""
    # coordinates is a geometry.Point object
    # Obviously RN implementing for just one func but in the future have parameters for
    # this for different functions. No safety checks either so sure be careful.

    # This has two hills on two sides and flat throughout

    # @TODO: have default values
    flat_range = params['range']
    top_height = params['height']

    x = coordinates.x
    y = coordinates.y
    l = flat_range['low']
    h = flat_range['high']

    # crop from y's a bit too

    if y < 0.2:
        if x < l:
            return 0
        elif x > h: # and x < (h+(1-h)/2)
            return (top_height+0.005)*((x - h)/((1 - h)))
    elif y > 0.8:
        if x < l:
            return 0
        elif x > h: # and x < (h+(1-h)/2)
            return (top_height+0.005)*((x - h)/((1 - h)))

    if x < l:
        return (top_height-0.025)*((l - x)/(l))
    elif x > h: # and x < (h+(1-h)/2)
        return (top_height+0.005)*((x - h)/((1 - h)))
    else:
        return 0
    #    elif x >= (h+(1-h)/2):
    #        return (top_height+0.025)*((1 - x)/((1 - h)/2))
