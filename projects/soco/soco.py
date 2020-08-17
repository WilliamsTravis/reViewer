# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import copy
import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from dash.dependencies import Input, Output, State
from reviewer import print_args
from revruns import Data_Path
from support import BASEMAPS, MAPLAYOUT, TITLES, UNITS, STYLESHEET
from support import make_scales, get_label


DP = Data_Path("./data")

FILES = DP.contents("*csv")

SCALES = make_scales(FILES, DP.join("scales.csv"))

DEFAULT_MAPVIEW = {
    "mapbox.center": {
        "lon": -85,
        "lat": 32.5
    },
    "mapbox.zoom": 5.0,
    "mapbox.bearing": 0,
    "mapbox.pitch": 0
}

DATASETS = [{"label": "120m Hub Height", "value": DP.join("120hh_20ps.csv")},
            {"label": "140m Hub Height", "value": DP.join("140hh_20ps.csv")},
            {"label": "160m Hub Height", "value": DP.join("160hh_20ps.csv")}]

VARIABLES = [{"label": "Capacity", "value": "capacity"},
             {"label": "Site-Based LCOE", "value": "mean_lcoe"},
             {"label": "LCOT", "value": "lcot"},
             {"label": "Total LCOE", "value": "total_lcoe"}]

CHARTOPTIONS = [{"label": "Cumulative Capacity", "value": "cumsum"}]

LCOEOPTIONS = [{"label": "Site-Based", "value": "mean_lcoe"},
               {"label": "Transmission", "value": "lcot"},
               {"label": "Total", "value": "total_lcoe"}]

app = dash.Dash(__name__, external_stylesheets=[STYLESHEET])


# Page Layout
app.layout = html.Div([
 
    # Map of Capacity Factors / LCOE    
    html.Div([
        html.Div([
            html.Div([
                # html.H5("Turbine Hub Height", className="four columns"),
                dcc.Dropdown(
                    id="map_options",
                    clearable=False,
                    options=DATASETS,
                    multi=False,
                    value=DP.join("120hh_20ps.csv"),
                    className="four columns",
                    style={"width": "100%"})
            ]),
            html.Div([
                # html.H5("Variable", className="four columns"),
                dcc.Dropdown(
                    id="variable_options",
                    clearable=False,
                    options=VARIABLES,
                    multi=False,
                    value="capacity",
                    className="four columns",
                    style={"width": "100%"})
            ]),
            html.Div([
                 # html.H5("Basemap", className="four columns"),
                 dcc.Dropdown(
                    id="basemap_options",
                    clearable=False,
                    options=BASEMAPS,
                    multi=False,
                    value="light",
                    className="four columns",
                    style={"width": "100%"})            
            ]),
        ], className="row"),
        dcc.Graph(
            id="map",
        )], className="six columns"),

    # Chart of cumulative cpacity vs LCOE
    html.Div([
        html.Div([
            dcc.Dropdown(
                id="chart_options",
                clearable=False,
                options=CHARTOPTIONS,
                multi=False,
                value="cumsum",
                className="four columns",
                style={"width": "100%"}),
            dcc.Dropdown(
                id="lcoe_options",
                clearable=False,
                options=LCOEOPTIONS,
                multi=False,
                value="total_lcoe",
                className="four columns",
                style={"width": "100%"}),
            ], className="row"),
         dcc.Graph(
            id="chart",
        )], className="six columns"),

    # To maintain the view after updating the map
    html.Div(id="mapview_store", 
             children=json.dumps(DEFAULT_MAPVIEW),
             style={"display": "none"})
], className="row")
    

@app.callback(
    [Output('map', 'figure'),
     Output("mapview_store", "children")],
    [Input("map_options", "value"),
     Input("variable_options", "value"),
     Input("basemap_options", "value")],
    [State("map", "relayoutData")])
def make_map(selection, variable, basemap, mapview):

    
    print_args(make_map, selection, variable, basemap, mapview)

    # To save zoom levels and extent between map options (funny how this works)
    if not mapview:
        mapview = DEFAULT_MAPVIEW
    elif 'mapbox.center' not in mapview.keys():
        mapview = DEFAULT_MAPVIEW


    # Build the scatter plot data object
    df = pd.read_csv(selection)
    df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   " +
                  df[variable].round(2).astype(str) + " " + UNITS[variable])
    df = df[[variable, "latitude" ,"longitude", "text"]]
    data = dict(type='scattermapbox',
                lon=df['longitude'],
                lat=df['latitude'],
                text=df['text'],
                mode='markers',
                hoverinfo='text',
                hovermode='closest',
                showlegend=False,
                marker=dict(colorscale="Viridis",
                            reversescale=False,
                            color=df[variable],
                            cmax=SCALES[variable]["min"],
                            cmin=SCALES[variable]["max"],
                            opacity=1.0,
                            size=5,
                            colorbar=dict(title=UNITS[variable],
                                          dtickrange=SCALES[variable],
                                          textposition="auto",
                                          orientation="h",
                                          font=dict(size=15,
                                                    fontweight='bold')))
                )

    # Set up layout
    title = TITLES[variable] + " - " + get_label(DATASETS, selection)
    layout_copy = copy.deepcopy(MAPLAYOUT)
    layout_copy['mapbox']['center'] = mapview['mapbox.center']
    layout_copy['mapbox']['zoom'] = mapview['mapbox.zoom']
    layout_copy['mapbox']['bearing'] = mapview['mapbox.bearing']
    layout_copy['mapbox']['pitch'] = mapview['mapbox.pitch']
    layout_copy['titlefont']=dict(color='#CCCCCC', size=35,
                                  family='Time New Roman',
                                  fontweight='bold')
    layout_copy['title'] = title
    layout_copy['mapbox']['style'] = basemap
    figure = dict(data=[data], layout=layout_copy)

    return figure, json.dumps(mapview)


   
@app.callback(
    Output('chart', 'figure'),
    [Input("map_options", "value"),
     Input("lcoe_options", "value")])
def make_chart(selection, lcoe):

    print_args(make_chart, selection, lcoe)

    # Only the 20MW plant for now
    files = [f for f in FILES if "20ps" in f]
    files.sort()
    paths = {os.path.splitext(os.path.basename(f))[0][:3]: f for f in files}

    df = None
    for key, path in paths.items():
        if df is None:
            df = pd.read_csv(path)[["capacity", lcoe]]
            df = df.sort_values(lcoe)
            df["ccap"] = df["capacity"].cumsum()
            df["value"] = df[lcoe].expanding().mean()
            df["hh"] = key
            df = df[["ccap", "value", "hh"]]
        else:
            df2 = pd.read_csv(path)[["capacity", lcoe]]
            df2 = df2.sort_values(lcoe)
            df2["hh"] = key
            df2["ccap"] = df2["capacity"].cumsum()
            df2["value"] = df2[lcoe].expanding().mean()
            df2["hh"] = key
            df2 = df2[["ccap", "value", "hh"]]
            df = pd.concat([df, df2])

    df = df.sort_values("ccap")

    fig = px.line(df,
                  x="ccap",
                  y="value",
                  title=(TITLES[lcoe] + " by Cumulative Capacity"),
                  labels={"ccap": UNITS["capacity"], "value": UNITS[lcoe]},
                  color='hh')

    fig.update_layout(uniformtext_minsize=35, uniformtext_mode='hide')



    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server()



# def cap(files):
#     """How to convey capacity vs lcoe for all 6? Better start with just the
#     three."""


    


# def main():

#     # Cumulative Capacity vs LCOE
#     files = DP.contents("*20ps*csv")

    