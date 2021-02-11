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

from app import app, cache, cache2, cache3
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from plotly.colors import sequential as seq_colors

from review import print_args
from review.support import (AGGREGATIONS, BASEMAPS, BUTTON_STYLES,
                            CHART_OPTIONS, COLOR_OPTIONS, DEFAULT_MAPVIEW,
                            MAP_LAYOUT, STATES, TAB_STYLE, TABLET_STYLE,
                            VARIABLES)
from review.support import (chart_point_filter, Config, Data_Path, Difference,
                            Least_Cost, Plots)



# Temporary
CONFIG = Config("Transition").project_config

DP = Data_Path(CONFIG["directory"])
FILEDF = pd.DataFrame(CONFIG["data"])
SPECS = CONFIG["parameters"]

GROUPS = [c for c in FILEDF.columns if c not in ["file", "name"]]
GROUP_OPTIONS = [
    {"label": g, "value": g} for g in GROUPS
]
REGION_OPTIONS = [
    {"label": "National", "value": "national"},
    {"label": "NREL Regions", "value": "nrel_region"},
    {"label": "States", "value": "state"}
]
SCENARIO_OUTPUTS = DP.contents("review_outputs", "least_cost*_sc.csv")
SCENARIO_ORIGINALS = list(FILEDF["file"].values)
FILES = SCENARIO_ORIGINALS + SCENARIO_OUTPUTS
NAMES = [os.path.basename(f).replace("_sc.csv", "") for f in FILES]
NAMES = [" ".join([n.capitalize() for n in name.split("_")]) for name in NAMES]
FILE_LIST = dict(zip(NAMES, FILES))
SCENARIO_OPTIONS = [
    {"label": key, "value": file} for key, file in FILE_LIST.items()
]
VARIABLE_OPTIONS = [
    {"label": v, "value": k} for k, v in CONFIG["titles"].items()
]
# Temporary


REGION_OPTIONS = [
    {"label": "National", "value": "national"},
    {"label": "NREL Regions", "value": "nrel_region"},
    {"label": "States", "value": "state"}
]

TABLET_STYLE_CLOSED = {
    **TABLET_STYLE,
    **{"border-bottom": "1px solid #d6d6d6"}
}
TAB_BOTTOM_SELECTED_STYLE = {
    'borderBottom': '1px solid #1975FA',
    'borderTop': '1px solid #d6d6d6',
    'line-height': '25px',
    'padding': '0px'
}

DEFAULT_SIGNAL = json.dumps([FILEDF["file"].iloc[0], None, "capacity",
                             "mean_cf", "off", None, 0.0243, 398.1312,
                             ["mean_lcoe_threshold", 50], "MW"])


