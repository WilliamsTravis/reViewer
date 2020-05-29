# -*- coding: utf-8 -*-
"""
Minimal working scattermapbox DASH portal.

This is a temporary script file.
"""

import copy
import gc
import json
import psutil
import warnings

import dash
import dash_core_components as dcc
import dash_html_components as html
import h5py
import numpy as np
import pandas as pd

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask_caching import Cache
from pandas.core.common import SettingWithCopyWarning
from reviewer import Data_Path
from reviewer.options import BASEMAPS, COLORSCALES, FILES
from reviewer.mapbox import MAPLAYOUT
from reviewer.navbar import NAVBAR


warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


# Data path object, data can be anywhere on the filesystem
DP = Data_Path("~/github/reViewer/data")

# Initial Map View Values
DEFAULT_MAPVIEW = {
    "mapbox.center": {"lon": -80, "lat": 30},
    "mapbox.zoom": 2.5,
    "mapbox.bearing": 0,
    "mapbox.pitch": 0
}

# Zoom-dependent data sets
ZOOM_DATASETS = {
    1: DP.join("Dataset_1.csv"),
    2: DP.join("dataset_2.csv"),
    3: DP.join("dataset_3.csv"),
    4: DP.join("dataset_4.csv"),
    5: DP.join("dataset_5.csv")
}


app = dash.Dash(__name__)
server = app.server

cache = Cache(config={'CACHE_TYPE': 'filesystem',
                      'CACHE_DIR': 'data/cache',
                      'CACHE_THRESHOLD': 2})
cache.init_app(server)


app.layout = html.Div([
    NAVBAR,
    html.Div(
        className="app-header",
        children=[
            html.Div("reViewer Mapbox Test bed")
        ]
    ),
    html.Div(
      id="options",
      children=[
        dcc.Dropdown(
            id='basemap',
            clearable=False,
            options=BASEMAPS,
            multi=False,
            value="satellite-streets",
            style={"width": "50%", "float": "left"}
        ),        
        dcc.Dropdown(
            id="color",
            clearable=False,
            options=COLORSCALES,
            multi=False,
            value="Viridis",
            style={"width": "50%", "float": "left"}
        ),
        dcc.Dropdown(
            id="file",
            clearable=False,
            options=FILES,
            multi=False,
            value="florida_sc.csv",
            style={"width": "50%", "float": "left"}
        )
      ],
      className="row"
    ),
    html.Div([
      dcc.Graph(id="map",
                config={'showSendToCloud': True})]),
    html.Div(id="mapdata_store", children=json.dumps(DEFAULT_MAPVIEW))
])


def zoom_data(mapview_store, mapview, trig):
    """For a mapbox element, take it's current mapdata (zoom, pitch,
    center point, etc.) along with its previous mapdata, determine if the
    floor-level zoom value has changed, and, if so, trigger a map update
    with the appropriate zoom-dependent dataset.

    Parameters
    ----------
    mapview_store : dict
        A dictionary object return from an html div storing a previously-
        triggered mapbox mapdata dictionary.
    mapview : dict
        A dictionary containg mapbox mapdata from the most recently
        triggered render.
    trig : str
        A string indicating which Dash element triggered the last mapbox
        update.

    Returns
    -------
    pd.core.frame.DataFrame
        A pandas data frame.
    """

    # If trigger was zoom, but it didn't change enough, don't update
    if "relayoutData" in trig:
        if "mapbox.zoom" in mapview:
            # print("\nZOOM: " + str(round(mapview["mapbox.zoom"], 2)) + "\n")
            zoom_store = np.floor(mapview_store["mapbox.zoom"])
            zoom = np.floor(mapview["mapbox.zoom"])
            if zoom == zoom_store:
                raise PreventUpdate
            else:
                print("Update triggered by zoom level!")
        else:
            zoom = zoom_store
    else:
        zoom = zoom_store

    # dataset = pd.read_csv(ZOOM_DATASETS[zoom], low_memory=False)
    dataset = ZOOM_DATASETS[zoom]

    return dataset

     
@app.callback([Output("map", 'figure'),
               Output("mapdata_store", "children")],
              [Input("file", "value"),
               Input("color", "value"),
               Input("basemap", "value"),
               Input("map", "relayoutData")],
              [State("mapdata_store", "children")])
def makeMap(file, color, basemap, mapview, mapview_store):
    """Starting with just a sample supply curve file and a basemap

    map_type = "satellite-streets"
    file = DP.join("outputs_sc.csv")
    """

    # Get the upate triggering elemet name
    trig = dash.callback_context.triggered[0]['prop_id']

    # Extract saved mapdata
    if mapview_store == '{"autosize": true}':
        mapview_store = DEFAULT_MAPVIEW
    else:
        mapview_store = json.loads(mapview_store)

    # In the future we'll use the output of this function
    future_dataset = zoom_data(mapview_store, mapview, trig)
    print("DATASET USED: " + future_dataset)

    # Create a data frame of coordinates, index values, labels, etc
    df = pd.read_csv(DP.join(file), low_memory=False)
    df["hovertext"] = (df["county"] + " County, " + df["state"] + "<br>" +
                       df["latitude"].round(2).astype(str) + ", " +
                       df["longitude"].round(2).astype(str) + "<br>" +
                       df["mean_cf"].round(4).astype(str))
    df["hovertext"][
        pd.isnull(df["hovertext"])] = df["mean_cf"].round(4).astype(str)

    # Create the scattermapbox object
    data = dict(type='scattermapbox',
              lon=df['longitude'],
              lat=df['latitude'],
              text=df['hovertext'],
              mode='markers',
              hoverinfo='text',
              hovermode='closest',
              showlegend=False,
              marker=dict(colorscale=color,
                          reversescale=False,
                          color=df['mean_cf'],
                          cmax=0.4,
                          cmin=0.23,
                          opacity=1.0,
                          size=8,
                          colorbar=dict(textposition="auto",
                                        orientation="h",
                                        font=dict(size=15,
                                                  fontweight='bold'))))

    # Set up layout
    layout_copy = copy.deepcopy(MAPLAYOUT)
    layout_copy['title'] = "Florida Capacity Factors"
    if mapview and "mapbox.center" in mapview:
        layout_copy['mapbox']['center'] = mapview['mapbox.center']
        layout_copy['mapbox']['zoom'] = mapview['mapbox.zoom']
        layout_copy['mapbox']['bearing'] = mapview['mapbox.bearing']
        layout_copy['mapbox']['pitch'] = mapview['mapbox.pitch']
    figure = dict(data=[data], layout=layout_copy)

    # Clear memory space
    gc.collect()

    # Check on Memory
    # print("\nCPU: {}% \nMemory: {}%\n".format(psutil.cpu_percent(),
    #                                 psutil.virtual_memory().percent))

    return figure, json.dumps(mapview)


                
if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()
