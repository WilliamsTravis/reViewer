# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import copy
import json
import os

from glob import glob

import dash
import dash_core_components as dcc
import dash_html_components as html

from app import app
from dash.dependencies import Input, Output, State
from review import print_args, Data_Path
from .support import (BASEMAPS, BUTTON_STYLES, CHART_OPTIONS, COLOR_OPTIONS,
                      DATAKEYS, DATASETS, DEFAULT_MAPVIEW, MAP_LAYOUT,
                      PS_OPTIONS, STATES, STYLESHEET, TITLES, TAB_STYLE,
                      TABLET_STYLE, UNITS, VARIABLES)
from .support import (chart_point_filter, fix_cfs, get_label, make_scales,
                      get_boxplot, get_ccap, get_histogram, get_scatter)

os.chdir(os.path.expanduser("~/github/reView/projects/soco"))


DP = Data_Path("~/github/reView/projects/soco/data")  # <---------------------- Fix these paths
FILES = DP.contents("*.csv")
SCALES = make_scales(FILES, DP.join("scales.csv"))
fix_cfs(FILES)


layout = html.Div(
    children=[

        html.Div([
            html.Div([
                html.H4("Project"),
                dcc.Dropdown(
                    id="project",
                    options=[{"label": "Southern Company", "value": "soco"}],
                    placeholder="Choose reV Project",
                    value="soco"
                    )
                ], className="three columns"
            ),

            # Variable options
            html.Div(
                id="variable_options_div",
                children=[
                    html.H4("Variable"),
                    dcc.Dropdown(
                        id="variable_options",
                        clearable=False,
                        options=VARIABLES,
                        multi=False,
                        value="total_lcoe"
                    )
                ], className="three columns"
            ),

        ], className="row", style={"width": "75%",
                                   "margin-bottom": "50px"}),

        html.Div([

            # MAP DIV
            html.Div([
                html.Div([

                    # Map options
                    dcc.Tabs(
                        id="map_options_tab",
                        value="state",
                        style=TAB_STYLE,
                        children=[
                            dcc.Tab(value='state',
                                    label='State',
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

                    # State options
                    html.Div(
                        id="state_options_div",
                        children=[
                            dcc.Dropdown(
                                id="state_options",
                                clearable=True,
                                options=STATES,
                                multi=True,
                                value=None
                            )
                        ]),

                    # Basemap options
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
                dcc.Graph(
                    id="map",
                    config={
                        "showSendToCloud": True,
                        "plotlyServerURL": "https://chart-studio.plotly.com"
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
                            value=3,
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
                        ]),

                ], className="row"),

                # The chart
                dcc.Graph(
                    id="chart",
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
        html.Div(id="plantsize_store",
                 children="20",
                 style={"display": "none"})

    ], className="twelve columns")


@app.callback([Output('chart_options_tab', 'children'),
               Output('chart_options_div', 'style'),
               Output('chart_xvariable_options_div', 'style')],
              [Input('chart_options_tab', 'value'),
               Input('chart_options', 'value')])
def chart_tab_options(tab_choice, chart_choice):
    """Choose which map tab dropown to display."""
    styles = [{'display': 'none'}] * 2
    order = ["chart", "xvariable"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}

    # If Cumulative capacity only show the y variable
    if chart_choice in ["cumsum", "histogram", "box"]:
        children = [
            dcc.Tab(value='chart',
                    label='Chart Type',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE
                    )
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
                    selected_style=TABLET_STYLE)
            ]

    return children, styles[0], styles[1]


@app.callback([Output("state_options", "style"),
               Output('basemap_options_div', 'style'),
               Output('color_options_div', 'style')],
              [Input('map_options_tab', 'value')])
def map_tab_options(tab_choice):
    """Choose which map tab dropdown to display."""
    styles = [{'display': 'none'}] * 3
    order = ["state", "basemap", "color"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}

    return styles[0], styles[1], styles[2]


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


@app.callback([Output("hubheight_options", "options"),
               Output("hubheight_options", "value")],
              [Input("plant_size_options", "value")],
              [State("hubheight_options", "value")])
def set_plant_size(ps, hh):
    """Set the hubheight dataset options according to the plant size."""
    if "winner" in hh:
        hh = "lcoe_winner_{}ps".format(ps)
    else:
        hh = hh[:6] + str(ps) + hh[-2:]

    return DATAKEYS[ps], hh


@app.callback(
    [Output('map', 'figure'),
     Output("mapview_store", "children")],
    [Input("hubheight_options", "value"),
     Input("plant_size_options", "value"),
     Input("variable_options", "value"),
     Input("state_options", "value"),
     Input("basemap_options", "value"),
     Input("color_options", "value"),
     Input("chart", "selectedData"),
     Input("map_point_size", "value"),
     Input("rev_color", "n_clicks"),
     Input("reset_chart", "n_clicks")],
    [State("map", "relayoutData"),
     State("map", "selectedData"),
     State("plantsize_store", "children")])
def make_map(hubheight, plantsize, variable, state, basemap, color, chartsel,
             point_size, rev_color, reset, mapview, mapsel, ps_state):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    # print_args(make_map, hubheight, plantsize, variable, state, basemap,
    #            color, chartvar, chartsel,  point_size, rev_color, reset,
    #            mapview, stored_variable, sync_variable, mapsel, ps_state)

    trig = dash.callback_context.triggered[0]['prop_id']

    # To save zoom levels and extent between map options (funny how this works)
    if not mapview:
        mapview = DEFAULT_MAPVIEW
    elif 'mapbox.center' not in mapview.keys():
        mapview = DEFAULT_MAPVIEW

    # Build the scatter plot data object
    df = DATASETS[hubheight].copy()

    if rev_color % 2 == 1:
        rev_color = True
    else:
        rev_color = False

    if "reset" not in trig:
        # If there is a selection in the chart filter these points
        if chartsel:
            df = chart_point_filter(df, chartsel, variable)

        if "selectedData" not in trig:
            if mapsel:
                idx = [p["pointIndex"] for p in mapsel["points"]]
                df = df.loc[idx]

        # Finally filter for states
        if state:
            df = df[df["state"].isin(state)]

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
    title = (TITLES[variable]
             + " - "
             + get_label(DATAKEYS[plantsize], hubheight)
             + " - {} MW Plant".format(plantsize)
             )
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

    return figure, json.dumps(mapview)


@app.callback(
    [Output('chart', 'figure'),
     Output("plantsize_store", "children")],
    [Input("chart_options", "value"),
     Input("chart_xvariable_options", "value"),
     Input("variable", "value"),
     Input("state_options", "value"),
     Input("map", "selectedData"),
     Input("chart_point_size", "value"),
     Input("reset_chart", "n_clicks")],
    [State("map", "relayoutData"),
     State("chart", "selectedData"),
     State("plantsize_store", "children")])
def make_chart(chart, x, y, state, mapsel, point_size, reset, chartview,
               chartsel, ps_state):
    """Make one of a variety of charts."""
    print_args(make_chart, chart, x, y, state, mapsel, point_size)

    trig = dash.callback_context.triggered[0]['prop_id']

    # Only the 20MW plant for now

    # # Get the initial figure
    # if chart == "cumsum":
    #     fig = get_ccap(paths, y, mapsel, int(point_size), state, reset, trig)
    #     title = (get_label(VARIABLES, y)
    #              + " by Cumulative Capacity - "
    #              + " {} MW Plant".format(ps))

    # elif chart == "scatter":
    #     fig = get_scatter(paths, x, y, mapsel, int(point_size), state, reset,
    #                       trig)
    #     title = (get_label(VARIABLES, y)
    #              + " by "
    #              + get_label(VARIABLES, x)
    #              + " - "
    #              + " {} MW Plant".format(ps))

    # elif chart == "histogram":
    #     fig = get_histogram(paths, y, mapsel, int(point_size), state, reset,
    #                         trig)
    #     title = (get_label(VARIABLES, y) + " Histogram - "
    #              + " {} MW Plant".format(ps))

    # elif chart == "box":
    #     fig = get_boxplot(paths, y, mapsel, int(point_size), state, reset,
    #                       trig)
    #     title = (get_label(VARIABLES, y) + " Boxplots - "
    #              + " {} MW Plant".format(ps))

    # # Update the layout and traces
    # fig.update_layout(
    #     font_family="Time New Roman",
    #     title_font_family="Times New Roman",
    #     legend_title_font_color="black",
    #     font_color="white",
    #     title_font_size=25,
    #     font_size=15,
    #     margin=dict(l=70, r=20, t=70, b=20),
    #     height=500,
    #     paper_bgcolor="#1663B5",
    #     legend_title_text='Hub Height',
    #     dragmode="select",
    #     title=dict(
    #             text=title,
    #             yref="paper",
    #             y=1,
    #             x=0.1,
    #             yanchor="bottom",
    #             pad=dict(b=10)
    #             ),
    #     legend=dict(
    #         title_font_family="Times New Roman",
    #         bgcolor="#E4ECF6",
    #         font=dict(
    #            family="Times New Roman",
    #            size=15,
    #            color="black"
    #            )
    #        )
    #     )

    # return fig, json.dumps(ps)
