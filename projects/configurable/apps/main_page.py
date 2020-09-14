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

from app import app, cache
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from review import print_args
from .support import (BASEMAPS, BUTTON_STYLES, CHART_OPTIONS, COLOR_OPTIONS,
                      CONFIG, CONFIG_PATH, DEFAULT_MAPVIEW, MAP_LAYOUT,STATES,
                      TITLES, TAB_STYLE, TABLET_STYLE, UNITS, VARIABLES)
from .support import (chart_point_filter, config_div, get_dataframe_path,
                      get_scales, get_variables, setup_options, sort_mixed,
                      Plots)

NOPTIONS = 5
OPTION_INPUTS, OPTION_PLACEHOLDER = setup_options(NOPTIONS)


layout = html.Div(
    children=[

        # Project selection - use id "project" to access
        html.Div(
            id="project_div",
            className="twelve columns",
            children=config_div(CONFIG_PATH),
            style={"margin-bottom": "50px"}
        ),

        # Dynamic options - ids are "0" up to possible NOPTIONS
        html.Div(
            id="option_div",
            className="row",
            children=OPTION_PLACEHOLDER,
            style={"margin-bottom": "50px"}
        ),

        # The chart and map div
        html.Div([
    
            # The map div
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
    
            # The chart div
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
                                dcc.Tab(value="group",
                                        label="Grouping Variable",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE),
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
                                )
                            ]),
    
                        # The grouping variable
                        html.Div(
                            id="group_options_div",
                            children=[
                                dcc.Dropdown(
                                    id="group_options",
                                    clearable=False,
                                    options=[{"value": "placeholder",
                                              "label": "placeholder"}],
                                    multi=False,
                                    value="placeholder"
                                )
                            ]
                        ),

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
                                )
                            ])
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


        # Just a testing output div
        html.Div(
            id="testing"
            ),

        # To maintain the view after updating the map
        html.Div(id="mapview_store",
                 children=json.dumps(DEFAULT_MAPVIEW),
                 style={"display": "none"}),

        # For storing the data frame path and triggering updates
        html.Div(
            id="map_data_path",
            style={"display": "none"}
            ),

        # For storing the signal need for the set of chart data frames
        html.Div(
            id="chart_data_signal",
            style={"display": "none"}
            ),
    ]
)


# Read and cache the dataframe according to the input values
@cache.memoize()
def cache_map_table(path, idx=None):
    """Read and store a data frame from the config and options given."""
    df = pd.read_csv(path)
    if idx:
        df = df.iloc[idx]
    return df


@cache.memoize()
def cache_chart_tables(project, group, x, y, state, idx, *options):
    """Read and store a data frame from the config and options given.
    
    project = "Southern Company"
    y = "total_lcoe"
    x = "capacity"
    group = "Plant Size"
    filters = {"Hub Height": "120", "Plant Size": "20"}
    idx = None    
    """
    if group == "placeholder":
        raise PreventUpdate
    project_config = CONFIG[project]
    directory = project_config["directory"]
    data = pd.DataFrame(project_config["data"]).copy()
    option_names = [c for c in data.columns if c != "file"]
    filters = dict(zip(option_names, options))
    if group in filters:
        del filters[group]
    for fltr, value in filters.items():
        data = data[data[fltr] == value]
        del data[fltr]

    dfs = {}
    for i, row in data.iterrows():
        group_val = row[group]
        file = row["file"]
        path = os.path.join(directory, file)
        df = pd.read_csv(path, usecols=[x, y, "state"])
        if state:
            df = df[df["state"] == state]
        if idx:
            df = df.iloc[idx, :]
        df = df[[x, y]]
        dfs[group_val] = df

    return dfs


@app.callback([Output('chart_options_tab', 'children'),
               Output('chart_options_div', 'style'),
               Output('group_options_div', 'style'),
               Output('chart_xvariable_options_div', 'style')],
              [Input('chart_options_tab', 'value'),
               Input('chart_options', 'value'),
               Input('project', 'value')])
