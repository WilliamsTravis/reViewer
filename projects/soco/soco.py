# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import copy
import json
import os

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from dash.dependencies import Input, Output, State
from reviewer import print_args
from revruns import Data_Path
from support import BASEMAPS, BUTTON_STYLES, CHARTOPTIONS, COLOR_OPTIONS
from support import DATASETS, DEFAULT_MAPVIEW, MAPLAYOUT
from support import STYLESHEET, TITLES, TAB_STYLE, TABLET_STYLE, UNITS
from support import VARIABLES
from support import chart_point_filter, fix_cfs, get_label, make_scales
from support import get_boxplot, get_ccap, get_histogram, get_scatter

os.chdir(os.path.expanduser("~/github/reViewer/projects/soco"))


DP = Data_Path("./data")

FILES = DP.contents("*csv")

SCALES = make_scales(FILES, DP.join("scales.csv"))

fix_cfs(FILES)


app = dash.Dash(__name__, external_stylesheets=[STYLESHEET])
server = app.server
valid_auth_pairs = {'soco': 'Bbbmwshcd1.'}
auth = dash_auth.BasicAuth(app, valid_auth_pairs)


# Page Layout
app.layout = html.Div([

    # Navigation bar
    html.Nav(
        className="top-bar fixed",
        children=[

            html.Div([

              html.Div([
                  html.H1(
                      "reView",
                      style={
                         'float': 'left',
                         'position': 'relative',
                         "color": "white",
                         'font-family': 'Times New Roman',
                         'font-size': '48px',
                         "font-face": "bold",
                         "margin-bottom": 5,
                         "margin-left": 15,
                         "margin-top": 0
                         }
                  ),
                  html.H2(
                      " | Southern Company Preliminary Results",
                      style={
                        'float': 'left',
                        'position': 'relative',
                        "color": "white",
                        'font-family': 'Times New Roman',
                        'font-size': '36px',
                        "margin-bottom": 5,
                        "margin-left": 15,
                        "margin-top": 10,
                        "margin-right": 55
                        }
                    ),

                  ]),

              html.Button(
                    id='sync_variables',
                    children='Sync Variables: On',
                    n_clicks=1,
                    type='button',
                    title=('Click to sync the chosen variable between the map '
                           'and y-axis of the chart.'),
                    style=BUTTON_STYLES["on"]
                    ),

              html.Button(
                    id='rev_color',
                    children='Reverse Map Color: Off',
                    n_clicks=1,
                    type='button',
                    title=('Click to render the map with the inverse of '
                           'the chosen color ramp.'),
                    style=BUTTON_STYLES["on"]
                    ),

              html.Button(
                    id="reset_chart",
                    children="Reset Selections",
                    title="Clear Point Selection Filters.",
                    # style=BUTTON_STYLES["on"]
                    style={'display': 'none'}  # <----------------------------- Not ready yet, I have to cache the selections
                    ),

              html.A(
                html.Img(
                  src=("static/nrel_logo.png"),
                  className='twelve columns',
                  style={
                      'height': 70,
                      'width': 180,
                      "float": "right",
                      'position': 'relative',
                      "margin-left": "10",
                      'border-bottom-right-radius': '3px'
                      }
                ),
                href="https://www.nrel.gov/",
                target="_blank"
              )

              ],
                style={
                    'background-color': '#1663B5',
                    'width': '100%',
                    "height": 70,
                    'margin-right': '0px',
                    'margin-top': '-15px',
                    'margin-bottom': '35px',
                    'border': '3px solid #FCCD34',
                    'border-radius': '5px'
                    },
                className='row'),
        ]),

    html.Div([

        # MAP DIV
        html.Div([
            html.Div([

                # Map options
                dcc.Tabs(
                    id="map_options_tab",
                    value="hh",
                    style=TAB_STYLE,
                    children=[
                        dcc.Tab(value='hh',
                                label='Hub Height',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE
                                ),
                        dcc.Tab(value='variable',
                                label='Variable',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE),
                        dcc.Tab(value='basemap',
                                label='Basemap',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE),
                        dcc.Tab(value='color',
                                label='Color Ramp',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE)
                    ]),

                # Hub height dataset option
                html.Div(
                    id="hubheight_options_div",
                    children=[
                        dcc.Dropdown(
                            id="hubheight_options",
                            clearable=False,
                            options=DATASETS,
                            multi=False,
                            value=DP.join("120hh_20ps.csv")
                        )
                    ]),

                # Variable options
                html.Div(
                    id="map_variable_options_div",
                    children=[
                        dcc.Dropdown(
                            id="map_variable_options",
                            clearable=False,
                            options=VARIABLES,
                            multi=False,
                            value="mean_cf"
                        )
                    ]),

                # Basmap options
                html.Div(
                    id="basemap_options_div",
                    children=[
                         dcc.Dropdown(
                            id="basemap_options",
                            clearable=False,
                            options=BASEMAPS,
                            multi=False,
                            value="light"
                         )
                    ]),

                # Color scale options
                html.Div(
                    id="color_options_div",
                    children=[
                          dcc.Dropdown(
                            id="color_options",
                            clearable=False,
                            options=COLOR_OPTIONS,
                            multi=False,
                            value="Viridis"
                          )
                    ]),
            ], className="row"),

            # The map
            dcc.Graph(id="map", config={'showSendToCloud': True}),

            # Point Size
            html.Div(
                id="map_point_size_div",
                children=[
                    html.H6("Point Size:",
                            className="two columns"),
                    dcc.Input(
                        id="map_point_size",
                        value=5,
                        type="number",
                        className="two columns",
                        style={"margin-left": -5, "width": "7%"}
                    ),
                ], className="row"),
            ], className="six columns"),

        # Chart of cumulative cpacity vs LCOE
        html.Div([
            html.Div([
                html.Div([

                    # Chart options
                    dcc.Tabs(
                        id="chart_options_tab",
                        value="chart",
                        style=TAB_STYLE,
                        children=[
                            dcc.Tab(value='chart',
                                    label='Chart Type',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE
                                    ),
                            dcc.Tab(value='xvariable',
                                    label='X Variable',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE),
                            dcc.Tab(value='yvariable',
                                    label='Y Variable',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE)
                            ]),

                    # Type of chart
                    html.Div(
                        id="chart_options_div",
                        children=[
                            dcc.Dropdown(
                                id="chart_options",
                                clearable=False,
                                options=CHARTOPTIONS,
                                multi=False,
                                value="cumsum"
                            ),
                        ]),

                    # X-axis Variable
                    html.Div(
                        id="chart_xvariable_options_div",
                        children=[
                            dcc.Dropdown(
                                id="chart_xvariable_options",
                                clearable=False,
                                options=VARIABLES,
                                multi=False,
                                value="mean_cf"
                            ),
                        ]),

                    # Y-axis Variable
                    html.Div(
                        id="chart_yvariable_options_div",
                        children=[
                            dcc.Dropdown(
                                id="chart_yvariable_options",
                                clearable=False,
                                options=VARIABLES,
                                multi=False,
                                value="mean_cf"
                            ),
                        ]),
                    ]),

            ], className="row"),

            # The chart
            dcc.Graph(id="chart", config={'showSendToCloud': True}),

            # Point Size
            html.Div(
                id="chart_point_size_div",
                children=[
                    html.H6("Point Size:",
                            className="two columns"),
                    dcc.Input(
                        id="chart_point_size",
                        value=5,
                        type="number",
                        className="two columns",
                        style={"margin-left": -5, "width": "7%"}
                    ),
                ], className="row"),
            ], className="six columns"),

    ], className="row"),

    # To maintain the view after updating the map
    html.Div(id="mapview_store",
             children=json.dumps(DEFAULT_MAPVIEW),
             style={"display": "none"}),
    html.Div(id="chartview_store",
             children=json.dumps(DEFAULT_MAPVIEW),
             style={"display": "none"})
], className="row")


