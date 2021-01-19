# -*- coding: utf-8 -*-
"""
View reV results using a configuration file.

Things to do:
    - Fix charts when the same x- and y-axis variables are selected
    - Add more configurations
    - Fix custom color ramp format
    - Fix ordering of number boxplot groups
    - Fix variable axis ranges in charts
    - Add point selection reset button
    - Add link to GDS page
    - Customize CSS, remove internal styling
    - Deal with long titles
    - include a value range table in the config file
    - speed up get_scales
"""
import copy
import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from app import app, cache
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from review import print_args
from review.support import (BASEMAPS, BUTTON_STYLES, CHART_OPTIONS,
                            COLOR_OPTIONS, CONFIG, CONFIG_PATH,
                            DEFAULT_MAPVIEW, MAP_LAYOUT, STATES,
                            TAB_STYLE, TABLET_STYLE, VARIABLES)
from review.support import (chart_point_filter, config_div, get_dataframe_path,
                            sort_mixed, Config, Plots)

layout = html.Div(
    children=[
        # Project selection - use id "project" to access
        html.Div(
            id="project_div",
            className="twelve columns",
            children=config_div(CONFIG_PATH),
            style={"margin-bottom": "50px"}
        ),

        # Dynamic options
        html.Div(
            id="option_div",
            className="row",
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
                            value=5,
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

        # To store option names for the map title
        html.Div(
            id="chosen_map_options",
            style={"display": "none"}
            ),

        # To store option names for the chart title
        html.Div(
            id="chosen_chart_options",
            style={"display": "none"}
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


@cache.memoize()
def cache_map_table(path, y="total_lcoe", idx=None):
    """Read and store a data frame from the config and options given."""
    df = pd.read_csv(path)
    if idx is not None:
        df = df.loc[idx]
    df = df[[y, "state", "county", "latitude", "longitude"]]
    return df


@cache.memoize()
def cache_chart_tables(project, group, x, y, state, idx, *options):
    """Read and store a data frame from the config and options given.

    project = "Southern Company"
    y = "capacity"
    x = "capacity"
    group = "Plant Size"
    filters = {"Hub Height": "120", "Plant Size": "20"}
    idx = None
    """
    project_config = CONFIG[project]
    data = pd.DataFrame(project_config["data"]).copy()
    option_names = [c for c in data.columns if c not in ["file", "name"]]
    filters = dict(zip(option_names, options))

    # We're keeping the grouping variable
    if group in filters:
        del filters[group]

    # If every possible combination is present this works
    for fltr, value in filters.items():
        data = data[data[fltr] == value]
        del data[fltr]

    # If there are results
    dfs = {}
    for i, row in data.iterrows():
        group_val = row[group]
        path = row["file"]
        df = pd.read_csv(path, usecols=[x, y, "state"])
        if x == y:
            df[x + "2"] = df[x].copy()
        if state:
            df = df[df["state"].isin(state)]
        if idx:
            df = df.iloc[idx, :]
        df = df[[x, y]]
        dfs[group_val] = df

    # If there's one result
    name = data["name"].values[0]

    return dfs, name


# @app.callback()
# def set_project_options(x):
#     """Update the project option list with the config file."""


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


@app.callback([Output("map_data_path", "children"),
               Output("chosen_map_options", "children")],
              [Input("option_div", "children"),
               Input("project", "value"),
               Input({"type": "option_dropdown", "index": ALL}, "value")])
def get_map_table(option_div, project, *options):
    """Get the data path from a list of map options and store those optons."""
    print_args(get_map_table, option_div, project, *options)
    if len(options) == 1:
        options = options[0]
    options = [str(o) for o in options if o is not None]
    op_names = []
    for o in option_div:
        entry = o["props"]["children"][0]["props"]
        if "children" in entry:
            op_name = entry["children"]
            if "option_" not in op_name and op_name != "Variable":
                op_names.append(op_name)
    op_values = dict(zip(op_names, options))

    if any(op_values):
        path = get_dataframe_path(project, op_values)
        print(path)
        return path, json.dumps(op_values)


@app.callback(Output("chart_data_signal", "children"),
              [Input("project", "value"),
               Input("group_options", "value"),
               Input("variable", "value"),
               Input("chart_xvariable_options", "value"),
               Input("state_options", "value"),
               Input({'type': 'option_dropdown', 'index': ALL}, 'value')])
def get_chart_tables(project, group, y, x, state, *options):
    """Store the signal used to get the set of tables needed for the chart."""
    print_args(get_chart_tables, project, group, y, x, state, *options)
    options = options[0]
    options = [str(o) for o in options if o]
    signal = json.dumps([project, group, y, x, state, *options])
    print("signal = " + signal)
    return signal


@app.callback(Output("group_options_div", "children"),
              [Input("project", "value")])
def chart_group_options(project):
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
    del data["name"]

    # For each field in the data frame create a dropdown menu of options
    entries = []
    for i, group in enumerate(data.columns):
        values = list(data[group].unique())
        values = sort_mixed(values)
        options = [{"label": value, "value": value} for value in values]
        entry = html.Div([
                    html.H5(group),
                    dcc.Dropdown(id={"type": "option_dropdown", "index": i},
                                 options=options,
                                 value=values[0]),
                    ],
                className="two columns")
        entries.append(entry)

    # Add in the variable options
    variables = project_config["titles"]
    for group in data.columns:
        if group in variables:
            del variables[group]

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
     Input("reset_chart", "n_clicks"),
     Input("project", "value")],
    [State("map", "relayoutData"),
     State("map", "selectedData"),
     State("chosen_map_options", "children")])
def make_map(data_path, variable, state, basemap, color, chartsel, point_size,
             rev_color, reset, project, mapview, mapsel, op_values):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    print("RENDERING MAP")
    if not data_path:
        print("MAP: No data path")
        raise PreventUpdate

    print_args(make_map, data_path, variable, state, basemap, color, chartsel,
               point_size, rev_color, reset, project, mapview, mapsel,
               op_values)

    trig = dash.callback_context.triggered[0]['prop_id']
    config = Config(project)
    op_values = json.loads(op_values)

    # To save zoom levels and extent between map options (funny how this works)
    if not mapview:
        mapview = DEFAULT_MAPVIEW
    elif 'mapbox.center' not in mapview.keys():
        mapview = DEFAULT_MAPVIEW

    # Get/build the value scale table
    scales = config.scales

    if rev_color % 2 == 1:
        rev_color = True
    else:
        rev_color = False

    # Build the scatter plot data object
    df = cache_map_table(data_path, y=variable)

    if "reset" not in trig:
        # If there is a selection in the chart filter these points
        if chartsel:
            if len(chartsel["points"]) > 0:
                df = chart_point_filter(df, chartsel, variable)

        if "selectedData" not in trig:
            if mapsel:
                idx = [p["pointIndex"] for p in mapsel["points"]]
                df = df.loc[idx]

        # Finally filter for states
        if state:
            df = df[df["state"].isin(state)]

    if not isinstance(df[variable].iloc[0], str):
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[variable].round(2).astype(str) + " "
                      + config.units[variable])
    else:
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[variable] + " "
                      + config.units[variable])

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
                        title=config.units[variable],
                        dtickrange=[
                            scales[variable]["min"],
                            scales[variable]["max"]
                            ],
                        textposition="auto",
                        orientation="h",
                        font=dict(
                            size=15,
                            fontweight='bold')
                        )
                    )
                )

    # Set up layout
    if project == "Transition":
        title = os.path.basename(data_path).replace("_sc.csv", "")
        title = " ".join(title.split("_")).capitalize()
        title_size = 25
    else:
        title = config.map_title(variable, op_values)
        title_size = config.title_size
    layout_copy = copy.deepcopy(MAP_LAYOUT)
    layout_copy['mapbox']['center'] = mapview['mapbox.center']
    layout_copy['mapbox']['zoom'] = mapview['mapbox.zoom']
    layout_copy['mapbox']['bearing'] = mapview['mapbox.bearing']
    layout_copy['mapbox']['pitch'] = mapview['mapbox.pitch']
    layout_copy['titlefont'] = dict(color='white', size=title_size,
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
     Input("reset_chart", "n_clicks"),
     Input("chosen_map_options", "children")],
    [State("chart", "relayoutData"),
     State("chart", "selectedData")])
