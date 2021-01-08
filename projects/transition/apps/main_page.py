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
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from plotly.colors import sequential as seq_colors

from review import print_args
from review.support import (AGGREGATIONS, BASEMAPS, BUTTON_STYLES,
                            CHART_OPTIONS, COLOR_OPTIONS, CONFIG_PATH,
                            DEFAULT_MAPVIEW, MAP_LAYOUT, STATES,
                            TAB_STYLE, TABLET_STYLE, VARIABLES)
from review.support import chart_point_filter, Config, Plots
from revruns import rr
from tqdm import tqdm


with open(CONFIG_PATH, "r") as file:
    FULL_CONFIG = json.load(file)
CONFIG = FULL_CONFIG["Transition"]

DP = rr.Data_Path(CONFIG["directory"])
FILEDF = pd.DataFrame(CONFIG["data"])
MASTER_FNAME = ("National Impact Innovations - Land Based WInd Scenario "
                "Matrix.xlsx")
MASTER = rr.get_sheet(DP.join("data", "tables", MASTER_FNAME),
                      sheet_name="Rev_full_matrix")

GROUPS = [c for c in FILEDF.columns if c not in ["file", "name"]]
GROUP_OPTIONS = [
    {"label": g, "value": g} for g in GROUPS
]
REGION_OPTIONS = [
    {"label": "National", "value": "national"},
    {"label": "NREL Regions", "value": "nrel_region"},
    {"label": "States", "value": "state"}
]

SCENARIO_OPTIONS = [
    {"label": " ".join(row["name"].split("_")[:2]).capitalize(),
     "value": row["file"]} for i, row in FILEDF.iterrows()
]
VARIABLE_OPTIONS = [
    {"label": v, "value": k} for k, v in CONFIG["titles"].items()
]

TABLET_STYLE_CLOSED = {
    **TABLET_STYLE,
    **{"border-bottom": "1px solid #d6d6d6"}
}

DEFAULT_SIGNAL = json.dumps([FILEDF["file"].iloc[0], None, "total_lcoe", 0,
                             200, "$/MWh"])


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
                             value="capacity"),
                ],
                className="two columns"),

            # Upper Total LCOE Threshold
            html.Div([
                html.H6("Upper LCOE Threshold"),
                dcc.Input(
                    id="upper_lcoe_threshold",
                    value=None,
                    type="number",
                    className="two columns",
                    placeholder="NA",
                    style={"width": "70%"}
                ),
            ], className="two columns"),

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
                            dcc.Tab(value='list',
                                    label='List',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE_CLOSED)
                            ]
                    ),

                    html.Div(
                        id="low_cost_choice_div",
                        children=[
                            # List Options
                            html.Div(
                                id="list_div",
                                children=[
                                    dcc.Dropdown(
                                        id="low_cost_list",
                                        multi=True,
                                        options=SCENARIO_OPTIONS,
                                        value=SCENARIO_OPTIONS[0]["value"]
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
                                ]),
                        ]),
                ]),

            html.Hr(),

            ], className="four columns"),

        ], className="row", style={"margin-bottom": "50px"}),

        #Submit Button to avoid repeated callbacks
        html.Button(
        id="submit",
        children="Submit",
        style={"width": "10%", "margin-left": "0px",
               "padding": "0px", "background-color": "#F9F9F9",
               "margin-bottom": "50px"}
        ),

        # Print total capacity after all the filters
        html.Div(id="total_capacity",
                 style={"display": "none",
                        "font-size": "20px", "font-weight": "bold"}),

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
                                dcc.Tab(value='region',
                                        label='Region',
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
                            ]),

                        # Region grouping
                        html.Div(
                            id="chart_region_div",
                            children=[
                                dcc.Dropdown(
                                    id="chart_region",
                                    clearable=False,
                                    options=REGION_OPTIONS,
                                    multi=False,
                                    value="national"
                                )
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
            id="map_signal",
            children=DEFAULT_SIGNAL,
            style={"display": "none"}
            )
    ]
)


# Support functions
def build_map_layout(mapview, title, basemap, title_size=25):
    """Build the map data layout dictionary."""
    layout = copy.deepcopy(MAP_LAYOUT)
    layout['mapbox']['center'] = mapview['mapbox.center']
    layout['mapbox']['zoom'] = mapview['mapbox.zoom']
    layout['mapbox']['bearing'] = mapview['mapbox.bearing']
    layout['mapbox']['pitch'] = mapview['mapbox.pitch']
    layout['titlefont'] = dict(color='white',
                               size=title_size,
                               family='Time New Roman',
                               fontweight='bold')
    layout["legend"] = dict(size=20)
    layout["dragmode"] = "select"
    layout['title']['text'] = title
    layout['mapbox']['style'] = basemap
    return layout