layout = html.Div(
    children=[

        # Constant info block
        html.Div([

            # Project Selection
            html.Div([
                html.H4("Project"),
                dcc.Dropdown(
                    id="project"
                )
            ], className="three columns"),

            # Print total capacity after all the filters are applied
            html.Div([
                html.H5("Remaining Generation Capacity: "),
                html.H1(id="capacity_print", children="")
            ], className="three columns")

        ], className="row", style={"margin-bottom": "35px"}),

        # Options Label
        html.H4("Options"),
        html.Hr(style={"height": "0px", "width": "98%", "border": "none",
                       "border-top": "1px solid grey"}),

        # Data Options
        html.Div([

            # First Scenario
            html.Div([
                html.H5("Scenario A"),
                dcc.Dropdown(
                    id="scenario_a",
                    options=SCENARIO_OPTIONS,
                    value=SCENARIO_OPTIONS[0]["value"]
                ),
                dcc.Markdown(
                    id="scenario_a_specs",
                    style={"margin-left": "15px", "font-size": "9pt",
                           "height": "300px", "overflow-y": "scroll"}
                )
            ], className="three columns", style={"margin-left": "50px"}),

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
                        dcc.Markdown(
                            id="scenario_b_specs",
                            style={"margin-left": "15px", "font-size": "9pt",
                                   "height": "300px", "overflow-y": "scroll"}
                        )
                        ], className="three columns")
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
                dcc.Tabs(
                    id="threshold_field",
                    value="total_lcoe_threshold",
                    style=TAB_STYLE,
                    children=[
                        dcc.Tab(value='total_lcoe_threshold',
                                label='Total LCOE',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE_CLOSED),
                        dcc.Tab(value='mean_lcoe_threshold',
                                label='Site LCOE',
                                style=TABLET_STYLE,
                                selected_style=TABLET_STYLE_CLOSED)
                ]),
                dcc.Input(
                    id="upper_lcoe_threshold",
                    value=None,
                    type="number",
                    placeholder="NA",
                    style={"width": "100%"}
                ),
                dcc.Tabs(
                    id="threshold_mask",
                    value="mask_off",
                    style=TAB_STYLE,
                    children=[
                        dcc.Tab(value='mask_off',
                                label='No Mask',
                                style=TABLET_STYLE,
                                selected_style=TAB_BOTTOM_SELECTED_STYLE),
                        dcc.Tab(value='mask_on',
                                label='Scenario B Mask',
                                style=TABLET_STYLE,
                                selected_style=TAB_BOTTOM_SELECTED_STYLE)
                ]),
            ], className="two columns"),

            # Show difference map
            html.Div([
                html.H5("Scenario B Difference"),
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
                        id="low_cost_by",
                        value="total_lcoe",
                        style=TAB_STYLE,
                        children=[
                            dcc.Tab(value='total_lcoe',
                                    label='Total LCOE',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE_CLOSED),
                            dcc.Tab(value='mean_lcoe',
                                    label='Site LCOE',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE_CLOSED),
                        ]
                    ),
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

        ], id="options", className="row", style={"margin-bottom": "50px"}),

        #Submit Button to avoid repeated callbacks
        html.Div([
            html.Button(
                id="submit",
                children="Submit",
                className="row",
                style={"background-color": "#cccccc",
                       "border-color": "#00000",
                       "width": "125px",
                       "height": "45px",
                       "margin-bottom": "50px",
                       "text-align": "center"}
            ),
        ], style={"margin-left": "50px"}),

        html.Hr(style={"height": "0px", "width": "98%", "border": "none",
                       "border-top": "1px solid grey"}),

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

        # The filedf is used for group options
        html.Div(
            id="filedf",
            style={"display": "none"}
            ),

        # Interim way to share data between map and chart
        html.Div(
            id="map_signal",
            children=DEFAULT_SIGNAL,
            style={"display": "none"}
            ),

        # Because we can't have a callback with no output
        html.Div(
            id="catch_low_cost",
            style={"dsiplay": "none"}
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
    # Create hover text
    if units == "category":
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[y].astype(str) + " " + units)
    else:
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[y].round(2).astype(str) + " " + units)

    # Offshore points will be nans, since they don't have states or counties
    if any(df["text"].isnull()):
        ondf = df[~pd.isnull(df["text"])]
        offdf = df[pd.isnull(df["text"])]
        if units == "category":
            offdf["text"] = (offdf["latitude"].round(2).astype(str) + ", "
                             + offdf["longitude"].round(2).astype(str)
                             + ": <br>   "
                             + offdf[y].astype(str) + " " + units)
        else:
            offdf["text"] = (offdf["latitude"].round(2).astype(str) + ", "
                             + offdf["longitude"].round(2).astype(str)
                             + ": <br>   "
                             + offdf[y].round(2).astype(str) + " " + units)
        df = pd.concat([ondf, offdf])

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


def build_specs(scenario, project):
    """Calculate the percentage of each scenario present."""
    config = Config(project)
    specs = config.project_config["parameters"]
    dct = specs[scenario]
    table = """| Variable | Value |\n|----------|------------|\n"""
    for variable, value in dct.items():
        row = "| {} | {} |\n".format(variable, value)
        table = table + row
    return table


def build_spec_split(path):
    """Calculate the percentage of each scenario present."""
    df = cache_table(path)
    scenarios, counts = np.unique(df["scenario"], return_counts=True)
    total = df.shape[0]
    percentages = [counts[i] / total for i in range(len(counts))]
    percentages = [round(p * 100, 4)  for p in percentages]
    pdf = pd.DataFrame(dict(p=percentages, s=scenarios))
    pdf = pdf.sort_values("p", ascending=False)
    table = """| Scenario | Percentage |\n|----------|------------|\n"""
    for _, row in pdf.iterrows():
        row = "| {} | {}% |\n".format(row["s"], row["p"])
        table = table + row

    return table