def chart_tab_options(tab_choice, chart_choice, project):
    """Choose which map tab dropown to display."""
    styles = [{'display': 'none'}] * 3
    order = ["chart", "group", "xvariable"]
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
            dcc.Tab(value="group",
                    label="Grouping Variable",
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE),
            ]
    else:
        children = [
            dcc.Tab(value='chart',
                    label='Chart Type',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE
                    ),
            dcc.Tab(value="group",
                    label="Grouping Variable",
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE),
            dcc.Tab(value='xvariable',
                    label='X Variable',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE)
            ]

    return children, styles[0], styles[1], styles[2]


@app.callback(Output("map_data_path", "children"),
              [Input("project", "value")] + OPTION_INPUTS)
def get_map_table(project, *options):
    if any(options):
        path = get_dataframe_path(project, *options)
        return path


@app.callback(Output("chart_data_signal", "children"),
              [Input("project", "value"),
               Input("group_options", "value"),
               Input("variable", "value"),
               Input("chart_xvariable_options", "value"),
               Input("state_options", "value")] + OPTION_INPUTS)
def get_chart_tables(project, group, y, x, state, *options):
    """Store the signal used to get the set of tables needed for the chart."""
    options = [str(o) for o in options if o]
    signal = json.dumps([project, group, y, x, state, *options])
    print("signal = " + signal)
    return signal


@app.callback(Output("group_options_div", "children"),
              [Input("project", "value")])
def group_options(project):
    """Update grouping options for the chart according to the project."""
    # Get the possible grouping variables
    project_config = CONFIG[project]
    data = pd.DataFrame(project_config["data"])
    del data["file"]
    groups = data.columns
    group_options = [{"label": group, "value": group} for group in groups]

    # The grouping variable
    children = [
            dcc.Dropdown(
                id="group_options",
                clearable=False,
                options=group_options,
                multi=False,
                value=data.columns[0]
            )
        ]

    return children


@app.callback(Output("option_div", "children"),
              [Input("project", "value")])
def make_options(project):
    """Return a list of dropdowns for variables in chosen project config."""
    # Extract the project config and its data frame
    project_config = CONFIG[project]
    data = pd.DataFrame(project_config["data"])
    del data["file"]

    # For each field in the data frame create a dropdown menu of options
    entries = []
    for i in range(NOPTIONS):
        if i in range(len(data.columns)):
            variable = data.columns[i]
            values = list(data[variable].unique())
            values = sort_mixed(values)
            options = []
            for value in values:
                option = {"label": value, "value": value}
                options.append(option)
            entry = html.Div([
                html.H5(variable),
                dcc.Dropdown(id="option_{}".format(i),
                             options=options,
                             value=values[0]),
                ],
                className="two columns")
            entries.append(entry)
        else:
            entry = html.Div([
                dcc.Dropdown(id="option_{}".format(i)),
                ],
                style={"display": "none"},
                className="two columns")
            entries.append(entry)

    # Add in the variable options
    variables = get_variables(project_config)
    var_options = []
    for value, label in variables.items():
        option = {"label": label, "value": value}
        var_options.append(option)
    
    var = html.Div([
            html.H5("Variable"),
            dcc.Dropdown(id="variable",
                         options=var_options,
                         value="total_lcoe"),
            ],
            className="two columns")
    entries = entries + [var]

    return entries


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


@app.callback(
    [Output('map', 'figure'),
     Output("mapview_store", "children")],
    [Input("map_data_path", "children"),
     Input("variable", "value"),
     Input("state_options", "value"),
     Input("basemap_options", "value"),
     Input("color_options", "value"),
      Input("chart", "selectedData"),
     Input("map_point_size", "value"),
      Input("rev_color", "n_clicks"),
      Input("reset_chart", "n_clicks")],
    [State("project", "value"),
     State("map", "relayoutData"),
     State("map", "selectedData")])