def build_scatter(df, y, x, units, color, rev_color, ymin, ymax, point_size):
    """Build a Plotly scatter plot dictionary."""
    if x == y:
        df = df.iloc[:, 1:]

    # Create hover text
    if units == "category":
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[y] + " "
                      + units)
    else:
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[y].round(2).astype(str) + " "
                      + units)

    if units == "category":
        cats = {cat: i for i, cat in enumerate(df[y].unique())}
        df["cat"] = df[y].map(cats)
        y = "cat"
        showlegend = True
        data = []

        # How to allow optionality for categorical colors?
        colors = seq_colors.__dict__[color][::len(cats)]

        for cat, value in cats.items():
            # Create a sub data frame
            sdf = df[df[y] == value]

            # Create data object
            trace = dict(type='scattermapbox',
                         hoverinfo='text',
                         hovermode='closest',
                         lat=sdf['latitude'],
                         lon=sdf['longitude'],
                         mode='markers',
                         name=cat,
                         showlegend=showlegend,
                         text=sdf['text'],
                         marker=dict(
                             # color=sdf[y],
                             # colorscale=color,
                             opacity=1.0,
                             reversescale=rev_color,
                             size=point_size
                             )
                         )

            # Add to data
            data.append(trace)

    else:
        showlegend = False
        marker = dict(
             color=df[y],
             colorscale=color,
             cmax=ymax,
             cmin=ymin,
             opacity=1.0,
             reversescale=rev_color,
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

        # Create data object
        data = [dict(type='scattermapbox',
                     lon=df['longitude'],
                     lat=df['latitude'],
                     text=df['text'],
                     mode='markers',
                     hoverinfo='text',
                     hovermode='closest',
                     showlegend=showlegend,
                     marker=marker)]

    return data


def build_title(df, path, path2, y, x,  difference, title_size = 25):
    """Create chart title."""
    config = Config("Transition")
    title = os.path.basename(path).replace("_sc.csv", "")
    title = " ".join(title.split("_")).capitalize()
    title = title + "  |  " + config.titles[y]
    if y in AGGREGATIONS:
        ag_fun = AGGREGATIONS[y]
        if ag_fun == "mean":
            conditioner = "Unweighted mean"
        else:
            conditioner = "Total"

        if difference == "on":
            ag = "mean"
            s1 = os.path.basename(path).replace("_sc.csv", "")
            s2 = os.path.basename(path2).replace("_sc.csv", "")
            s1 = " ".join(s1.split("_")).capitalize()
            s2 = " ".join(s2.split("_")).capitalize()
            title = "{} vs {} |  ".format(s2, s1) + config.titles[y]
            conditioner = "% Difference | Average"
            units = ""

        if isinstance(df, pd.core.frame.DataFrame):
            if x == y:
                df = df.iloc[:, 1:]
            if y == "capacity":
                ag = round(df[y].apply(ag_fun) / 1_000_000, 2)
                if difference == "on":
                    units = ""
                else:
                    units = "TW"
            else:
                ag = round(df[y].apply(ag_fun), 2)
                if difference == "on":
                    units = ""
                else:
                    units = config.units[y]

            ag_print = "     <br> {}: {} {}".format(conditioner, ag, units)
            title = title + ag_print

    return title


def calc_low_cost(paths, dst, by="total_lcoe"):
    """Calculate a single data frame by the lowest cost row from many."""
    # Separate function for a retrieving a single data frame
    def retrieve(arg):
        path, scenario = arg
        df = cache_table(path)
        df["scenario"] = scenario
        return df

    # Retrieve a data frame and add scenario
    if not os.path.exists(dst):
        paths.sort()
        scenarios = [os.path.basename(path).split("_")[1] for path in paths]
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

        # Save
        df.to_csv(dst, index=False)

    return dst


@app.callback(Output("lchh_path", "children"),
              [Input("low_cost_enter", "n_clicks")],
              [State("low_cost_group_tab", "value"),
               State("low_cost_list", "value"),
               State("low_cost_split_group", "value"),
               State("low_cost_split_group_options", "value")])
def retrieve_low_cost(enter, how, lst, group, group_choice):
    """Calculate low cost fields based on user decision."""
    # print_args(retrieve_low_cost, enter, how, lst, group)
    if how == "all":
        # Just one output
        fname = "scenarios_all_lchh_sc.csv"
        paths = FILEDF["file"].values
    elif how == "list":
        # Just one output
        paths = lst
        scenarios = [os.path.basename(path).split("_")[1] for path in paths]
        scen_key = "_".join(scenarios)
        fname = "scenarios_{}_lchh_sc.csv".format(scen_key)
    else:
        # This could create multiple outputs, but we'll do one at a time
        fname = "scenarios_{}_{}_sc.csv".format(group,
                                                group_choice.replace(".", ""))
        paths = FILEDF["file"][FILEDF[group] == group_choice].values

    lchh_path = DP.join("review_outputs", fname, mkdir=True)
    df = calc_low_cost(paths, lchh_path, by="total_lcoe")
    return lchh_path


@cache.memoize()
def cache_table(path):
    """Read in just a single table."""
    df = pd.read_csv(path, low_memory=False)
    if not "print_capacity" in df.columns:
        df["print_capacity"] = df["capacity"].copy()
    if not "lcoe_threshold" in df.columns:
        df["lcoe_threshold"] = df["total_lcoe"].copy()
    return df


@cache2.memoize()
def cache_map_data(signal):
    """Read and store a data frame from the config and options given."""
    # Get signal elements
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units] = json.loads(signal)

    # Read and cache first table
    df = cache_table(path)

    # Is it faster to subset columns before rows?
    keepers = [y, x, "print_capacity", "lcoe_threshold", "state",
               "nrel_region", "county", "latitude", "longitude",
               "sc_point_gid"]
    df = df[keepers]
    if y == x:
        df = df.iloc[:, 1:]

    # If there's a second table, read/cache that
    if path2:
        df2 = cache_table(path2)
        df2 = df2[keepers]
        if y == x:
            df2 = df2.iloc[:, 1:]
        # They might have different shapes
        # if df.shape[0] != df2.shape[0]:
        #     df2 = df2.rename({y: y + "_2"}, axis=1)
        #     df3 = df.rr.nearest(df2, fields=[y + "_2"])
        #     y1 = df3[y]
        #     y2 = df3[y + "_2"]
        # else:
        #     y1 = df[y]
        #     y2 = df2[y]

        # The above doesn't seem to work for two lchh's
        if df.shape[0] > df2.shape[0]:
            df2 = df2.rename({y: y + "_2"}, axis=1)
            df3 = df.rr.nearest(df2, fields=[y + "_2"])
        else:
            df = df.rename({y: y + "_2"}, axis=1)
            df3 = df2.rr.nearest(df, fields=[y + "_2"])
        y1 = df3[y]
        y2 = df3[y + "_2"]

        # Now find the percent difference
        df[y] = (1 - y1 / y2) * 100

    # If threshold, calculate here
    if threshold:
        df = df[df["lcoe_threshold"] <= threshold]

    # Finally filter for states
    if states:
        df = df[df["state"].isin(states)]

    return df