def build_title(df, path, path2, y, x,  difference, title_size=25):
    """Create chart title."""
    # print_args(build_title, df, path, path2, y, x,  difference, title_size)
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
            s1 = " ".join([s.capitalize() for s in s1.split("_")])
            s2 = "  ".join([s.capitalize() for s in s2.split("_")])
            title = "{} vs {} |  ".format(s1, s2) + config.titles[y]
            conditioner = "% Difference | Average"
            units = ""

        if isinstance(df, pd.core.frame.DataFrame):
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


def calc_mask(df1, df2, threshold, threshold_field):
    """Remove the areas in df2 under the threshold from df1."""
    # How to deal with mismatching grids?
    tidx = df2["sc_point_gid"][df2[threshold_field] <= threshold].values
    df = df1[~df1["sc_point_gid"].isin(tidx)]
    return df


@app.callback(Output("capacity_print", "children"),
             [Input("map_signal", "children"),
              Input("map", "selectedData"),
              Input("chart", "selectedData")])
def calc_total_capacity(signal, mapsel, chartsel):
    """Calculate total remaining capacity after all filters are applied."""
    # print_args(calc_total_capacity, signal, mapsel, chartsel)
    trig = dash.callback_context.triggered[0]['prop_id'].split(".")[0]
    df = cache_map_data(signal)
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units, mask] = json.loads(signal)
    if trig == "map":
        if mapsel:
            idx = [d["pointIndex"] for d in mapsel["points"]]
            df = df.iloc[idx]
    elif trig == "chart":
        if chartsel:
            df = chart_point_filter(df, chartsel, y)
    total = round(df["print_capacity"].sum() / 1_000_000, 2)
    total_print = "{} TW".format(total)
    return total_print


@cache.memoize()
def cache_table(path):
    """Read in just a single table."""
    df = pd.read_csv(path, low_memory=False)
    df["index"] = df.index
    if not "print_capacity" in df.columns:
        df["print_capacity"] = df["capacity"].copy()
    if not "total_lcoe_threshold" in df.columns:
        df["total_lcoe_threshold"] = df["total_lcoe"].copy()
        df["mean_lcoe_threshold"] = df["mean_lcoe"].copy()
    return df


@cache2.memoize()
def cache_map_data(signal):
    """Read and store a data frame from the config and options given."""
    # Get signal elements
    [path, path2, y, x, difference, states, ymin, ymax, threshold,
     units, mask] = json.loads(signal)

    # Read and cache first table
    df1 = cache_table(path)

    # Separate the threshold values out
    threshold_field = threshold[0]
    threshold = threshold[1]

    # Is it faster to subset columns before rows?
    keepers = [y, x, "print_capacity", "total_lcoe_threshold",
               "mean_lcoe_threshold", "state",
               "nrel_region", "county", "latitude", "longitude",
               "sc_point_gid", "index"]
    df1 = df1[keepers]

    # For other functions this data frame needs an x field
    if y == x:
        df1 = df1.iloc[:, 1:]

    # If there's a second table, read/cache the difference
    if path2:
        # Match the format of the first dataframe
        df2 = cache_table(path2)
        df2 = df2[keepers]
        if y == x:
            df2 = df2.iloc[:, 1:]

        # If the difference option is specified difference
        if difference == "on":
            calculator = Difference()
            df = calculator.calc(df1, df2, y)
        else:
            df = df1.copy()

        # If mask, try that here
        if mask == "mask_on":
            if threshold:
                df = calc_mask(df, df2, threshold, threshold_field)
    else:
        df = df1.copy()

    # If threshold, calculate this for the final df here
    if threshold:
        df = df[df[threshold_field] < threshold]

    # Finally filter for states
    if states:
        if "onshore" in states:
            df = df[~pd.isnull(df["state"])]
        elif "offshore" in states:
            df = df[pd.isnull(df["state"])]
        else:
            df = df[df["state"].isin(states)]

    return df


@cache3.memoize()
def cache_chart_tables(signal, region="national", idx=None):
    """Read and store a data frame from the config and options given."""
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units, mask] = json.loads(signal)
    df = cache_map_data(signal)
    df = df[[x, y, "state", "nrel_region", "print_capacity", "index"]]

    if idx:
        df = df.iloc[idx]

    if states:
        if "onshore" in states:
            df = df[~pd.isnull(df["state"])]
        elif "offshore" in states:
            df = df[pd.isnull(df["state"])]
        else:
            df = df[df["state"].isin(states)]

    if region != "national":
        regions = df[region].unique()
        dfs = {r: df[df[region] == r] for r in regions}
    else:
        dfs = {"Map Data": df}

    return dfs