@app.callback([Output('hubheight_options_div', 'style'),
               Output('map_variable_options_div', 'style'),
               Output('basemap_options_div', 'style'),
               Output('color_options_div', 'style')],
              [Input('map_options_tab', 'value')])
def map_tab_options(tab_choice):
    """Choose which map tab dropdown to display."""
    styles = [{'display': 'none'}] * 4
    order = ["hh", "variable", "basemap", "color"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}

    return styles[0], styles[1], styles[2], styles[3]


@app.callback([Output('chart_options_tab', 'children'),
               Output('chart_options_div', 'style'),
               Output('chart_xvariable_options_div', 'style'),
               Output('chart_yvariable_options_div', 'style')],
              [Input('chart_options_tab', 'value'),
               Input('chart_options', 'value')])
def chart_tab_options(tab_choice, chart_choice):
    """Choose which map tab dropown to display."""
    styles = [{'display': 'none'}] * 3
    order = ["chart", "xvariable", "yvariable"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}

    # If Cumulative capacity only show the y variable
    if chart_choice in ["cumsum", "histogram", "box"]:
        children = [
            dcc.Tab(value='chart',
                    label='Chart Type',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE
                    ),
            dcc.Tab(value='yvariable',
                    label='Variable',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE)
            ]
    else:
        children = [
            dcc.Tab(value='chart',
                    label='Chart Type',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE
                    ),
            dcc.Tab(value='xvariable',
                    label='X Variable',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE),
            dcc.Tab(value='yvariable',
                    label='Y Variable',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE)
            ]

    return children, styles[0], styles[1], styles[2]