def make_chart(chart, signal, mapsel, point_size, reset, op_values, chartview,
               chartsel):
    """Make one of a variety of charts."""
    signal = json.loads(signal)
    print_args(make_chart, chart, signal, mapsel, point_size, reset, op_values,
               chartview, chartsel)

    # Get the set of data frame using the stored signal
    project, group, y, x, state, *options = signal
    config = Config(project)
    op_values = json.loads(op_values)

    # Turn the map selection object into indices
    if mapsel:
        idx = [d["pointIndex"] for d in mapsel["points"]]
    else:
        idx = None

    # And generate on of these plots
    if chart == "cumsum":
        x = "capacity"
        dfs, name = cache_chart_tables(project, group, x, y, state, idx,
                                       *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.ccap()
        ytitle = config.titles[y]
        var_title = ytitle + " by Cumulative Capacity"
        title = config.chart_title(var_title, op_values, group)

    elif chart == "scatter":
        dfs, name = cache_chart_tables(project, group, x, y, state, idx,
                                       *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.scatter()
        ytitle = config.titles[y]
        xtitle = config.titles[x]
        var_title = ytitle + " by " + xtitle
        title = config.chart_title(var_title, op_values, group)

    elif chart == "histogram":
        dfs, name = cache_chart_tables(project, group, x, y, state, idx,
                                       *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.histogram()
        var_title = config.titles[y]
        title = config.chart_title(var_title, op_values, group)

    elif chart == "box":
        dfs, name = cache_chart_tables(project, group, x, y, state, idx,
                                       *options)
        plotter = Plots(dfs, project, group, point_size)
        fig = plotter.box()
        var_title = config.titles[y]
        title = config.chart_title(var_title, op_values, group)

    # Quick hack for transition team
    if project == "Transition":
        title = name.replace("_sc.csv", "")
        title = " ".join(title.split("_")).capitalize()
        title_size = 25
    else:
        title_size = config.title_size
    ylim = [
         plotter.config.scales[y]["min"],
         plotter.config.scales[y]["max"]
     ]

    # Update the layout and traces
    fig.update_layout(
        font_family="Time New Roman",
        title_font_family="Times New Roman",
        legend_title_font_color="black",
        font_color="white",
        title_font_size=title_size,
        font_size=15,
        margin=dict(l=70, r=20, t=70, b=20),
        height=500,
        hovermode="x unified",
        paper_bgcolor="#1663B5",
        legend_title_text=group,
        dragmode="select",
        yaxis=dict(range=ylim),
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
            bgcolor="#E4ECF6",
            font=dict(
                family="Times New Roman",
                size=15,
                color="black"
                )
            )
        )

    return fig
