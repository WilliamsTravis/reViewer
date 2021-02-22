# -*- coding: utf-8 -*-
"""
View reV results using a configuration file.

Things to do:
    - Add in recalculations of LCOE figures with parameterized FCRs
      (useful life built in to this figure.)
    - Actually, what can we postprocess? Think about what is simple to quickly
      recalculate and parameterize that.
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
#from plotly.colors import sequential as seq_colors

from review import print_args
from review.support import (AGGREGATIONS, BASEMAPS, BOTTOM_DIV_STYLE,
                            BUTTON_STYLES, CHART_OPTIONS, COLOR_OPTIONS,
                            DEFAULT_MAPVIEW, MAP_LAYOUT, STATES, TAB_STYLE,
                            TABLET_STYLE, VARIABLES)
from review.support import (chart_point_filter, Config, Data, Data_Path,
                            Difference, Least_Cost, Plots)


############## Temporary for initial layout ###################################
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
PROJECT_OPTIONS = []
for project in Config().projects:
    if "parameters" in Config(project).project_config:
        option = {"label": project, "value": project}
        PROJECT_OPTIONS.append(option)
SCENARIO_OPTIONS = [
    {"label": key, "value": file} for key, file in FILE_LIST.items()
]
VARIABLE_OPTIONS = [
    {"label": v, "value": k} for k, v in CONFIG["titles"].items()
]
RECALC_TABLE = {
    "scenario_a": {
        "fcr": None, "capex": None, "opex": None, "losses": None
    },
    "scenario_b": {
        "fcr": None, "capex": None, "opex": None, "losses": None
    }
}
############## Temporary ######################################################

############## Everything below goes into css ################################
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

# Reverse Color button styles
RC_STYLES = copy.deepcopy(BUTTON_STYLES)
RC_STYLES["off"]["border-color"] =  RC_STYLES["on"]["border-color"] = "#1663b5"
RC_STYLES["off"]["border-width"] =  RC_STYLES["on"]["border-width"] = "3px"
RC_STYLES["off"]["border-top-width"] = "0px"
RC_STYLES["on"]["border-top-width"] = "0px"
RC_STYLES["off"]["border-radius-top-left"] = "0px"
RC_STYLES["on"]["border-radius-top-right"] = "0px"
RC_STYLES["off"]["float"] = RC_STYLES["on"]["float"] = "right"
############## Everything above goes into css ################################


layout = html.Div(
    children=[

        # Constant info block
        html.Div([

            # Project Selection
            html.Div([
                html.H4("Project"),
                dcc.Dropdown(
                    id="project",
                    options=PROJECT_OPTIONS,
                    value="Transition"
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
        html.Hr(style={"width": "98%",
                       "border-bottom": "2px solid #fccd34",
                       "border-top": "3px solid #1663b5"}),

        # Toggle Options
        html.Div([
            html.Button(
                  id="toggle_options",
                  children="Options: Off",
                  n_clicks=0,
                  type="button",
                  title=("Click to display options"),
                  style=BUTTON_STYLES["off"],
                  className="two columns"),
        ], style={"margin-left": "50px"}, className="row"),

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
                html.H5("Lowest LCOE Data Set*",
                        title=("This will save and add the least cost table"
                               " to the scenario A and B options. Submit "
                               "below to generate the table, then select the "
                               "resulting dataset in the dropdown. If "
                               "recalculating, just use scenario A's inputs, "
                               "we're still working on this part.")),
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
                                        multi=True
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

                # Submit Button to avoid repeated callbacks
                html.Div([
                    html.Button(
                        id="low_cost_submit",
                        children="Submit",
                        className="row"
                    ),
                ]),

                html.Hr(),
            ], className="four columns"),


            # LCOE Recalc
            html.Div([
                html.H5("Recalculate With New Costs*",
                        title=("Recalculating will not re-sort transmission "
                               "connections so there will be some error with "
                               "Transmission Capital Costs, LCOT, and Total "
                               "LCOE.")),
                dcc.Tabs(
                    id="recalc_tab",
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
                              selected_style=TABLET_STYLE_CLOSED),          
                    ]
                ),

                html.Div(
                    id="recalc_tab_options",
                    children=[
                       dcc.Tabs(
                            id="recalc_scenario",
                            value="scenario_a",
                            style=TAB_STYLE,
                            children=[
                              dcc.Tab(value='scenario_a',
                                      label='Scenario A',
                                      style=TABLET_STYLE,
                                      selected_style=TABLET_STYLE_CLOSED),
                              dcc.Tab(value='scenario_b',
                                      label='Scenario B',
                                      style=TABLET_STYLE,
                                      selected_style=TABLET_STYLE_CLOSED),
                            ]
                        ),

                        # Long table of scenario A recalc parameters
                        html.Div(
                            id="recalc_a_options",
                            children=[
                                # FCR A
                                html.Div([
                                    html.P("FCR % (A): ",
                                           className="three columns",
                                           style={"height": "60%"}),
                                    dcc.Input(id="fcr1", type="number",
                                              className="nine columns",
                                              style={"height": "60%"},
                                              value=None),
                                ], className="row"),

                                # CAPEX A
                                html.Div([
                                    html.P("CAPEX $/KW (A): ",
                                           className="three columns",
                                           style={"height": "60%"}),
                                    dcc.Input(id="capex1", type="number",
                                              className="nine columns",
                                              style={"height": "60%"}),
                                ], className="row"),
                        
                                # OPEX A
                                html.Div([
                                    html.P("OPEX $/KW (A): ",
                                           className="three columns",
                                           style={"height": "60%"}),
                                    dcc.Input(id="opex1", type="number",
                                              className="nine columns",
                                              style={"height": "60%"}),
                                ], className="row"),

                                # Losses A
                                html.Div([
                                    html.P("Losses % (A): ",
                                           className="three columns",
                                           style={"height": "60%"}),
                                    dcc.Input(id="losses1", type="number",
                                              className="nine columns",
                                              style={"height": "60%"}),
                                ], className="row")
                        ]),
    
                    html.Div(
                        id="recalc_b_options",
                        children=[
                            # FCR B
                            html.Div([
                                html.P("FCR % (B): ",
                                       className="three columns",
                                       style={"height": "60%"}),
                                dcc.Input(id="fcr2", type="number",
                                          className="nine columns",
                                          style={"height": "60%"}),
                            ], className="row"),
                    
                            # CAPEX B
                            html.Div([
                                html.P("CAPEX $/KW (B): ",
                                       className="three columns",
                                       style={"height": "60%"}),
                                dcc.Input(id="capex2", type="number",
                                          className="nine columns",
                                          style={"height": "60%"}),
                            ], className="row"),
                    
                            # OPEX B
                            html.Div([
                                html.P("OPEX $/KW (B): ",
                                       className="three columns",
                                       style={"height": "60%"}),
                                dcc.Input(id="opex2", type="number",
                                          className="nine columns",
                                          style={"height": "60%"}),
                            ], className="row"),

                            # Losses B
                            html.Div([
                                html.P("Losses % (B): ",
                                       className="three columns",
                                       style={"height": "60%"}),
                                dcc.Input(id="losses2", type="number",
                                          className="nine columns",
                                          style={"height": "60%"}),
                            ], className="row")
                    ]),
                ]),

                html.Hr(),

            ], className="four columns"),




        ], id="options", className="row", style={"margin-bottom": "50px"}),


        # Submit Button to avoid repeated callbacks
        html.Div([
            html.Button(
                id="submit",
                children="Submit",
                style=BUTTON_STYLES["on"],
                title=("Click to submit options"),
                className="two columns"
            ),
        ], style={"margin-left": "50px"}, className="row"),

        html.Hr(style={"width": "98%",
                       "border-top": "2px solid #fccd34",
                       "border-bottom": "3px solid #1663b5"}),

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

                # Below Map Options
                html.Div([

                    # Left options
                    html.Div([
                        html.H6("Point Size:",
                            style={"margin-left": 5},
                            className="three columns"),
                        dcc.Input(
                            id="map_point_size",
                            value=5,
                            type="number",
                            className="two columns",
                            style={"width": "11%", "margin-left": "-20px"}
                        ),
                        html.H6("Color Min: ", className="three columns"),
                        dcc.Input(
                            id="map_color_min",
                            placeholder="",
                            type="number",
                            className="two columns",
                            style={"width": "11%", "margin-left": "-20px"}
                        ),
                        html.H6("Color Max: ", className="three columns"),
                        dcc.Input(
                            id="map_color_max",
                            placeholder="",
                            type="number",
                            className="two columns",
                            style={"width": "11%", "margin-left": "-20px"}
                        )
                    ], className="seven columns", style=BOTTOM_DIV_STYLE),

                    # Right option
                    html.Button(
                        id="rev_color",
                        children="Reverse Map Color: Off",
                        n_clicks=0,
                        type="button",
                        title=("Click to render the map with the inverse of "
                               "the chosen color ramp."),
                        style=RC_STYLES["on"], className="one column"
                    )
                ]),
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
                                className="seven columns",
                                style={"margin-left": 7}
                                ),
                        dcc.Input(
                            id="chart_point_size",
                            value=5,
                            type="number",
                            className="two columns",
                            style={"width": "35%", "margin-left": "-5px"}
                        ),
                    ],
                    className="row",
                    style={**BOTTOM_DIV_STYLE, **{"width": "18%"}}
                    ),
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

        # Because we can't have a callback with no output
        html.Div(
            id="catch_low_cost",
            style={"display": "none"}
            ),

        # Interim way to share data between map and chart
        html.Div(
            id="map_signal",
            children=DEFAULT_SIGNAL,
            style={"display": "none"}
            ),

        # This table of recalc parameters
        html.Div(
            id="recalc_table",
            children=json.dumps(RECALC_TABLE),
            style={"display": "none"}
            ),

    ]
)


# Support functions
def build_map_layout(mapview, title, basemap, title_size=18):
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

        # We'll need to change the color drop down options for categorical
        # colors = seq_colors.__dict__[color][::len(cats)]

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
        data = [
            dict(
                type='scattermapbox',
                lon=df['longitude'],
                lat=df['latitude'],
                text=df['text'],
                mode='markers',
                hoverinfo='text',
                hovermode='closest',
                showlegend=showlegend,
                marker=marker,
                render_mode="webgl",
                editable="true"
            )
        ]

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


def build_spec_split(path, project):
    """Calculate the percentage of each scenario present."""
    df = cache_table(project, path)
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


def build_title(df, project, path, path2, y, x,  diff, recalc_table=None):
    """Create chart title."""
    # print_args(build_title, df, path, path2, y, x,  difference, recalc,
#                title_size)
    config = Config(project)
    s1 = os.path.basename(path).replace("_sc.csv", "")
    s1 = " ".join(s1.split("_")).capitalize()

    # User specified FCR?
    if recalc_table:
        msgs = []
        for k, v in recalc_table["scenario_a"].items():
            if v:
                msgs.append(f"{k}: {v}")
        if msgs:
            reprint = ", ".join(msgs)
            s1 += f" ({reprint})" 

    title = s1 + "  |  " + config.titles[y]

    if y in AGGREGATIONS:
        ag_fun = AGGREGATIONS[y]
        if ag_fun == "mean":
            conditioner = "Unweighted mean"
        else:
            conditioner = "Total"

        # Difference title
        if diff == "on":
            ag = "mean"
            s2 = os.path.basename(path2).replace("_sc.csv", "")
            s2 = "  ".join([s.capitalize() for s in s2.split("_")])
            if recalc_table:
                msgs = []
                for k, v in recalc_table["scenario_b"].items():
                    if v:
                        msgs.append(f"{k}: {v}")
                if msgs:
                    reprint = ", ".join(msgs)
                    s2 += f" ({reprint})" 

                title = "{} vs <br>{} | ".format(s1, s2) + config.titles[y]
            else:
                title = "{} vs {} | ".format(s1, s2) + config.titles[y]
            conditioner = "% Difference | Average"
            units = ""

        # Map title (not chart)
        if isinstance(df, pd.core.frame.DataFrame):
            if y == "capacity":
                ag = round(df[y].apply(ag_fun) / 1_000_000, 2)
                if diff == "on":
                    units = ""
                else:
                    units = "TW"
            else:
                ag = round(df[y].apply(ag_fun), 2)
                if diff == "on":
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
     units, mask, recalc_table, recalc, project] = json.loads(signal)
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
def cache_table(project, path, recalc_table=None, recalc="off"):
    """Read in just a single table."""
    # Get the table
    data = Data(project)
    if recalc == "on" and path in data.files.values():
        df = data.build(path, **recalc_table)
    else:
        df = data.read(path)

    # We want some consistent fields
    df["index"] = df.index
    if "print_capacity" not in df.columns:
        df["print_capacity"] = df["capacity"].copy()
    if "total_lcoe_threshold" not in df.columns:
        df["total_lcoe_threshold"] = df["total_lcoe"].copy()
        df["mean_lcoe_threshold"] = df["mean_lcoe"].copy()
    return df


@cache2.memoize()
def cache_map_data(signal):
    """Read and store a data frame from the config and options given."""
    # Get signal elements
    [path, path2, y, x, difference, states, ymin, ymax, threshold,
     units, mask, recalc_table, recalc, project] = json.loads(signal)

    # Unpack recalc table
    recalc_a = recalc_table["scenario_a"]
    recalc_b = recalc_table["scenario_b"]

    # Read and cache first table
    df1 = cache_table(project, path, recalc_a, recalc)

    # Separate the threshold values out
    threshold_field = threshold[0]
    threshold = threshold[1]

    # Is it faster to subset columns before rows?
    keepers = [y, x, "print_capacity", "total_lcoe_threshold",
               "mean_lcoe_threshold", "state", "nrel_region", "county",
               "latitude", "longitude", "sc_point_gid", "index"]
    df1 = df1[keepers]

    # For other functions this data frame needs an x field
    if y == x:
        df1 = df1.iloc[:, 1:]

    # If there's a second table, read/cache the difference
    if path2:
        # Match the format of the first dataframe
        df2 = cache_table(project, path2, recalc_b)
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
     units, mask, recalc_table, recalc, project] = json.loads(signal)
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
    trig = dash.callback_context.triggered[0]['prop_id'].split(".")[0]
    if filedf:
#        print_args(options_lchh_group, group, filedf, trig=trig)
        filedf = json.loads(filedf)
        filedf = pd.DataFrame(filedf)
        options = filedf[group].unique()
        option_list = [{"label": o, "value": o} for o in options]
        return option_list, options[0]
    else:
        raise PreventUpdate


@app.callback([Output("low_cost_group_tab_div", "style"),
               Output("low_cost_list", "style"),
               Output("low_cost_split_group_div", "style"),
               Output("low_cost_submit", "style")],
              [Input("low_cost_tabs", "value"),
               Input("low_cost_group_tab", "value")])
def options_low_cost_toggle(choice, how):
    """Show the grouping options for the low cost function.

    (Make container Div.)
    """
    submit_style = {
        **BUTTON_STYLES["on"],
        **{"background-color": "#F9F9F9", "border-color": "#D6D6D6",
           "margin": "0 auto"}}

    if choice == "on":
        style1 = {}
    else:
        style1 = {"display": "none"}
        submit_style = {"display": "none"}

    if how == "all":
        style2 = {"display": "none"}
        style3 = {"display": "none"}

    elif how == "list":
        style2 = {}
        style3 = {"display": "none"}
    else:
        style2 = {"display": "none"}
        style3 = {}
    return style1, style2, style3, submit_style


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
               Output("low_cost_list", "options"),
               Output("scenario_a", "value"),
               Output("scenario_b", "value"),
               Output("low_cost_list", "value"),
               Output("variable", "options"),
               Output("low_cost_split_group", "options"),
               Output("filedf", "children")],
              [Input("project", "value"),
               Input("catch_low_cost", "children")])
def options_options(project, lc_update):
    """Update the options given a project."""
    # Catch the trigger
    trig = dash.callback_context.triggered[0]['prop_id'].split(".")[0]
    print_args(options_options, project, lc_update, trig=trig)

    # We need the project configuration
    config = Config(project)

    # Find the files
    DP = Data_Path(config.project_config["directory"])
    filedf = pd.DataFrame(config.project_config["data"])
    scneario_outputs = DP.contents("review_outputs", "least_cost*_sc.csv")
    scenario_originals = list(filedf["file"].values)
    files = scenario_originals + scneario_outputs
    names = [os.path.basename(f).replace("_sc.csv", "") for f in files]
    names = [" ".join([n.capitalize() for n in name.split("_")])
             for name in names]
    file_list = dict(zip(names, files))

    # Infer the groups
    groups = [c for c in filedf.columns if c not in ["file", "name"]]

    # Build the options lists
    group_options = [{"label": g, "value": g} for g in groups]
    scenario_options = [
        {"label": key, "value": file} for key, file in file_list.items()
    ]
    variable_options = []
    for k, v in config.project_config["titles"].items():
        variable_options.append({"label": v, "value": k})
    least_cost_options = []
    for key, file in file_list.items():
        if file in config.files.values():
            option = {"label": key, "value": file}
            least_cost_options.append(option)

    # Lots of returns here, abbreviating for space
    so = scenario_options
    lco = least_cost_options
    sva = so[0]["value"]
    svb = so[1]["value"]
    vo = variable_options
    go = group_options
    fdf = json.dumps(filedf.to_dict())

    # Update options and value if least cost was just used
    if "catch_low_cost" in trig:
        so = json.loads(lc_update)
        sva = so[-1]["value"]

    return so, so, lco, sva, svb, sva, vo, go, fdf


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
    project = options[0]["value"]
    return options, project


@app.callback(Output("recalc_a_options", "children"),
              [Input("project", "value"),
               Input("scenario_a", "value")],
              [State("recalc_table", "children")])
def options_recalc_a(project, scenario, recalc_table):
    """Update the drop down options for each scenario."""
    print_args(options_recalc_a, project, scenario, recalc_table)
    data = Data(project)
    recalc_table = json.loads(recalc_table)
    scenario = os.path.basename(scenario).replace("_sc.csv", "")
    if scenario not in data.scenarios:
        raise PreventUpdate
    table = recalc_table["scenario_a"]
    otable = data.original_parameters(scenario)
    children = [
        # FCR A
        html.Div([
            html.P("FCR % (A): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="fcr1", type="number", className="nine columns",
                      style={"height": "60%"},
                      value=table["fcr"], placeholder=otable["fcr"]),
        ], className="row"),

        # CAPEX A
        html.Div([
            html.P("CAPEX $/KW (A): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="capex1", type="number", className="nine columns",
                      style={"height": "60%"},
                      value=table["capex"], placeholder=otable["capex"]),
        ], className="row"),

        # OPEX A
        html.Div([
            html.P("OPEX $/KW (A): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="opex1", type="number", className="nine columns",
                      style={"height": "60%"},
                      value=table["opex"], placeholder=otable["opex"]),
        ], className="row"),

        # Losses A
        html.Div([
            html.P("Losses % (A): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="losses1", type="number", className="nine columns",
                      value=table["losses"], placeholder=otable["losses"],
                      style={"height": "60%"}),
        ], className="row")]

    return children


@app.callback(Output("recalc_b_options", "children"),
              [Input("project", "value"),
               Input("scenario_b", "value")],
              [State("recalc_table", "children")])
def options_recalc_b(project, scenario, recalc_table):
    """Update the drop down options for each scenario."""
    print_args(options_recalc_b, project, scenario, recalc_table)
    data = Data(project)
    recalc_table = json.loads(recalc_table)
    scenario = os.path.basename(scenario).replace("_sc.csv", "")
    if scenario not in data.scenarios:
        raise PreventUpdate

    table = recalc_table["scenario_b"]
    otable = data.original_parameters(scenario)
    scenario = os.path.basename(scenario).replace("_sc.csv", "")
    table = recalc_table["scenario_b"]
    otable = data.original_parameters(scenario)
    children = [
        # FCR B
        html.Div([
            html.P("FCR % (B): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="fcr2", type="number", className="nine columns",
                      style={"height": "60%"},
                      value=table["fcr"], placeholder=otable["fcr"]),
        ], className="row"),

        # CAPEX B
        html.Div([
            html.P("CAPEX $/KW (B): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="capex2", type="number", className="nine columns",
                      style={"height": "60%"},
                      value=table["capex"], placeholder=otable["capex"]),
        ], className="row"),

        # OPEX B
        html.Div([
            html.P("OPEX $/KW (B): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="opex2", type="number", className="nine columns",
                      style={"height": "60%"},
                      value=table["opex"], placeholder=otable["opex"]),
        ], className="row"),

        # Losses B
        html.Div([
            html.P("Losses % (B): ", className="three columns",
                   style={"height": "60%"}),
            dcc.Input(id="losses2", type="number", className="nine columns",
                      value=table["losses"], placeholder=otable["losses"],
                      style={"height": "60%"}),
        ], className="row")]

    return children


@app.callback([Output("recalc_tab_options", "style"),
               Output("recalc_a_options", "style"),
               Output("recalc_b_options", "style")],
              [Input("recalc_tab", "value"),
               Input("recalc_scenario", "value")])
def options_recalc_toggle(recalc, scenario):
    """Toggle the recalc options on and off."""
    tab_style = {}
    recalc_a_style = {}
    recalc_b_style = {}

    # Toggle all options
    if recalc == "off":
        tab_style = {"display": "none"}
    if scenario == "scenario_a":
        recalc_b_style = {"display": "none"}
    else:
        recalc_a_style = {"display": "none"}    

    return tab_style, recalc_a_style, recalc_b_style


@app.callback([Output("options", "style"),
               Output("toggle_options", "children"),
               Output("toggle_options", "style")],
              [Input('toggle_options', 'n_clicks')])
def options_toggle_options(click):
    """Toggle options on/off."""
    if not click:
        click = 0
    if click % 2 != 1:
        block_style = {"display": "none"}
        button_children = 'Options: Off'
        button_style = BUTTON_STYLES["off"]
    else:
        block_style = {"margin-bottom": "50px"}
        button_children = 'Options: On'
        button_style = {**BUTTON_STYLES["on"], **{"margin-bottom": "35px"}}

    return block_style, button_children, button_style


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
        style = RC_STYLES["off"]
    else:
        children = 'Reverse Map Color: On'
        style = RC_STYLES["on"]

    return children, style


@app.callback(Output("catch_low_cost", "children"),
              [Input("low_cost_submit", "n_clicks")],
              [State("project", "value"),
               State("low_cost_group_tab", "value"),
               State("low_cost_list", "value"),
               State("low_cost_split_group", "value"),
               State("low_cost_split_group_options", "value"),
               State("scenario_a", "options"),
               State("low_cost_by", "value"),
               State("recalc_table", "children")])
def retrieve_low_cost(submit, project, how, lst, group, group_choice, options,
                      by, recalc_table):
    """Calculate low cost fields based on user decision."""
    print_args(retrieve_low_cost, submit, project, how, lst, group,
               group_choice, options, by, recalc_table)

    if not submit:
        raise PreventUpdate

    config = Config(project)
    DP = Data_Path(config.directory)

    # Make a tag for all of our recalc values
    if recalc_table:
        recalc_table = json.loads(recalc_table)
        tags = []
        for k, v in recalc_table["scenario_a"].items():
            if v:
                tag = "{:05d}{}".format(round(float(v) * 1000), k)
                tags.append(tag)
        recalc_tag = "_".join(tags)

    # Build the appropriate paths and target file name
    if how == "all":
        # Just one output
        if recalc_table:
            fname = f"least_cost_by_{by}_{recalc_tag}_all_sc.csv"
        else:
            fname = f"least_cost_by_{by}_all_sc.csv"
        paths = FILEDF["file"].values
    elif how == "list":
        # Just one output
        paths = lst
        scenarios = [os.path.basename(path).split("_")[1] for path in paths]
        scen_key = "_".join(scenarios)
        if recalc_table:
            fname = f"least_cost_by_{by}_{scen_key}_{recalc_tag}_sc.csv"
        else:
            fname = f"least_cost_by_{by}_{scen_key}_sc.csv"
    else:
        # This could create multiple outputs, but we'll do one at a time
        grp_key = group_choice.replace(".", "")
        if recalc_table:
            fname = f"least_cost_by_{by}_{group}_{grp_key}_{recalc_tag}_sc.csv"
        else:
            fname = f"least_cost_by_{by}_{group}_{grp_key}_sc.csv"
        paths = FILEDF["file"][FILEDF[group] == group_choice].values

    # Build full paths and create the target file
    paths = [DP.join(path) for path in paths]
    lchh_path = DP.join("review_outputs", fname, mkdir=True)
    print("calculating" + " " + lchh_path + "...")
    calculator = Least_Cost(project, recalc_table=recalc_table)
    calculator.calc(paths, lchh_path, by=by)

    # Update the scenario file options
    label = " ".join([f.capitalize() for f in fname.split("_")[:-1]])
    if label not in [o["label"] for o in options]:
        option = {"label": label, "value": lchh_path}
        options.append(option)
    return json.dumps(options)


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
              [State("project", "value"),
               State("upper_lcoe_threshold", "value"),
               State("threshold_field", "value"),
               State("scenario_a", "value"),
               State("scenario_b", "value"),
               State("lchh_path", "children"),
               State("variable", "value"),
               State("chart_xvariable_options", "value"),
               State("difference", "value"),
               State("low_cost_tabs", "value"),
               State("threshold_mask", "value"),
               State("recalc_table", "children"),
               State("recalc_tab", "value")])
def retrieve_map_signal(submit, states, chart, project, threshold,
                        threshold_field, path, path2, lchh_path, y, x, diff,
                        lchh_toggle, mask, recalc_table, recalc):
    """Create signal for sharing data between map and chart with dependence."""
    print_args(retrieve_map_signal, submit, states, chart, project, threshold,
                threshold_field, path, path2, lchh_path, y, x, diff,
                lchh_toggle, mask, recalc_table, recalc)
    trig = dash.callback_context.triggered[0]['prop_id']
    print("trig = '" + trig + "'")

    # Prevent the first trigger when difference is off
    if "scenario_b" in trig and diff == "off":
        raise PreventUpdate

    # Prevent the first trigger when mask is off
    if "mask" in trig and mask == "off":
        raise PreventUpdate

    # Get/build the value scale table
    config = Config(project)
    scales = config.project_config["scales"]

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

    # Unpack recalc table
    if recalc_table:
        recalc_table = json.loads(recalc_table)

    # Let's just recycle all this for the chart
    signal = json.dumps([path, path2, y, x, diff, states, ymin, ymax,
                         threshold, units, mask, recalc_table, recalc, project])
    return signal


@app.callback(Output("recalc_table", "children"),
              [Input("fcr1", "value"),
               Input("capex1", "value"),
               Input("opex1", "value"),
               Input("losses1", "value"),
               Input("fcr2", "value"),
               Input("capex2", "value"),
               Input("opex2", "value"),
               Input("losses2", "value"),
               Input("project", "value")])
def retrieve_recalc_parameters(fcr1, capex1, opex1, losses1,
                               fcr2, capex2, opex2, losses2,
                               project):
    """Retrive all given recalc values and store them."""
    trig = dash.callback_context.triggered[0]['prop_id'].split(".")[0]
    if "project" == trig:
        recalc_table = {
            "scenario_a": {
                "fcr": None, "capex": None, "opex": None, "losses": None
            },
            "scenario_b": {
                "fcr": None, "capex": None, "opex": None, "losses": None
            }
        }
    else:
        recalc_table = {
            "scenario_a":{
                "fcr": fcr1,
                "capex": capex1,
                "opex": opex1,
                "losses": losses1,
            },
            "scenario_b": {
                "fcr": fcr2,
                "capex": capex2,
                "opex": opex2,
                "losses": losses2
            }
        }
    return json.dumps(recalc_table)


@app.callback([Output("scenario_a_specs", "children"),
               Output("scenario_b_specs", "children")],
              [Input("scenario_a", "value"),
               Input("scenario_b", "value"),
               Input("project", "value")])
def scenario_specs(scenario_a, scenario_b, project):
    """Output the specs association with a chosen scenario."""
    # print_args(scenario_specs, scenario_a, scenario_b)
    if "least_cost" not in scenario_a:
        scenario_a = scenario_a.replace("_sc.csv", "")
        specs1 = build_specs(scenario_a, project)
    else:
        specs1 = build_spec_split(scenario_a, project)

    if "least_cost" not in scenario_b:
        scenario_b = scenario_b.replace("_sc.csv", "")
        specs2 = build_specs(scenario_b, project)
    else:
        specs2 = build_spec_split(scenario_b, project)

    return specs1, specs2


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
              [State("project", "value"),
               State("map", "relayoutData"),
               State("map", "selectedData")])
def make_map(signal, basemap, color, chartsel, point_size,
             rev_color, uymin, uymax, project, mapview, mapsel):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    print_args(make_map, signal, basemap, color, chartsel, point_size,
               rev_color, uymin, uymax, project, mapview, mapsel)
    trig = dash.callback_context.triggered[0]['prop_id']
    print("'MAP'; trig = '" + str(trig) + "'")

    # Get map elements from data signal
    df = cache_map_data(signal)
    df.index = df["index"]
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units, mask, recalc_table, recalc, project] = json.loads(signal)

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
    if recalc == "off":
        recalc_table = None
    data = build_scatter(df, y, x, units, color, rev_color, ymin, ymax,
                         point_size)
    title = build_title(df, project, path, path2, y, x, diff, recalc_table)
    layout = build_map_layout(mapview, title, basemap)
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
              [State("project", "value"),
               State("chart", "relayoutData"),
               State("chart", "selectedData")])
def make_chart(signal, chart, mapsel, point_size, op_values, region,
               uymin, uymax, project, chartview, chartsel):
    """Make one of a variety of charts."""
#    print_args(make_chart, signal, chart, mapsel, point_size, op_values,
#                region, chartview, chartsel)
    trig = dash.callback_context.triggered[0]['prop_id']
    print("trig = '" + str(trig) + "'")

    # Unpack the signal
    [path, path2, y, x, diff, states, ymin, ymax, threshold,
     units, mask, recalc_table, recalc, project] = json.loads(signal)

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

    # Get the data frames
    dfs = cache_chart_tables(signal, region, idx)
    plotter = Plots(project, dfs, group, point_size, yunits=units)

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
    if recalc == "off":
        recalc_table = None
    title = build_title(dfs, project, path, path2, y, x, diff, recalc_table)

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
        font_size=15,
        margin=dict(l=70, r=20, t=115, b=20),
        height=700,
        hovermode="x unified",
        paper_bgcolor="#1663B5",
        legend_title_text=group,
        dragmode="select",
        yaxis=dict(range=ylim),
        titlefont=dict(color="white",
                       size=18,
                       family="Time New Roman"),
        title=dict(
                text=title,
                yref="container",
                x=0.05,
                y=0.94,
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