@cache3.memoize()
def cache_chart_tables(signal, region="national", idx=None):
    """Read and store a data frame from the config and options given."""
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units] = json.loads(signal)
    df = cache_map_data(signal)
    df = df[[x, y, "state", "nrel_region", "print_capacity"]]

    if states:
        df = df[df["state"].isin(states)]

    if region != "national":
        regions = df[region].unique()
        dfs = {r: df[df[region] == r] for r in regions}
    else:
        dfs = {"Map Data": df}

    if idx:
        dfs = {key: df.iloc[idx] for key, df in dfs.items()}

    return dfs


@app.callback([Output("scenario_a", "options"),
               Output("scenario_b", "options")],
              [Input("submit", "n_clicks")],
              [State("low_cost_group_tab", "value"),
               State("low_cost_list", "value"),
               State("low_cost_split_group", "value"),
               State("low_cost_split_group_options", "value"),
               State("scenario_a", "options")])
def retrieve_low_cost(submit, how, lst, group, group_choice, options):
    """Calculate low cost fields based on user decision."""
    # print_args(retrieve_low_cost, submit, how, lst, group)
    # Build the appropriate paths and target file name
    if how == "all":
        # Just one output
        fname = "least_cost_all_sc.csv"
        paths = FILEDF["file"].values
    elif how == "list":
        # Just one output
        paths = lst
        scenarios = [os.path.basename(path).split("_")[1] for path in paths]
        scen_key = "_".join(scenarios)
        fname = "least_cost_{}_sc.csv".format(scen_key)
    else:
        # This could create multiple outputs, but we'll do one at a time
        fname = "least_cost_{}_{}_sc.csv".format(group,
                                                 group_choice.replace(".", ""))
        paths = FILEDF["file"][FILEDF[group] == group_choice].values

    # Build the full target path and create the file
    lchh_path = DP.join("review_outputs", fname, mkdir=True)
    calc_low_cost(paths, lchh_path, by="total_lcoe")

    # Update the scenario file options
    label = " ".join([f.capitalize() for f in fname.split("_")[:-1]])
    if label not in [o["label"] for o in options]:
        option = {"label": label, "value": lchh_path}
        options.append(option)
    return options, options