@app.callback([Output('sync_variables', 'children'),
               Output('sync_variables', 'style')],
              [Input('sync_variables', 'n_clicks')])
def toggle_sync_button(click):
    """Toggle Syncing on/off."""
    if not click:
        click = 0
    if click % 2 == 1:
        children = "Sync Variables: On"
        style = BUTTON_STYLES["on"]

    else:
        children = "Sync Variables: Off"
        style = BUTTON_STYLES["off"]

    return children, style,


@app.callback([Output('rev_color', 'children'),
               Output('rev_color', 'style')],
              [Input('rev_color', 'n_clicks')])
def toggle_rev_color_button(click):
    """Toggle Reverse Color on/off."""
    if not click:
        click = 0
    if click % 2 == 1:
        children = 'Reverse Map Color: Off'
        style = BUTTON_STYLES["off"]
        # style["width"] = "250px",

    else:
        children = 'Reverse Map Color: On'
        style = BUTTON_STYLES["on"]
        # style["width"] = "250px",

    return children, style


# @app.callback(Output("map_variable_options", "value"),
#               [Input("chart_yvariable_options", "value"),
#                Input("sync_variables", "n_clicks")])
# def sync_map(chart_selection, sync):
#     """If syncing is on, change the map value given chart input."""
#     if sync % 2 == 1:
#         return chart_selection


# @app.callback(Output("chart_yvariable_options", "value"),
#               [Input("map_variable_options", "value"),
#                Input("sync_variables", "n_clicks")])
# def sync_chart(map_selection, sync):
#     """If syncing is on, change the chart value given map input."""
#     if sync % 2 == 1:
#         return map_selection


@app.callback(
    [Output('map', 'figure'),
     Output("mapview_store", "children")],
    [Input("hubheight_options", "value"),
     Input("map_variable_options", "value"),
     Input("basemap_options", "value"),
     Input("color_options", "value"),
     Input("chart_yvariable_options", "value"),
     Input("chart", "selectedData"),
     Input("map_point_size", "value"),
     Input("rev_color", "n_clicks"),
     Input("reset_chart", "n_clicks"),
     Input("sync_variables", "n_clicks")],
    [State("map", "relayoutData")])
