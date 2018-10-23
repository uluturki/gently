import numpy as np #@TODO Anything that need numpy here needs to be somewhere else!
import math #@TODO Anything that need numpy here needs to be somewhere else!
import networkx as nx
import plotly
from .geometry import Point
#import plotly.graph_objs as plotly.go

# @TODO Move this under simulation module as submodule, as a sibling module of stage, or maybe put it in stage, since it only visualizes the stage, though in the future it may visualize with time and stuff.

# Add these as node properties to G in the future

_layout_dim = 1000 # have it always cubic for now
_d = 0.015
_scol = "rgb(30, 140, 15)"
_node_size = _d*_layout_dim/math.pi

# Grid for the surface height function
_x_range=np.linspace(0,1,100)
_y_range=np.linspace(0,1,100)

# @TODO RIGHT AWAY: Layout and stuff is all wrong and jambled, fix that first thing.
def visualize_stage(S,figure_name = 'stage_vis'):
# Params, S: simulation stage, terrain comes in S too so no need to pass it either. This is seriously starting to feel like it should go in stage...
# Dimensions and radii and stuff are not parameters because it's not the intenion of this function. This function simply aims to have reproducable figures for publications... They will be set once and be forever fixed.
# Figure name is the name of the figure (or html file) that will be saved.