@app.callback([Output("low_cost_group_tab_div", "style"),
               Output("low_cost_list", "style"),
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
    elif how == "list":
        style2 = {}
        style3 = {"display": "none"}
    else:
        style2 = {"display": "none"}
        style3 = {}
    return style1, style2, style3


@app.callback([Output("low_cost_split_group_options", "options"),
               Output("low_cost_split_group_options", "value")],
              [Input("low_cost_split_group", "value")])
def display_lchh_group_options(group):
    """Display the available options for a chosen group."""
    options = FILEDF[group].unique()
    option_list = [{"label": o, "value": o} for o in options]
    return option_list, options[0]


@app.callback([Output("scenario_a_specs", "children"),
               Output("scenario_b_specs", "children")],
              [Input("scenario_a", "value"),
               Input("scenario_b", "value")])
def scenario_specs(scenario_a, scenario_b):
    """Output the specs association with a chosen scenario."""
    # print_args(scenario_specs, scenario_a, scenario_b)

    fields = [f for f in FILEDF.columns if f not in ["file", "name"]]

    if "least_cost" not in scenario_a:
        df1 = FILEDF[FILEDF["file"] == scenario_a][fields].to_dict()
        dct1 = {k: v[list(v.keys())[0]] for k, v in df1.items()}
        specs1 = []
        for i, (k, v) in enumerate(dct1.items()):
            specs1.append("{}: {}".format(k, v))
            specs1.append(html.Br())
    else:
        specs1 = ["Combination of multiple scenarios."]

    if "least_cost" not in scenario_b:
        df2 = FILEDF[FILEDF["file"] == scenario_b][fields].to_dict()
        dct2 = {k: v[list(v.keys())[0]] for k, v in df2.items()}
        specs2 = []
        for i, (k, v) in enumerate(dct2.items()):
            specs2.append("{}: {}".format(k, v))
            specs2.append(html.Br())
    else:
        specs2 = ["Combination of multiple scenarios."]

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


# Map callbacks
@app.callback(Output("chart_data_signal", "children"),
              [Input("variable", "value"),
               Input("chart_xvariable_options", "value"),
               Input("state_options", "value")])
def get_chart_tables(y, x, state):
    """Store the signal used to get the set of tables needed for the chart."""
    # print_args(get_chart_tables, y, x, state)
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



@app.callback(Output("map_signal", "children"),
              [Input("submit", "n_clicks"),
               Input("state_options", "value")],
              [State("upper_lcoe_threshold", "value"),
               State("scenario_a", "value"),
               State("scenario_b", "value"),
               State("lchh_path", "children"),
               State("variable", "value"),
               State("chart_xvariable_options", "value"),
               State("difference", "value"),
               State("low_cost_tabs", "value")])
def map_signal(submit, states, threshold, path, path2, lchh_path, y, x, diff,
               lchh_toggle):
    """A signal for sharing data between map and chart with dependence."""
    trig = dash.callback_context.triggered[0]['prop_id']

    # Prevent the first trigger when difference is off
    if "scenario_b" in trig and difference == "off":
        raise PreventUpdate

    # Get/build the value scale table
    config = Config("Transition")
    scales = config.scales

    # Build the scatter plot data object
    if diff == "off":
        path2 = None
        ymin = scales[y]["min"]
        ymax = scales[y]["max"]
        units = config.units[y]
    else:
        ymin = -50
        ymax = 50
        units = "%"

    # Here we will retrieve either ...
    if "lchh_path" in trig and lchh_toggle == "on":
        path = lchh_path

    # Let's just recycle all this for the chart
    signal = json.dumps([path, path2, y, x, diff, states, ymin, ymax,
                         threshold, units])
    return signal


@app.callback([Output("map", "figure"),
               Output("mapview_store", "children")],
              [Input("map_signal", "children"),
               Input("basemap_options", "value"),
               Input("color_options", "value"),
               Input("chart", "selectedData"),
               Input("map_point_size", "value"),
               Input("rev_color", "n_clicks"),
               Input("map_color_min", "value"),
               Input("map_color_max", "value")],
              [State("map", "relayoutData"),
               State("map", "selectedData")])
def make_map(signal, basemap, color, chartsel, point_size,
             rev_color, uymin, uymax, mapview, mapsel):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    config = Config("Transition")
    trig = dash.callback_context.triggered[0]['prop_id']
    # print_args(make_map, signal, basemap, color, chartsel, point_size,
    #            rev_color, uymin, uymax, mapview, mapsel)
    print("trig = '" + str(trig) + "'")

    # Get map elements from data signal
    df = cache_map_data(signal)
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units] = json.loads(signal)


    # To save zoom levels and extent between map options (funny how this works)
    if not mapview:
        mapview = DEFAULT_MAPVIEW
    elif 'mapbox.center' not in mapview.keys():
        mapview = DEFAULT_MAPVIEW

    # Reverse color
    if rev_color % 2 == 1:
        rev_color = True
    else:
        rev_color = False

    # Use user defined value ranges
    if uymin:
        ymin = uymin
    if uymax:
        ymax = uymax

    # If there is a selection in the chart filter these points
    if chartsel:
        if len(chartsel["points"]) > 0:
            df = chart_point_filter(df, chartsel, y)

    if "selectedData" not in trig:
        if mapsel:
            idx = [p["pointIndex"] for p in mapsel["points"]]
            df = df.loc[idx]

    # Build map elements
    data = build_scatter(df, y, x, units, color, rev_color, ymin, ymax,
                          point_size)
    title = build_title(df, path, path2, y, x, diff, title_size=25)
    layout = build_map_layout(mapview, title, basemap, title_size=25)
    figure = dict(data=data, layout=layout)

    return figure, json.dumps(mapview)


# Charts
@app.callback([Output('chart_options_tab', 'children'),
               Output('chart_options_div', 'style'),
               Output('chart_xvariable_options_div', 'style'),
               Output('chart_region_div', 'style')],
              [Input('chart_options_tab', 'value'),
               Input('chart_options', 'value')])
def chart_tab_options(tab_choice, chart_choice):
    """Choose which map tab dropown to display."""
    # print_args(chart_tab_options, tab_choice, chart_choice)
    styles = [{'display': 'none'}] * 3
    order = ["chart", "xvariable", "region"]
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
            dcc.Tab(value='region',
                    label='Region',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE)
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
                    selected_style=TABLET_STYLE),
            dcc.Tab(value='region',
                    label='Region',
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE)
        ]

    return children, styles[0], styles[1], styles[2]