def make_map(hubheight, variable, basemap, color, chartvar, chartsel,
             point_size, rev_color, reset, sync_variable, mapview):
    """Make the scatterplot map."""
    # print_args(make_map, hubheight, variable, basemap, color, chartvar,
    #            chartsel, mapview, sync_variable, rev_color)

    trig = dash.callback_context.triggered[0]['prop_id']
    if sync_variable % 2 == 1:
        if "variable" in trig:
            if trig == "chart_yvariable_options.value":
                variable = chartvar

    # To save zoom levels and extent between map options (funny how this works)
    if not mapview:
        mapview = DEFAULT_MAPVIEW
    elif 'mapbox.center' not in mapview.keys():
        mapview = DEFAULT_MAPVIEW

    # Build the scatter plot data object
    df = pd.read_csv(hubheight)

    # Reset any previous selections
    # if "reset" in trig:
    #     chartsel = None

    # If there is a selection in the chart filter these points
    if chartsel:
        df = chart_point_filter(df, chartsel, chartvar)

    df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   " +
                  df[variable].round(2).astype(str) + " " + UNITS[variable])
    df = df[[variable, "latitude", "longitude", "text"]]

    if rev_color % 2 == 1:
        rev_color = False
    else:
        rev_color = True
    data = dict(type='scattermapbox',
                lon=df['longitude'],
                lat=df['latitude'],
                text=df['text'],
                mode='markers',
                hoverinfo='text',
                hovermode='closest',
                showlegend=False,
                marker=dict(
                    colorscale=color,
                    reversescale=rev_color,
                    color=df[variable],
                    cmin=SCALES[variable]["min"],
                    cmax=SCALES[variable]["max"],
                    opacity=1.0,
                    size=point_size,
                    colorbar=dict(
                        title=UNITS[variable],
                        dtickrange=SCALES[variable],
                        textposition="auto",
                        orientation="h",
                        font=dict(
                            size=15,
                            fontweight='bold')
                        )
                    )
                )

    # Set up layout
    title = TITLES[variable] + " - " + get_label(DATASETS, hubheight)
    layout_copy = copy.deepcopy(MAPLAYOUT)
    layout_copy['mapbox']['center'] = mapview['mapbox.center']
    layout_copy['mapbox']['zoom'] = mapview['mapbox.zoom']
    layout_copy['mapbox']['bearing'] = mapview['mapbox.bearing']
    layout_copy['mapbox']['pitch'] = mapview['mapbox.pitch']
    layout_copy['titlefont'] = dict(color='white', size=35,
                                    family='Time New Roman',
                                    fontweight='bold')
    layout_copy["dragmode"] = "select"
    layout_copy['title']['text'] = title
    layout_copy['mapbox']['style'] = basemap
    figure = dict(data=[data], layout=layout_copy)

    return figure, json.dumps(mapview)


@app.callback(
    Output('chart', 'figure'),
    [Input("chart_options", "value"),
     Input("chart_xvariable_options", "value"),
     Input("chart_yvariable_options", "value"),
     Input("map_variable_options", "value"),
     Input("map", "selectedData"),
     Input("chart_point_size", "value"),
     Input("reset_chart", "n_clicks"),
     Input("sync_variables", "n_clicks")],
    [State("map", "relayoutData")])
def make_chart(chart, x, y, mapvar, mapsel, point_size, reset, sync_variable,
               chartview):
    """Make one of a variety of charts."""
    print_args(make_chart, chart, x, y, mapvar, mapsel, point_size,
               sync_variable)

    trig = dash.callback_context.triggered[0]['prop_id']
    if sync_variable % 2 == 1:
        if "variable" in trig:
            if trig == "map_variable_options.value":
                y = mapvar

    # Reset any previous selections
    # if "reset" in trig:
    #     mapsel = None

    # Only the 20MW plant for now
    files = [f for f in FILES if "20ps" in f]
    files.sort()
    paths = {os.path.splitext(os.path.basename(f))[0][:3]: f for f in files}

    # Get the initial figure
    if chart == "cumsum":
        fig = get_ccap(paths, y, mapsel, int(point_size))
    elif chart == "scatter":
        fig = get_scatter(paths, x, y, mapsel, int(point_size))
    elif chart == "histogram":
        fig = get_histogram(paths, y, mapsel, int(point_size))
    elif chart == "box":
        fig = get_boxplot(paths, y, mapsel, int(point_size))

    # Update the layout and traces
    fig.update_layout(
        font_family="Time New Roman",
        title_font_family="Times New Roman",
        legend_title_font_color="white",
        font_color="white",
        title_font_size=35,
        font_size=15,
        margin=dict(l=70, r=20, t=70, b=20),
        height=500,
        paper_bgcolor="#1663B5",
        legend_title_text='Hub Height',
        dragmode="select",
        title=dict(
                yref="paper",
                y=1,
                x=0.1,
                yanchor="bottom",
                pad=dict(b=10)
                ),
        legend=dict(
            title_font_family="Times New Roman",
            font=dict(
               family="Times New Roman",
               size=15,
               color="white"
               )
           )
        )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server()
