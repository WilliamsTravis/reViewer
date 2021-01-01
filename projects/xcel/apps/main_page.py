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

from app import app
from dash.dependencies import Input, Output, State
from review import print_args
from revruns.rr import Data_Path
from .support import (BASEMAPS, BUTTON_STYLES, CHART_OPTIONS, COLOR_OPTIONS,
                      DATAKEYS, DATASETS, DEFAULT_MAPVIEW, MAP_LAYOUT,
                      STYLESHEET, TITLES, TAB_STYLE,
                      TABLET_STYLE, UNITS, VARIABLES)
from .support import (chart_point_filter, fix_cfs, get_label, make_scales,
                      get_boxplot, get_ccap, get_histogram, get_scatter)

os.chdir(os.path.expanduser("~/github/reView/projects/xcel"))


DP = Data_Path("~/github/reView/projects/xcel/data")  # <-------------------- Fix this
FILES = DP.contents("*csv")
SCALES = make_scales(FILES, DP.join("scales.csv"))

fix_cfs(FILES)

layout = html.Div(
    children=[

        html.Div([

            # MAP DIV
            html.Div([
                html.Div([

                    # Map options
                    dcc.Tabs(
                        id="map_options_tab",
                        value="land_use",
                        style=TAB_STYLE,
                        children=[
                            dcc.Tab(value='land_use',
                                    label='Land Use Scenario',
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
                        id="land_use_options_div",
                        children=[
                            dcc.Dropdown(
                                id="land_use_options",
                                clearable=False,
                                options=DATAKEYS,
                                multi=False,
                                value="liberal"
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
                dcc.Graph(id="map",
                          config={
                            "showSendToCloud": True,
                            "plotlyServerURL":
                                "https://chart-studio.plotly.com"
                             }
                          ),

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
                                    options=CHART_OPTIONS,
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
                dcc.Graph(id="chart",
                          config={
                            "showSendToCloud": True,
                            "plotlyServerURL": "https://chart-studio.plotly.com"
                          }),

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
             style={"display": "none"}),

    html.Div(id="map_selection_store",
             style={"display": "None"}),

    html.Div(id="chart_selection_store",
             style={"display": "None"})

    ], className="twelve columns")


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


@app.callback([Output('land_use_options_div', 'style'),
               Output('map_variable_options_div', 'style'),
               Output('basemap_options_div', 'style'),
               Output('color_options_div', 'style')],
              [Input('map_options_tab', 'value')])
def map_tab_options(tab_choice):
    """Choose which map tab dropdown to display."""
    styles = [{'display': 'none'}] * 4
    order = ["land_use", "variable", "basemap", "color"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}

    return styles[0], styles[1], styles[2], styles[3]


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

    else:
        children = 'Reverse Map Color: On'
        style = BUTTON_STYLES["on"]

    return children, style


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


@app.callback(
    [Output('map', 'figure'),
     Output("mapview_store", "children"),
     Output("map_selection_store", "children")],
    [Input("land_use_options", "value"),
     Input("map_variable_options", "value"),
     Input("basemap_options", "value"),
     Input("color_options", "value"),
     Input("chart_yvariable_options", "value"),
     Input("chart", "selectedData"),
     Input("map_point_size", "value"),
     Input("rev_color", "n_clicks"),
     Input("reset_chart", "n_clicks")],
    [State("map", "relayoutData"),
     State("map_selection_store", "children"),
     State("sync_variables", "n_clicks"),
     State("map", "selectedData")])
def make_map(land_use, variable, basemap, color, chartvar,
             chartsel, point_size, rev_color, reset, mapview, stored_variable,
             sync_variable, mapsel):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    # print_args(make_map, hubheight, plantsize, variable, state, basemap,
    #            color, chartvar, chartsel,  point_size, rev_color, reset,
    #            mapview, stored_variable, sync_variable, mapsel, ps_state)

    trig = dash.callback_context.triggered[0]['prop_id']
    print(trig)
    if sync_variable % 2 == 1:
        if "variable" in trig:
            if trig == "chart_yvariable_options.value":
                variable = chartvar
            elif trig == "map_variable_options.value":
                variable = variable
            else:
                variable = stored_variable

    # To save zoom levels and extent between map options (funny how this works)
    if not mapview:
        mapview = DEFAULT_MAPVIEW
    elif 'mapbox.center' not in mapview.keys():
        mapview = DEFAULT_MAPVIEW

    # Build the scatter plot data object
    df = DATASETS[land_use].copy()

    if rev_color % 2 == 1:
        rev_color = True
    else:
        rev_color = False

    if "reset" not in trig:
        # If there is a selection in the chart filter these points
        if chartsel:
            df = chart_point_filter(df, chartsel, chartvar)

        if "selectedData" not in trig:
            if mapsel:
                idx = [p["pointIndex"] for p in mapsel["points"]]
                df = df.loc[idx]

    df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   " +
                  df[variable].round(2).astype(str) + " " + UNITS[variable])
    df = df[[variable, "latitude", "longitude", "text"]]

    # Reverse color is from a button (number of clicks)
    if rev_color % 2 == 1:
        rev_color = False
    else:
        rev_color = True

    # Create data object
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
    title = (TITLES[variable] + " - "
             + get_label(DATAKEYS, land_use))
    layout_copy = copy.deepcopy(MAP_LAYOUT)
    layout_copy['mapbox']['center'] = mapview['mapbox.center']
    layout_copy['mapbox']['zoom'] = mapview['mapbox.zoom']
    layout_copy['mapbox']['bearing'] = mapview['mapbox.bearing']
    layout_copy['mapbox']['pitch'] = mapview['mapbox.pitch']
    layout_copy['titlefont'] = dict(color='white', size=25,
                                    family='Time New Roman',
                                    fontweight='bold')
    layout_copy["dragmode"] = "select"
    layout_copy['title']['text'] = title
    layout_copy['mapbox']['style'] = basemap
    figure = dict(data=[data], layout=layout_copy)

    return figure, json.dumps(mapview), variable


@app.callback(
    [Output('chart', 'figure'),
     Output("chart_selection_store", "children")],
    [Input("chart_options", "value"),
     Input("chart_xvariable_options", "value"),
     Input("chart_yvariable_options", "value"),
     Input("map_variable_options", "value"),
     Input("map", "selectedData"),
     Input("chart_point_size", "value"),
     Input("reset_chart", "n_clicks")],
    [State("map", "relayoutData"),
     State("chart_selection_store", "children"),
     State("sync_variables", "n_clicks"),
     State("chart", "selectedData")])
def make_chart(chart, x, y, mapvar, mapsel, point_size, reset,
               chartview, stored_variable, sync_variable, chartsel):
    """Make one of a variety of charts."""
    # print_args(make_chart, chart, ps, x, y, mapvar, state, mapsel,
    #            point_size, sync_variable)

    trig = dash.callback_context.triggered[0]['prop_id']
    if sync_variable % 2 == 1:
        if "variable" in trig:
            # if ps != int(ps_state):
            #     print("PS MISMATCH")
            #     y = mapvar
            if trig == "map_variable_options.value":
                y = mapvar
            elif trig == "chart_yvariable_options.value":
                y = y
            else:
                y = stored_variable

    # Only the 20MW plant for now
    paths = {"liberal": "liberal",
             "moderate": "moderate",
             "conservative": "conservative"
             }

    # Get the initial figure
    if chart == "cumsum":
        fig = get_ccap(paths, y, mapsel, int(point_size), reset, trig)
        title = (get_label(VARIABLES, y)
                 + " by Cumulative Capacity ")

    elif chart == "scatter":
        fig = get_scatter(paths, x, y, mapsel, int(point_size), reset,
                          trig)
        title = (get_label(VARIABLES, y)
                 + " by "
                 + get_label(VARIABLES, x))

    elif chart == "histogram":
        fig = get_histogram(paths, y, mapsel, int(point_size), reset,
                            trig)
        title = (get_label(VARIABLES, y) + " Histogram")

    elif chart == "box":
        fig = get_boxplot(paths, y, mapsel, int(point_size), reset,
                          trig)
        title = (get_label(VARIABLES, y) + " Boxplots")

    # Update the layout and traces
    fig.update_layout(
        font_family="Time New Roman",
        title_font_family="Times New Roman",
        legend_title_font_color="white",
        font_color="white",
        title_font_size=25,
        font_size=15,
        margin=dict(l=70, r=20, t=70, b=20),
        height=500,
        paper_bgcolor="#1663B5",
        legend_title_text='Hub Height',
        dragmode="select",
        title=dict(
                text=title,
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

    return fig, y