# @TODO they can maybe be fixed global variables within this module in the future.

    G = S.G_dict['combined']
    G_n2n = S.G_dict['nodes']
    G_b2n = S.G_dict['b2n']

    N_vis = len(G)
    basestation_keys = S.coordinates_dict_base['basestation'].keys()
    node_keys = S.coordinates_dict_base['node'].keys()

    pos = nx.get_node_attributes(G,'pos')
    pert_list = S.perturbation_list



    Xn=[pos[k][0] for k in node_keys]# x-coordinates of nodes
    Yn=[pos[k][1] for k in node_keys]# y-coordinates
    Zn=[pos[k][2] for k in node_keys]# z-coordinates

    Xbs=[pos[k][0] for k in basestation_keys]# x-coordinates of nodes
    Ybs=[pos[k][1] for k in basestation_keys]# y-coordinates
    Zbs=[pos[k][2] for k in basestation_keys]# z-coordinates

    # Get the edge end point coordinates
    edge_list_b2n = G_b2n.edges()
    Xe_b2n=[]
    Ye_b2n=[]
    Ze_b2n=[]
    for e in edge_list_b2n:
        Xe_b2n+=[pos[e[0]][0],pos[e[1]][0], None]# x-coordinates of edge ends
        Ye_b2n+=[pos[e[0]][1],pos[e[1]][1], None]
        Ze_b2n+=[pos[e[0]][2],pos[e[1]][2], None]


    #@TODO Color node to node edges node color (red)!
    trace_b2n_edges=plotly.graph_objs.Scatter3d(x=Xe_b2n,
                   y=Ye_b2n,
                   z=Ze_b2n,
                   mode='lines',
                   name='connections',
                   line=plotly.graph_objs.Line(color='rgba(0,0,125,1)', width=0.8)
                   )

    # Get the edge end point coordinates
    edge_list_n2n = G_n2n.edges()
    Xe_n2n=[]
    Ye_n2n=[]
    Ze_n2n=[]
    for e in edge_list_n2n:
        Xe_n2n+=[pos[e[0]][0],pos[e[1]][0], None]# x-coordinates of edge ends
        Ye_n2n+=[pos[e[0]][1],pos[e[1]][1], None]
        Ze_n2n+=[pos[e[0]][2],pos[e[1]][2], None]


    #@TODO Color node to node edges node color (red)!
    trace_n2n_edges=plotly.graph_objs.Scatter3d(x=Xe_n2n,
                   y=Ye_n2n,
                   z=Ze_n2n,
                   mode='lines',
                   name='connections',
                   line=plotly.graph_objs.Line(color='rgba(125,0,0,1)', width=1.1)
                   )

    trace_nodes=plotly.graph_objs.Scatter3d(x=Xn,
                   y=Yn,
                   z=Zn,
                   mode='markers',
                   name='nodes',
                   marker=plotly.graph_objs.Marker(symbol='dot',
                                 size=_node_size,
                                 line=plotly.graph_objs.Line(color='rgb(50,50,50)', width=0.5),
                                 color='rgba(125,0,0,0.9)'
                                 )
                   )

    trace_bs=plotly.graph_objs.Scatter3d(x=Xbs,
                   y=Ybs,
                   z=Zbs,
                   mode='markers',
                   name='basestations',
                   marker=plotly.graph_objs.Marker(symbol='dot',
                                 size=_node_size*3,
                                 line=plotly.graph_objs.Line(color='rgb(50,50,50)', width=0.5),
                                 color='rgba(0,0,125,1)'
                                 )
                   )


    # This is defining a unit cube mesh, any rectangular prism can be achieved by
    # arithmetic on x, y, z vectors.
    # go through a list of cubes here.

    #mesh_cube_unit = { 'x': np.array([-0.5, -0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5]),
    #                   'y': np.array([-0.5, 0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5]),
    #                   'z': np.array([0, 0, 0, 0, 1, 1, 1, 1]),
    #                   'i': np.array([0, 0, 0, 1, 0, 3, 3, 7, 2, 5, 6, 7]),
    #                   'j': np.array([1, 2, 4, 4, 4, 4, 2, 6, 1, 7, 5, 5]),
    #                   'k': np.array([2, 3, 1, 5, 3, 6, 6, 2, 7, 1, 4, 6])
    #                 }


    mesh_list = [plotly.graph_objs.Mesh3d(pert.mesh, color='rgba(125,125,125,1)', opacity = 0.8) for pert in pert_list]
    #mesh=plotly.graph_objs.Mesh3d(pert_1.mesh)

    # Looks like X and Y is all confused
    h_surface = []
    for y_h in _y_range:
        h_temp = []
        for x_h in _x_range:
            h_temp.append(S.terrain_function(Point(x_h,y_h,0),S.terrain_params)) # z doesn't matter for the point since that's what we are trying to figure out, ignored inside function.
        h_surface.append(h_temp)

    _scol = "rgb(30, 140, 15)"

    trace_surface = plotly.graph_objs.Surface(
            x=_x_range,
            y=_y_range,
            z=h_surface,
            showscale = False,
            autocolorscale = False,
            cauto = False,
            cmax = 0,
            cmin = -0.5,
            colorscale = [ [  0, _scol], [0.35, _scol], [0.5, _scol],
                           [0.6, _scol], [0.7, _scol],  [1, _scol] ],
            surfacecolor= _scol,
            opacity = 1.0
        )



    # _x_range=np.linspace(0,1,100)
    # _y_range=np.linspace(0,1,100)
    #
    # s_flat_range = {'low':-0.1,'high':1.1}
    # top_height=0.1
    #
    # h_surface_flat = []
    # for y_h in _y_range:
    #     h_temp = []
    #     for x_h in _x_range:
    #         h_temp.append(surface_height_func({'x':x_h,'y':y_h},s_flat_range,top_height))
    #     h_surface_flat.append(h_temp)
    #
    #
    # trace_surface_flat = plotly.graph_objs.Surface(
    #         x=_x_range,
    #         y=_y_range,
    #         z=h_surface_flat,
    #         showscale = False,
    #         autocolorscale = False,
    #         cauto = False,
    #         cmax = 0,
    #         cmin = -0.5,
    #         colorscale = [ [  0, _scol], [0.35, _scol], [0.5, _scol],
    #                        [0.6, _scol], [0.7, _scol],  [1, _scol] ],
    #         surfacecolor= _scol
    #         )

    # size is a bit arbitrary, figure that out to match d with size
    axis=dict(autorange=False,
              showbackground=False,
              showline=True,
              zeroline=True,
              showgrid=True,
              showticklabels=False,
              range=[0,1],
              title=''
              )

    z_axis=dict(autorange=False,
              showbackground=False,
              showline=True,
              zeroline=True,
              showgrid=True,
              showticklabels=False,
              range=[0,0.2],
              title='',
              nticks=6,
              )

    #camera = dict(
    #    up=dict(x=0, y=0, z=1),
    #    center=dict(x=0, y=0, z=0),
    #    eye=dict(x=1.75, y=-1.1, z=0.65)
    #)

    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=2.0710389646410197, y=0.6609030190054094, z=0.707922068348940)

    )
    #        eye=dict(x=2.0710389646410197, y=0.6609030190054094, z=0.707922068348940)

    # Actualy, size of the thing is given as 1000*1000*1000 so size ends up d*1000,
    # or whatever the width and height is.
    aspect_ratio = dict(x=1.2,y=1.2,z=0.5)
    marg = dict(l=10,r=10,t=10,b=10,pad=0,autoexpand=True)
    #title="2D Deployment without Perturbations",
    layout = plotly.graph_objs.Layout(
             autosize=False,
             width=_layout_dim,
             height=_layout_dim,
             showlegend=False,
             scene=plotly.graph_objs.Scene(
             xaxis=plotly.graph_objs.XAxis(axis),
             yaxis=plotly.graph_objs.YAxis(axis),
             zaxis=plotly.graph_objs.ZAxis(z_axis),
             camera=camera,
             aspectratio = aspect_ratio,
             aspectmode = "manual",
            ),
         margin=marg,
        hovermode='closest',
       )


    #data=plotly.graph_objs.Data([trace_nodes, trace_bs] + mesh_list)
    data=plotly.graph_objs.Data([trace_nodes, trace_b2n_edges, trace_n2n_edges, trace_bs, trace_surface] + mesh_list) # trace_surface]  + mesh_list
    fig=plotly.graph_objs.Figure(data=data, layout=layout)

    plotly.offline.plot(fig, filename=figure_name + '.html')