@app.callback([Output('chart_options_tab', 'children'),
               Output('chart_options_div', 'style'),
               Output('chart_xvariable_options_div', 'style'),
               Output('chart_region_div', 'style')],
              [Input('chart_options_tab', 'value'),
               Input('chart_options', 'value')])
def options_chart_tabs(tab_choice, chart_choice):
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

@app.callback([Output("low_cost_split_group_options", "options"),
               Output("low_cost_split_group_options", "value")],
              [Input("low_cost_split_group", "value"),
               Input("filedf", "children")])
def options_lchh_group(group, filedf):
    """Display the available options for a chosen group."""
    filedf = json.loads(filedf)
    filedf = pd.DataFrame(filedf)
    options = filedf[group].unique()
    option_list = [{"label": o, "value": o} for o in options]
    return option_list, options[0]

@app.callback([Output("low_cost_group_tab_div", "style"),
               Output("low_cost_list", "style"),
               Output("low_cost_split_group_div", "style")],
              [Input("low_cost_tabs", "value"),
               Input("low_cost_group_tab", "value")])
def options_low_cost_toggle(choice, how):
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

@app.callback([Output("state_options", "style"),
               Output('basemap_options_div', 'style'),
               Output('color_options_div', 'style')],
              [Input('map_options_tab', 'value')])
def options_map_tab(tab_choice):
    """Choose which map tab dropdown to display."""
    styles = [{'display': 'none'}] * 3
    order = ["state", "basemap", "color"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}

    return styles[0], styles[1], styles[2]

@app.callback([Output("scenario_a", "options"),
               Output("scenario_b", "options"),
               Output("variable", "options"),
               Output("low_cost_split_group", "options"),
               Output("filedf", "children")],
              [Input("project", "value")])
def options_options(project):
    """Update the options given a project."""
    config = Config(project).project_config

    DP = Data_Path(config["directory"])
    filedf = pd.DataFrame(config["data"])
    groups = [c for c in filedf.columns if c not in ["file", "name"]]
    scneario_outputs = DP.contents("review_outputs", "least_cost*_sc.csv")
    scenario_originals = list(filedf["file"].values)
    files = scenario_originals + scneario_outputs
    names = [os.path.basename(f).replace("_sc.csv", "") for f in files]
    names = [" ".join([n.capitalize() for n in name.split("_")]) for name in names]
    file_list = dict(zip(names, files))

    group_options = [{"label": g, "value": g} for g in groups]
    scenario_options = [
        {"label": key, "value": file} for key, file in file_list.items()
    ]
    variable_options = [
        {"label": v, "value": k} for k, v in config["titles"].items()
    ]

    return (scenario_options, scenario_options, variable_options,
            group_options, json.dumps(filedf.to_dict()))


@app.callback([Output("project", "options"),
               Output("project", "value")],
              [Input("url", "pathname")])
def options_project(pathname):
    """Update project options. Triggered by navbar."""
    # Open config json
    fconfig = Config()
    options = []
    for project in fconfig.projects:
        pconfig = Config(project)
        if "parameters" in pconfig.project_config:
            options.append({"label": project, "value": project})
    return options, "Transition"

@app.callback([Output("options", "style"),
               Output("toggle_options", "children"),
               Output("toggle_options", "style"),
               Output("submit", "style")],
              [Input('toggle_options', 'n_clicks')])
def options_toggle_options(click):
    """Toggle options on/off."""
    if not click:
        click = 0
    if click % 2 != 1:
        block_style = {"display": "none"}
        button_children = 'Options: Off'
        button_style = BUTTON_STYLES["off"]
        submit_style = {"display": "none"}
    else:
        block_style = {"margin-bottom": "50px"}
        button_children = 'Options: On'
        button_style = BUTTON_STYLES["on"]
        submit_style = {"background-color": "#cccccc", "margin-bottom": "50px",
                        "text-align": "center", "width": "125px",
                        "height": "45px"}

    return block_style, button_children, button_style, submit_style

@app.callback(Output("scenario_b_div", "style"),
              [Input("difference", "value"),
               Input("threshold_mask", "value")])
def options_toggle_scenario_b(difference, mask):
    """Show scenario b if the difference option is on."""
    # trig = dash.callback_context.triggered[0]["prop_id"].split(".")
    # print_args(toggle_scenario_b, difference, mask)
    if difference == "on":
        style = {}
    elif mask == "mask_on":
        style = {}
    else:
        style = {"display": "none"}
    return style

