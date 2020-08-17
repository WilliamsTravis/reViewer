# -*- coding: utf-8 -*-
"""
Minimal working scattermapbox DASH portal.

This is a temporary script file.
"""

import copy
import gc
import json
import os
import warnings

from glob import glob

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask_caching import Cache
from pandas.core.common import SettingWithCopyWarning

from reviewer import Data_Path, print_args, value_map
from reviewer.options import BASEMAPS, COLORSCALES, DATAFOLDERS, ZOOMLEVELS
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

app = dash.Dash(__name__)
server = app.server
cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'data/cache',
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
            id="project",
            clearable=False,
            options=DATAFOLDERS,
            multi=False,
            value="ipm_wind_florida",
            style={"width": "50%", "float": "left"}
        )
      ],
      className="row"
    ),
    html.Div([
      dcc.Graph(id="map",
                config={'showSendToCloud': True})]),
    html.Div(id="mapview_store", children=json.dumps(DEFAULT_MAPVIEW))
])


def zoom_data(project, mapview_store, mapview, trig):
    """For a mapbox element, take it's current mapdata (zoom, pitch,
    center point, etc.) along with its previous mapdata, determine if the
    floor-level zoom value has changed, and, if so, trigger a map update
    with the appropriate zoom-dependent dataset.

    Parameters
    ----------
    project : str
        A path to the chosen project folder. This contains the set of
        varying resolution datasets. 
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

    print_args(zoom_data, project, mapview_store, mapview, trig)

    # We need to assign a file to each possible zoom level
    files = glob(DP.join(project, "*nc"))

    # Get the shared base name
    filebase = os.path.commonprefix(files)
    if filebase[-1] == "_":
        filebase = filebase[:-1]
 
    # Get zoom - dataset assignments
    datasets = {i: filebase + "_{}.nc".format(v) for i, v in ZOOMLEVELS.items()}

    # If trigger was zoom, but it didn't change enough, don't update
    zoom_store = np.floor(mapview_store["mapbox.zoom"])
    if "relayoutData" in trig:
        if "mapbox.zoom" in mapview:
            zoomscale = np.floor(mapview["mapbox.zoom"])
            if zoomscale == zoom_store:
                raise PreventUpdate
            else:
                print("Update triggered by zoom level!")
        else:
            zoomscale = zoom_store
    else:
        zoomscale = zoom_store

    # Get the right zoom-level file for the given project
    file = datasets[int(zoomscale)]

    return file


@app.callback([Output("map", 'figure'),
               Output("mapview_store", "children")],
              [Input("project", "value"),
               Input("color", "value"),
               Input("basemap", "value"),
               Input("map", "relayoutData")],
              [State("mapview_store", "children")])
def makeMap(project, color, basemap, mapview, mapview_store):
    """Starting with just a sample supply curve file and a basemap
    """
    
    # Print sample arguments
    print_args(makeMap, project, color, basemap, mapview, mapview_store)

    # Get the upate triggering elemet name
    trig = dash.callback_context.triggered[0]['prop_id']
    print("trig = " + "'" + trig + "'")

    # Extract saved mapdata
    if mapview_store == '{"autosize": true}':
        mapview_store = DEFAULT_MAPVIEW
    elif mapview_store == 'null':
        mapview_store = DEFAULT_MAPVIEW
    else:
        mapview_store = json.loads(mapview_store)

    # In the future we'll use the output of this function
    data_path = zoom_data(project, mapview_store, mapview, trig)

    # Create a data frame of coordinates, index values, labels, etc
    df = value_map(data_path, "mean")
    df["hovertext"] = df["value_mean"].round(4).astype(str)

    # Create the scattermapbox object
    data = dict(type='scattermapbox',
                lon=df['lon'],
                lat=df['lat'],
                text=df['hovertext'],
                mode='markers',
                hoverinfo='text',
                hovermode='closest',
                showlegend=False,
                marker=dict(colorscale=color,
                            reversescale=False,
                            color=df['value_mean'],
                            # cmax=0.4,
                            # cmin=0.23,
                            opacity=1.0,
                            size=8,
                            colorbar=dict(textposition="auto",
                                          orientation="h",
                                          font=dict(size=15,
                                                    fontweight='bold'))))

    # Set up layout
    layout_copy = copy.deepcopy(MAPLAYOUT)
    # layout_copy['title'] = "Florida Capacity Factors"
    if mapview and "mapbox.center" in mapview:
        layout_copy['mapbox']['center'] = mapview['mapbox.center']
        layout_copy['mapbox']['zoom'] = mapview['mapbox.zoom']
        layout_copy['mapbox']['bearing'] = mapview['mapbox.bearing']
        layout_copy['mapbox']['pitch'] = mapview['mapbox.pitch']
    figure = dict(data=[data], layout=layout_copy)

    # Clear memory space
    gc.collect()

    # Check on Memory
    # cpu = psutil.cpu_percent()
    # memory = psutil.virtual_memory().percent
    # print("\nCPU: {}% \nMemory: {}%\n".format(cpu, memory))

    return figure, json.dumps(mapview)

                
if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()