def make_map(data_path, variable, state, basemap, color, chartsel, point_size,
             rev_color, reset, project, mapview, mapsel):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    print_args(make_map, variable, state, basemap, color, chartsel, point_size,
                rev_color, reset, mapview, mapsel)

    trig = dash.callback_context.triggered[0]['prop_id']

    if not data_path:
        raise PreventUpdate

    # To save zoom levels and extent between map options (funny how this works)
    if not mapview:
        mapview = DEFAULT_MAPVIEW
    elif 'mapbox.center' not in mapview.keys():
        mapview = DEFAULT_MAPVIEW

    # Get/build the value scale table
    scales = get_scales(project)

    if rev_color % 2 == 1:
        rev_color = True
    else:
        rev_color = False

    # Build the scatter plot data object
    df = cache_map_table(data_path)

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
                    cmin=scales[variable]["min"],
                    cmax=scales[variable]["max"],
                    opacity=1.0,
                    size=point_size,
                    colorbar=dict(
                        title=UNITS[variable],
                        dtickrange=scales[variable],
                        textposition="auto",
                        orientation="h",
                        font=dict(
                            size=15,
                            fontweight='bold')
                        )
                    )
                )

    # Set up layout
    title = TITLES[variable]
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
    Output('chart', 'figure'),
    [Input("chart_options", "value"),
     Input("chart_data_signal", "children"),
     Input("map", "selectedData"),
     Input("chart_point_size", "value"),
     Input("reset_chart", "n_clicks")],
    [State("chart", "relayoutData"),
     State("chart", "selectedData")])
def make_chart(chart, signal, mapsel, point_size, reset, chartview, chartsel):
    """Make one of a variety of charts."""
    signal = json.loads(signal)
    print_args(make_chart, chart, signal, mapsel, point_size, reset,
               chartview, chartsel)

    # Get the set of data frame using the stored signal
    project, group, y, x, state, *options = signal

    # Turn the map selection object into indices
    if mapsel:
        idx = [d["pointIndex"] for d in mapsel["points"]]
    else:
        idx=None

    # And generate on of these plots
    if chart == "cumsum":
        x = "capacity"
        dfs = cache_chart_tables(project, group, x, y, state, idx, *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.ccap()

    elif chart == "scatter":
        dfs = cache_chart_tables(project, group, x, y, state, idx, *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.scatter()
        # title = (get_label(VARIABLES, y)
        #           + " by "
        #           + get_label(VARIABLES, x)
        #           + " - "
        #           + " {} MW Plant".format(ps))

    elif chart == "histogram":
        dfs = cache_chart_tables(project, group, x, y, state, idx, *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.histogram()
    #     title = (get_label(VARIABLES, y) + " Histogram - "
    #              + " {} MW Plant".format(ps))

    elif chart == "box":
        dfs = cache_chart_tables(project, group, x, y, state, idx, *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.box()
    #     title = (get_label(VARIABLES, y) + " Boxplots - "
    #              + " {} MW Plant".format(ps))

    # Update the layout and traces
    fig.update_layout(
        font_family="Time New Roman",
        title_font_family="Times New Roman",
        legend_title_font_color="black",
        font_color="white",
        title_font_size=25,
        font_size=15,
        margin=dict(l=70, r=20, t=70, b=20),
        height=500,
        hovermode="x unified",
        paper_bgcolor="#1663B5",
        legend_title_text=group,
        dragmode="select",
        # title=dict(
        #         text=title,
        #         yref="paper",
        #         y=1,
        #         x=0.1,
        #         yanchor="bottom",
        #         pad=dict(b=10)
        #         ),
        legend=dict(
            title_font_family="Times New Roman",
            bgcolor="#E4ECF6",
            font=dict(
                family="Times New Roman",
                size=15,
                color="black"
                )
            )
        )

    return fig


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
