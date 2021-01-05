# -*- coding: utf-8 -*-
"""Experiments to improvement performance.

Testing:
    - Speed and lazy loading with dask-geopandas
    - Converting table/hdf datasets to netcdf grids
    - scattergl for large datasets
    - densitymapbox for large spatial datasets
    - dash datashader for rendering raster images   

Created on Sun Nov 22 10:30:54 2020

@author: travis
"""
import copy
import os

import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app import app, cache
from dash.dependencies import Input, Output, State
from .support import MAP_LAYOUT


SAMPLE = os.path.expanduser("~/github/reView/data/conus_sc.csv")
DF = pd.read_csv(SAMPLE, low_memory=False)


layout = html.Div(
    children=[

        # # Row 1        
        # html.Div([
        #     # DASH Density Map Box
        #     html.Div(
        #         id="density_map_div",
        #         className="six columns",
        #         children=dcc.Graph(id="density_map")
        #     ),
    
        #     # DASH ScatterGL
        #     html.Div(
        #         id="scattergl_map_div",
        #         className="six columns",
        #         children=dcc.Graph(id="scattergl_map")

        #     )
        # ]),

        # Row 2        
        html.Div([
            # DASH Scattergeo
            html.Div(
                id="scattergeo_map_div",
                className="six columns",
                children=dcc.Graph(id="scattergeo_map")
            )
        ]),





    ]
)


# @app.callback(Output("density_map", "figure"),
#               [Input("test_link_button", "n_clicks")])
# def density_map(n_clicks):
#     """Make a simple density mapbox figure."""
#     # Open data frame
#     df = DF.copy()
#     df["mean_cf_txt"] = df["mean_cf"].astype(str)
    
#     # Create data object
#     data = go.Densitymapbox(
#             lat=df['latitude'],
#             lon=df['longitude'],
#             z=df['mean_cf'],
#             radius=2,
#     )

#     # Set up layout
#     layout_copy = copy.deepcopy(MAP_LAYOUT)
#     layout_copy['titlefont'] = dict(color='white', size=20,
#                                     family='Time New Roman',
#                                     fontweight='bold')
#     layout_copy["dragmode"] = "select"
#     layout_copy['title']['text'] = "Density Mapbox"

#     figure = dict(data=[data], layout=layout_copy)

#     return figure


# @app.callback(Output("scattergl_map", "figure"),
#               [Input("test_link_button", "n_clicks")])
# def scattergl_map(n_clicks):
#     """Make a scattergl figure with no map to see how fast it is."""
#     # Open data frame
#     df = DF.copy()
#     df["mean_cf_txt"] = df["mean_cf"].astype(str)
    
#     # Create data object
#     data = go.Scattergl(
#         x=df["longitude"],
#         y=df["latitude"],
#         mode='markers',
#         text=df["mean_cf"],
#         marker=dict(color=df["mean_cf"],
#                     showscale=True,
#                     colorscale='Viridis'))

#     # Set up layout
#     layout_copy = copy.deepcopy(MAP_LAYOUT)
#     layout_copy['titlefont'] = dict(color='white', size=20,
#                                     family='Time New Roman',
#                                     fontweight='bold')
#     layout_copy["dragmode"] = "select"
#     layout_copy['title']['text'] = "ScatterGL"

#     figure = dict(data=[data], layout=layout_copy)

#     return figure


@app.callback(Output("scattergeo_map", "figure"),
              [Input("test_link_button", "n_clicks")])
def scattergeo_map(n_clicks):
    """Make a scattergeo figure with no map to see how fast it is."""
    # Open data frame
    df = DF.copy()
    df["mean_cf_txt"] = df["mean_cf"].astype(str)
    
    # Create data object
    data = go.Scattergeo(
        lon=df["longitude"],
        lat=df["latitude"],
        mode='markers',
        text=df["mean_cf"],
        marker=dict(color=df["mean_cf"],
                    showscale=True,
                    colorscale='Viridis'))

    # Set up layout
    layout_copy = copy.deepcopy(MAP_LAYOUT)
    layout_copy['titlefont'] = dict(color='white', size=20,
                                    family='Time New Roman',
                                    fontweight='bold')
    layout_copy["dragmode"] = "select"
    layout_copy['title']['text'] = "ScatterGeo"

    figure = dict(data=[data], layout=layout_copy)

    return figure
