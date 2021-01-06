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
import numpy as np
import pandas as pd
import pathos.multiprocessing as mp

from app import app, cache, cache2, cache3
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from review import print_args
from review.support import (AGGREGATIONS, BASEMAPS, BUTTON_STYLES,
                            CHART_OPTIONS, COLOR_OPTIONS, CONFIG, CONFIG_PATH,
                            DEFAULT_MAPVIEW, MAP_LAYOUT, STATES,
                            TAB_STYLE, TABLET_STYLE, VARIABLES)
from review.support import (chart_point_filter, config_div, get_dataframe_path,
                            sort_mixed, Config, Plots)
from revruns import rr
from tqdm import tqdm

with open(os.path.expanduser("~/.review_config"), "r") as file:
    FULL_CONFIG = json.load(file)

CONFIG = FULL_CONFIG["Transition"]

DP = rr.Data_Path(CONFIG["directory"])


FILEDF = pd.DataFrame(CONFIG["data"])

GROUPS = [c for c in FILEDF.columns if c not in ["file", "name"]]
GROUP_OPTIONS = [
    {"label": g, "value": g} for g in GROUPS
]
MASTER_FNAME = ("National Impact Innovations - Land Based WInd Scenario "
                "Matrix.xlsx")

MASTER = rr.get_sheet(DP.join("data", MASTER_FNAME),
                      sheet_name="Rev_full_matrix")

SCENARIO_OPTIONS = [
    {"label": " ".join(row["name"].split("_")[:2]).capitalize(),
     "value": row["file"]} for i, row in FILEDF.iterrows()
]

TABLET_STYLE_CLOSED = {
    **TABLET_STYLE,
    **{"border-bottom": "1px solid #d6d6d6"}
}

VARIABLE_OPTIONS = [
    {"label": v, "value": k} for k, v in CONFIG["titles"].items()
    if k not in GROUPS
]