@app.callback(Output('chart', 'figure'),
              [Input("map_signal", "children"),
               Input("chart_options", "value"),
               Input("map", "selectedData"),
               Input("chart_point_size", "value"),
               Input("chosen_map_options", "children"),
               Input("chart_region", "value")],
              [State("chart", "relayoutData"),
               State("chart", "selectedData")])
def make_chart(signal, chart, mapsel, point_size, op_values, region, chartview,
               chartsel):
    """Make one of a variety of charts."""
    # print_args(make_chart, signal, chart, mapsel, point_size, op_values,
    #            region, chartview, chartsel)
    trig = dash.callback_context.triggered[0]['prop_id']
    print("trig = '" + str(trig) + "'")

    # Get map elements from data signal
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units] = json.loads(signal)

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
        signal = json.dumps([path, path2, y, x, diff, states, ymin, ymax,
                             threshold, units])
        dfs = cache_chart_tables(signal, region, idx)
        plotter = Plots(dfs, "Transition", group, point_size)
        fig = plotter.ccap()

    elif chart == "scatter":
        dfs = cache_chart_tables(signal, region)
        plotter = Plots(dfs, "Transition", group, point_size)
        fig = plotter.scatter()

    elif chart == "histogram":
        dfs = cache_chart_tables(signal, region)
        plotter = Plots(dfs, "Transition", group, point_size)
        ylim = [0, 2000]
        fig = plotter.histogram()

    elif chart == "box":
        dfs = cache_chart_tables(signal, region)
        plotter = Plots(dfs, "Transition", group, point_size)
        fig = plotter.box()

    # Whats the total capacity at this point?
    title = build_title(dfs, path, path2, y, x, diff, title_size=25)

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