@app.callback([Output('rev_color', 'children'),
               Output('rev_color', 'style')],
              [Input('rev_color', 'n_clicks')])
def options_toggle_rev_color_button(click):
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

@app.callback(Output("catch_low_cost", "children"),
              [Input("submit", "n_clicks")],
              [State("low_cost_group_tab", "value"),
               State("low_cost_list", "value"),
               State("low_cost_split_group", "value"),
               State("low_cost_split_group_options", "value"),
               State("scenario_a", "options"),
               State("low_cost_by", "value")])
def retrieve_low_cost(submit, how, lst, group, group_choice, options, by):
    """Calculate low cost fields based on user decision."""
    # print_args(retrieve_low_cost, submit, how, lst, group, group_choice,
    #            options)

    config = Config("Transition")

    # Build the appropriate paths and target file name
    if how == "all":
        # Just one output
        fname = "least_cost_by_{}_all_sc.csv".format(by)
        paths = FILEDF["file"].values
    elif how == "list":
        # Just one output
        paths = lst
        scenarios = [os.path.basename(path).split("_")[1] for path in paths]
        scen_key = "_".join(scenarios)
        fname = "least_cost_by_{}_{}_sc.csv".format(by, scen_key)
    else:
        # This could create multiple outputs, but we'll do one at a time
        fname = "least_cost_by_{}_{}_{}_sc.csv".format(
                                                 by,
                                                 group,
                                                 group_choice.replace(".", "")
                                                 )
        paths = FILEDF["file"][FILEDF[group] == group_choice].values

    # Build full paths and create the target file
    paths = [os.path.join(config.directory, path) for path in paths]
    lchh_path = DP.join("review_outputs", fname, mkdir=True)
    calculator = Least_Cost()
    calculator.calc(paths, lchh_path, by=by)

    # Update the scenario file options
    label = " ".join([f.capitalize() for f in fname.split("_")[:-1]])
    if label not in [o["label"] for o in options]:
        option = {"label": label, "value": lchh_path}
        options.append(option)
    return " "

@app.callback([Output("scenario_a_specs", "children"),
               Output("scenario_b_specs", "children")],
              [Input("scenario_a", "value"),
               Input("scenario_b", "value"),
               Input("project", "value")])
def scenario_specs(scenario_a, scenario_b, project):
    """Output the specs association with a chosen scenario."""
    print_args(scenario_specs, scenario_a, scenario_b)
    if "least_cost" not in scenario_a:
        scenario_a = scenario_a.replace("_sc.csv", "")
        specs1 = build_specs(scenario_a, project)
    else:
        specs1 = build_spec_split(scenario_a)

    if "least_cost" not in scenario_b:
        scenario_b = scenario_b.replace("_sc.csv", "")
        specs2 = build_specs(scenario_b, project)
    else:
        specs2 = build_spec_split(scenario_b)

    return specs1, specs2


# Map callbacks
@app.callback(Output("chart_data_signal", "children"),
              [Input("variable", "value"),
               Input("chart_xvariable_options", "value"),
               Input("state_options", "value")])
def retrieve_chart_tables(y, x, state):
    """Store the signal used to get the set of tables needed for the chart."""
    # print_args(get_chart_tables, y, x, state)
    signal = json.dumps([y, x, state])
    print("signal = " + signal)
    return signal

@app.callback(Output("map_signal", "children"),
              [Input("submit", "n_clicks"),
               Input("state_options", "value"),
               Input("chart_options", "value")],
              [State("upper_lcoe_threshold", "value"),
               State("threshold_field", "value"),
               State("scenario_a", "value"),
               State("scenario_b", "value"),
               State("lchh_path", "children"),
               State("variable", "value"),
               State("chart_xvariable_options", "value"),
               State("difference", "value"),
               State("low_cost_tabs", "value"),
               State("threshold_mask", "value")])