layout = html.Div(
    children=[

        # Initial Options
        html.Div([
            # First Scenario
            html.Div([
                html.H5("Scenario A"),
                dcc.Dropdown(
                    id="scenario_a",
                    options=SCENARIO_OPTIONS,
                    value=SCENARIO_OPTIONS[0]["value"]
                ),
                html.P(
                    id="scenario_a_specs",
                    style={"margin-left": "15px"}
                )
            ], className="two columns"),
    
            # Second Scenario
            html.Div(
                id="scenario_b_div",
                children=[
                    html.Div([
                        html.H5("Scenario B"),
                        dcc.Dropdown(
                            id="scenario_b",
                            options=SCENARIO_OPTIONS,
                            value=SCENARIO_OPTIONS[1]["value"]
                        ),
                        html.P(
                            id="scenario_b_specs"
                        )
                        ], className="two columns")
                ],
                style={"margin-left": "50px"}),

            # Variable options
            html.Div([
                html.H5("Variable"),
                dcc.Dropdown(id="variable",
                             options=VARIABLE_OPTIONS,
                             value="total_lcoe"),
                ],
                className="two columns"),

            # Show difference map
            html.Div([
                html.H5("Difference"),
                dcc.Tabs(
                    id="difference",
                    value="off",
                    style=TAB_STYLE,
                    children=[
                        dcc.Tab(value='on',
                                label='On',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE_CLOSED),
                        dcc.Tab(value='off',
                                label='Off',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE_CLOSED)
                ]),
                html.Hr()
            ], className="two columns"),

            # Calculate Lowest Cost Hub Heights
            html.Div([
                # Option to calculate or no
                html.H5("Lowest LCOE Data Set"),
                dcc.Tabs(
                    id="low_cost_tabs",
                    value="off",
                    style=TAB_STYLE,
                    children=[
                        dcc.Tab(value='on',
                                label='On',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE_CLOSED),
                        dcc.Tab(value='off',
                                label='Off',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE_CLOSED)
                ]),

                # How do we want to organize this?
                html.Div(
                    id="low_cost_group_tab_div",
                    style={"display": "none"},
                    children=[
                    dcc.Tabs(
                        id="low_cost_group_tab",
                        value="all",
                        style=TAB_STYLE,
                        children=[
                            dcc.Tab(value='all',
                                    label='All',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE_CLOSED),
                            dcc.Tab(value='group',
                                    label='Group',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE_CLOSED),
                            dcc.Tab(value='pair',
                                    label='Pair',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE_CLOSED)
                            ]   
                    ),                

                    html.Div(
                        id="low_cost_choice_div",
                        children=[
                            # Pair Options
                            html.Div(
                                id="pair_div",
                                children=[
                                    dcc.Dropdown(
                                        id="low_cost_pair_1",
                                        options=SCENARIO_OPTIONS,
                                        value=SCENARIO_OPTIONS[0]["value"]
                                    ),
                                    dcc.Dropdown(
                                        id="low_cost_pair_2",
                                        options=SCENARIO_OPTIONS,
                                        value=SCENARIO_OPTIONS[1]["value"]
                                    )
                                ]
                            ),

                            # Group Options
                            html.Div(
                                id="low_cost_split_group_div",
                                children=[
                                    dcc.Dropdown(
                                        id="low_cost_split_group",
                                        options=GROUP_OPTIONS,
                                        value=GROUP_OPTIONS[0]["value"]
                                    ),
                                    dcc.Dropdown(
                                        id="low_cost_split_group_options"
                                    )
                                ]
                            ),
                        
                        ]
                    ),                

                    # Enter Button for whichever option was picked
                    html.Button(
                        id="low_cost_enter",
                        children="Enter",
                        style={"width": "100%", "margin-left": "0px",
                               "padding": "0px", "background-color": "#d6d6d6"}
                    ),
                ]),
                html.Hr(),

            ], className="six columns")

        ], className="row", style={"margin-bottom": "50px"}),

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
                        html.H6("Point Size:", className="two columns"),
                        dcc.Input(
                            id="map_point_size",
                            value=5,
                            type="number",
                            className="two columns",
                            style={"margin-left": -5, "width": "7%"}
                        ),
                        html.H6("Color Min: ", className="two columns"),
                        dcc.Input(
                            id="map_color_min",
                            placeholder="",
                            type="number",
                            className="two columns",
                            style={"margin-left": -5, "width": "7%"}
                        ),
                        html.H6("Color Max: ", className="two columns"),
                        dcc.Input(
                            id="map_color_max",
                            placeholder="",
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

        # For storing and triggering lchh graphs
        html.Div(
            id="lchh_path",
            style={"display": "none"}
            ),

        # Interim way to share data between map and chart
        html.Div(
            id="map_data_paths",
            style={"display": "none"}
            )
    ]
)


def calc_low_cost(paths, dst, by="total_lcoe"):
    """Calculate a single data frame by the lowest cost row from many."""
    # Get a list of data frames
    paths.sort()
    scenarios = [os.path.basename(path).split("_")[1] for path in paths]
    if os.path.exists(dst):
        df = cache_table(dst)
    else:
        # Retrieve a data frame and add scenario
        def retrieve(arg):
            path, scenario = arg
            df = cache_table(path)
            df["scenario"] = scenario
            return df

        dfs = []
        args = [[paths[i], scenarios[i]] for i in range(len(paths))]
        with mp.Pool(mp.cpu_count()) as pool:
            for df in tqdm(pool.imap(retrieve, args), total=len(paths)):
                dfs.append(df)

        # How to deal with mismatching grids?
        shapes = [df.shape[0] for df in dfs]
        if len(np.unique(shapes)) > 1:
            base = dfs[np.where(shapes == np.min(shapes))[0][0]]
            gids = base["sc_point_gid"].values
            dfs = [df[df["sc_point_gid"].isin(gids)] for df in dfs]

        # For each row, find which df has the lowest lcoes
        values = np.array([df[by].values for df in dfs])
        df_indices = np.argmin(values, axis=0)
        row_indices = [np.where(df_indices == i)[0] for i in range(len(dfs))]
    
        dfs = [dfs[i].iloc[idx] for i, idx in enumerate(row_indices)]
        df = pd.concat(dfs)
        df.to_csv(dst, index=False)
        del dfs

    return df


@cache.memoize()
def cache_table(path):
    """Read in just a single table."""
    df = pd.read_csv(path, low_memory=False)
    return df


@cache2.memoize()
def cache_map_table(path, path2=None, y="total_lcoe", x="capacity", idx=None):
    """Read and store a data frame from the config and options given."""
    # Is it faster to subset columns before rows?
    keepers = [y, x, "state", "county", "latitude", "longitude",
               "sc_point_gid"]

    # Read and cache first table
    df = cache_table(path)
    df = df[keepers]
    if idx:
        df = df.loc[idx]

    # If there's a second table, read/cache that
    if path2:
        df2 = cache_table(path2)
        df2 = df2[keepers]
        if idx:
            df2 = df2.loc[idx]

        # They might have different shapes
        if df.shape[0] != df2.shape[0]:
            df2 = df2.rename({y: y + "_2"}, axis=1)
            df3 = df.rr.nearest(df2, fields=[y + "_2"])
            y1 = df3[y]
            y2 = df3[y + "_2"]
        else:
            y1 = df[y]
            y2 = df2[y]

        df[y] = (1 -  y1 / y2) * 100

    return df


@cache3.memoize()
def cache_chart_tables(path, path2, x, y, state, idx):
    """Read and store a data frame from the config and options given.

    project = "Southern Company"
    y = "capacity"
    x = "capacity"
    group = "Plant Size"
    filters = {"Hub Height": "120", "Plant Size": "20"}
    idx = None
    """
    df = cache_map_table(path, path2, y=y, x=x)
    df = df[[x, y, "state"]]
    if x == y:
        df[x + "2"] = df[x].copy()
    if state:
        df = df[df["state"].isin(state)]
    if idx:
        df = df.iloc[idx, :]
    df = df[[x, y]]
    dfs = {"Map Data": df}

    return dfs


@app.callback([Output("low_cost_group_tab_div", "style"),
               Output("low_cost_pair_1", "style"),
               Output("low_cost_pair_2", "style"),
               Output("low_cost_split_group_div", "style")],
              [Input("low_cost_tabs", "value"),
               Input("low_cost_group_tab", "value")])
def toggle_low_cost_options(choice, how):
    """Show the grouping options for the low cost function."""
    if choice == "on":
        style1 = {}
    else:
        style1 = {"display": "none"}
    if how == "all":
        style2 = {"display": "none"}
        style3 = {"display": "none"}
        style4 = {"display": "none"}
    elif how == "pair":
        style2 = {}
        style3 = {}
        style4 = {"display": "none"}
    else:
        style2 = {"display": "none"}
        style3 = {"display": "none"}
        style4 = {}
    return style1, style2, style3, style4 


@app.callback(Output("lchh_path", "children"),
              [Input("low_cost_enter", "n_clicks")],
              [State("low_cost_group_tab", "value"),
               State("low_cost_pair_1", "value"),
               State("low_cost_pair_2", "value"),
               State("low_cost_split_group", "value"),
               State("low_cost_split_group_options", "value")])
def retrieve_low_cost(enter, how, pair1, pair2, group, group_choice):
    """Calculate low cost fields based on user decision."""
    print_args(retrieve_low_cost, enter, how, pair1, pair2, group)
    if how == "all":
        # Just one output
        fname = "scenarios_all_lchh_sc.csv"
        paths = FILEDF["file"].values
    elif how == "pair":
        # Just one output
        paths = [pair1, pair2]
        scenarios = [os.path.basename(path).split("_")[1] for path in paths]
        scen_key = "_".join(scenarios)
        fname = "scenarios_{}_lchh_sc.csv".format(scen_key)
    else:
        # This could create multiple outputs, but we'll do one at a time
        fname = "scenarios_{}_{}_sc.csv".format(group,
                                                group_choice.replace(".", ""))
        paths = FILEDF["file"][FILEDF[group] == group_choice].values
        
    lchh_path = DP.join("review_outputs", fname, mkdir=True)
    df = calc_low_cost(paths, lchh_path)

    return lchh_path



    if len(scenarios) == FILEDF.shape[0]:
        scen_key = "all"
    else:
        scen_key = "_".join(scenarios)
    fname = "scenarios_{}_lchh_sc.csv".format(scen_key)




@app.callback([Output("low_cost_split_group_options", "options"),
               Output("low_cost_split_group_options", "value")],
              [Input("low_cost_split_group", "value")])
def display_lchh_group_options(group):
    """Display the available options for a chosen group."""
    options = FILEDF[group].unique()
    option_list = [{"label": o, "value": o} for o in options]
    return option_list, options[0]


# @cache.memoize()
# def cache_chart_tables(project, group, x, y, state, idx, *options):
#     """Read and store a data frame from the config and options given.

#     project = "Southern Company"
#     y = "capacity"
#     x = "capacity"
#     group = "Plant Size"
#     filters = {"Hub Height": "120", "Plant Size": "20"}
#     idx = None
#     """
#     project_config = CONFIG[project]
#     data = pd.DataFrame(project_config["data"]).copy()
#     option_names = [c for c in data.columns if c not in ["file", "name"]]
#     filters = dict(zip(option_names, options))

#     # We're keeping the grouping variable
#     if group in filters:
#         del filters[group]

#     # If every possible combination is present this works
#     for fltr, value in filters.items():
#         data = data[data[fltr] == value]
#         del data[fltr]

#     # If there are results
#     dfs = {}
#     for i, row in data.iterrows():
#         group_val = row[group]
#         path = row["file"]
#         df = pd.read_csv(path, usecols=[x, y, "state"])
#         if x == y:
#             df[x + "2"] = df[x].copy()
#         if state:
#             df = df[df["state"].isin(state)]
#         if idx:
#             df = df.iloc[idx, :]
#         df = df[[x, y]]
#         dfs[group_val] = df

#     # If there's one result
#     name = data["name"].values[0]

#     return dfs, name


@app.callback([Output("scenario_a_specs", "children"),
               Output("scenario_b_specs", "children")],
              [Input("scenario_a", "value"),
               Input("scenario_b", "value")])
def scenario_specs(scenario_a, scenario_b):
    """Output the specs association with a chosen scenario."""
    # print_args(scenario_specs, scenario_a, scenario_b)

    fields = [f for f in FILEDF.columns if f not in ["file", "name"]]

    df1 = FILEDF[FILEDF["file"] == scenario_a][fields].to_dict()
    df2 = FILEDF[FILEDF["file"] == scenario_b][fields].to_dict()

    dct1 = {k: v[list(v.keys())[0]] for k, v in df1.items()}
    dct2 = {k: v[list(v.keys())[0]] for k, v in df2.items()}

    specs1 = []
    for i, (k, v) in enumerate(dct1.items()):
        specs1.append("{}: {}".format(k, v))
        specs1.append(html.Br())

    specs2 = []
    for i, (k, v) in enumerate(dct2.items()):
        specs2.append("{}: {}".format(k, v))
        specs2.append(html.Br())

    return specs1, specs2


@app.callback(Output("scenario_b_div", "style"),
              [Input("difference", "value")])
def toggle_scenario_b(difference):
    """Show scenario b if the difference option is on."""
    if difference == "on":
        style = {}
    else:
        style = {"display": "none"}
    return style


@app.callback([Output('chart_options_tab', 'children'),
               Output('chart_options_div', 'style'),
               Output('chart_xvariable_options_div', 'style')],
              [Input('chart_options_tab', 'value'),
               Input('chart_options', 'value')])
def chart_tab_options(tab_choice, chart_choice):
    """Choose which map tab dropown to display."""
    print_args(chart_tab_options, tab_choice, chart_choice)
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
                    selected_style=TABLET_STYLE),
            dcc.Tab(value='xvariable',
                    label='X Variable',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE)
        ]

    return children, styles[0], styles[1]


@app.callback(Output("chart_data_signal", "children"),
              [Input("variable", "value"),
               Input("chart_xvariable_options", "value"),
               Input("state_options", "value")])
def get_chart_tables(y, x, state):
    """Store the signal used to get the set of tables needed for the chart."""
    print_args(get_chart_tables, y, x, state)
    signal = json.dumps([y, x, state])
    print("signal = " + signal)
    return signal


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
    [Output("map", "figure"),
     Output("mapview_store", "children"),
     Output("map_data_paths", "children")],
    [Input("scenario_a", "value"),
     Input("scenario_b", "value"),
     Input("variable", "value"),
     Input("lchh_path", "children"),
     Input("state_options", "value"),
     Input("basemap_options", "value"),
     Input("color_options", "value"),
     Input("chart", "selectedData"),
     Input("map_point_size", "value"),
     Input("rev_color", "n_clicks"),
     Input("reset_chart", "n_clicks"),
     Input("difference", "value"),
     Input("map_color_min", "value"),
     Input("map_color_max", "value")],
    [State("low_cost_tabs", "value"),
     State("map", "relayoutData"),
     State("map", "selectedData")])
def make_map(data_path, data_path2, variable, lchh_path, state,
             basemap, color, chartsel, point_size, rev_color, reset,
             difference, uymin, uymax, lchh_toggle, mapview, mapsel):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    config = Config("Transition")
    trig = dash.callback_context.triggered[0]['prop_id']
    print_args(make_map, data_path, data_path2, variable, lchh_path, state,
               basemap, color, chartsel, point_size, rev_color, reset,
               difference, uymin, uymax, lchh_toggle, mapview,
               mapsel, trig)
    print("trig = '" + str(trig) + "'")

    # Prevent the first trigger when difference is off
    if "scenario_b" in trig and difference == "off":
        raise PreventUpdate

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
    if difference == "off":
        data_path2 = None
        ymin = scales[variable]["min"]
        ymax = scales[variable]["max"]
        units = config.units[variable]
    else:
        ymin = -50
        ymax = 50
        units = "%"

    if uymin:
        ymin = uymin
    if uymax:
        ymax = uymax

    # Here we will retrieve either ...
    if "lchh_path" in trig and lchh_toggle == "on":
        data_path = lchh_path

    print("USING DATA PATH: " + data_path)
    df = cache_map_table(data_path, y=variable, path2=data_path2)

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
                      + units)
    else:
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[variable] + " "
                      + units)

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
                    cmin=ymin,
                    cmax=ymax,
                    opacity=1.0,
                    size=point_size,
                    colorbar=dict(
                        title=units,
                        dtickrange=[
                            ymin,
                            ymax
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
    title = os.path.basename(data_path).replace("_sc.csv", "")
    title = " ".join(title.split("_")).capitalize()
    title = title + "  |  " + config.titles[variable]
    if variable in AGGREGATIONS:
        ag_fun = AGGREGATIONS[variable]
        if ag_fun == "mean":
            conditioner = "Unweighted mean"
        else:
            conditioner = "Total"
        if variable == "capacity":
            ag = round(df[variable].apply(ag_fun) / 1_000_000, 2)
            units = "TW"
        else:
            ag = round(df[variable].apply(ag_fun), 2)
            units = config.units[variable]

        if difference == "on":
            s1 = os.path.basename(data_path).replace("_sc.csv", "")
            s2 = os.path.basename(data_path2).replace("_sc.csv", "")
            s1 = " ".join(s1.split("_")).capitalize()
            s2 = " ".join(s2.split("_")).capitalize()
            title = "{} vs {}  |  ".format(s2, s1)  + config.titles[variable]
            conditioner = "% Difference | Average"
            units = ""

        ag_print = "  |  {}: {} {}".format(conditioner, ag, units)
        title = title + ag_print

    # Let's just recycle all this for the chart
    chart_signal = [data_path, data_path2, ymin, ymax, title]

    title_size = 25

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

    return figure, json.dumps(mapview), json.dumps(chart_signal)


@app.callback(Output('chart', 'figure'),
             [Input("map_data_paths", "children"),
              Input("chart_options", "value"),
              Input("chart_data_signal", "children"),
              Input("map", "selectedData"),
              Input("chart_point_size", "value"),
              Input("reset_chart", "n_clicks"),
              Input("chosen_map_options", "children")],
             [State("chart", "relayoutData"),
              State("chart", "selectedData")])
def make_chart(map_data_paths, chart, signal, mapsel, point_size, reset,
               op_values, chartview, chartsel):
    """Make one of a variety of charts."""
    signal = json.loads(signal)
    print_args(make_chart, map_data_paths, chart, signal, mapsel, point_size,
               reset, op_values, chartview, chartsel)

    # Get the data_paths used in the map
    [data_path, data_path2, ymin, ymax, title] = json.loads(map_data_paths)

    # Get the set of data frame using the stored signal
    y, x, state = signal
    config = Config("Transition")

    # Turn the map selection object into indices
    if mapsel:
        idx = [d["pointIndex"] for d in mapsel["points"]]
    else:
        idx = None

    # And generate on of these plots
    group = "Map Data"
    title_size = 25
    ylim = [ymin, ymax]
    if chart == "cumsum":
        x = "capacity"
        dfs = cache_chart_tables(data_path, data_path2, x, y, state, idx)
        plotter = Plots(dfs, "Transition", group, point_size)
        fig = plotter.ccap()

    elif chart == "scatter":
        dfs = cache_chart_tables(data_path, data_path2, x, y, state, idx)
        plotter = Plots(dfs, "Transition", group, point_size)
        fig = plotter.scatter()

    elif chart == "histogram":
        dfs = cache_chart_tables(data_path, data_path2, x, y, state, idx)
        plotter = Plots(dfs, "Transition", group, point_size)
        fig = plotter.histogram()

    elif chart == "box":
        dfs = cache_chart_tables(data_path, data_path2, x, y, state, idx)
        plotter = Plots(dfs, "Transition", group, point_size)
        fig = plotter.box()

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
    # return ""