def retrieve_map_signal(submit, states, chart, threshold, threshold_field,
                        path, path2, lchh_path, y, x, diff, lchh_toggle, mask):
    """Create signal for sharing data between map and chart with dependence."""
    print_args(retrieve_map_signal, submit, states, chart, threshold,
               threshold_field, path, path2, lchh_path, y, x, diff,
               lchh_toggle, mask)
    trig = dash.callback_context.triggered[0]['prop_id']
    print("trig = '" + trig + "'")

    # Prevent the first trigger when difference is off
    if "scenario_b" in trig and diff == "off":
        raise PreventUpdate

    # Prevent the first trigger when mask is off
    if "mask" in trig and mask == "off":
        raise PreventUpdate

    # Get/build the value scale table
    config = Config("Transition")
    scales = config.scales

    # Get the full path from the config
    path = os.path.join(config.directory, path)
    if path2:
        path2 = os.path.join(config.directory, path2)

    # Createy mask and difference dependent variables
    ymin = scales[y]["min"]
    ymax = scales[y]["max"]
    units = config.units[y]
    if diff == "off" and mask == "mask_off":
        path2 = None
    elif diff == "on":
        ymin = -50
        ymax = 50
        units = "%"

    # Here we will retrieve either ...
    if "lchh_path" in trig and lchh_toggle == "on":
        path = lchh_path

    # Combine threshold and its field
    threshold = [threshold_field, threshold]

    # Get map elements from data signal
    if chart == "cumsum":
        x = "capacity"

    # Let's just recycle all this for the chart
    signal = json.dumps([path, path2, y, x, diff, states, ymin, ymax,
                         threshold, units, mask])
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
    print_args(make_map, signal, basemap, color, chartsel, point_size,
                rev_color, uymin, uymax, mapview, mapsel)
    trig = dash.callback_context.triggered[0]['prop_id']
    print("'MAP'; trig = '" + str(trig) + "'")

    # Get map elements from data signal
    df = cache_map_data(signal)
    df.index = df["index"]
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
      units, mask] = json.loads(signal)

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
            points = chartsel["points"]
            ys = [p["y"] for p in points]
            ymin = min(ys)
            ymax = max(ys)
            df = df[(df[y] >= ymin) & (df[y] <= ymax)]

    # Build map elements
    data = build_scatter(df, y, x, units, color, rev_color, ymin, ymax,
                          point_size)
    title = build_title(df, path, path2, y, x, diff, title_size=20)
    layout = build_map_layout(mapview, title, basemap, title_size=20)
    figure = dict(data=data, layout=layout)

    return figure, json.dumps(mapview)

@app.callback(Output('chart', 'figure'),
              [Input("map_signal", "children"),
                Input("chart_options", "value"),
                Input("map", "selectedData"),
                Input("chart_point_size", "value"),
                Input("chosen_map_options", "children"),
                Input("chart_region", "value"),
                Input("map_color_min", "value"),
                Input("map_color_max", "value")],
              [State("chart", "relayoutData"),
                State("chart", "selectedData")])
def make_chart(signal, chart, mapsel, point_size, op_values, region, uymin,
                uymax, chartview, chartsel):
    """Make one of a variety of charts."""
    print_args(make_chart, signal, chart, mapsel, point_size, op_values,
                region, chartview, chartsel)
    trig = dash.callback_context.triggered[0]['prop_id']
    print("trig = '" + str(trig) + "'")

    # Unpack the signal
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
      units, mask] = json.loads(signal)

    # Turn the map selection object into indices
    if mapsel:
        if len(mapsel["points"]) > 0:
            idx = [d["pointIndex"] for d in mapsel["points"]]
        else:
            idx = None
    else:
        idx = None

    # And generate on of these plots
    group = "Map Data"
    title_size = 20

    # Get the data frames
    dfs = cache_chart_tables(signal, region, idx)
    plotter = Plots("Transition", dfs, group, point_size,
                    yunits=units)

    if chart == "cumsum":
        fig = plotter.ccap()
    elif chart == "scatter":
        fig = plotter.scatter()
    elif chart == "histogram":
        ylim = [0, 2000]
        fig = plotter.histogram()
    elif chart == "box":
        fig = plotter.box()

    # Whats the total capacity at this point?
    title = build_title(dfs, path, path2, y, x, diff, title_size=title_size)

    # User defined y-axis limits
    if uymin:
        ymin = uymin
    if uymax:
        ymax = uymax
    ylim = [ymin, ymax]

    # Update the layout and traces
    fig.update_layout(
        font_family="Time New Roman",
        title_font_family="Times New Roman",
        legend_title_font_color="black",
        font_color="white",
        title_font_size=title_size,
        font_size=15,
        margin=dict(l=70, r=20, t=70, b=20),
        height=700,
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
