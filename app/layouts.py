# -*- coding: utf-8 -*-
"""The scenario page html layout.

Created on Tue Jul  6 15:23:09 2021

@author: twillia2
"""
import copy
import json

import dash_core_components as dcc
import dash_html_components as html

from review.support import (BASEMAPS, BOTTOM_DIV_STYLE, BUTTON_STYLES,
                            CHART_OPTIONS, COLOR_OPTIONS, DEFAULT_MAPVIEW,
                            STATES, TAB_STYLE, TABLET_STYLE)


# Everything below goes into a css
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

RC_STYLES = copy.deepcopy(BUTTON_STYLES)
RC_STYLES["off"]["border-color"] = RC_STYLES["on"]["border-color"] = "#1663b5"
RC_STYLES["off"]["border-width"] = RC_STYLES["on"]["border-width"] = "3px"
RC_STYLES["off"]["border-top-width"] = "0px"
RC_STYLES["on"]["border-top-width"] = "0px"
RC_STYLES["off"]["border-radius-top-left"] = "0px"
RC_STYLES["on"]["border-radius-top-right"] = "0px"
RC_STYLES["off"]["float"] = RC_STYLES["on"]["float"] = "right"
# Everything above goes into css


def scenario_layout(defaults):
    """Return the scenario layout with preset default values.

    Parameters
    ----------
        defaults : review.support.Defaults
            A review defaults object.

    Returns
    -------
        dash.development.base_component.ComponentMeta
            A DASH html div containing the scenario page components.
    """
    layout = html.Div(
        children=[

            # Constant info block
            html.Div([

                # Project Selection
                html.Div([
                    html.H4("Project"),
                    dcc.Dropdown(
                        id="project",
                        options=defaults.project_options,
                        value=defaults.project
                    )
                ], className="three columns"),

                # Print total capacity after all the filters are applied
                html.Div([
                    html.H5("Remaining Generation Capacity: "),
                    html.H1(id="capacity_print", children="")
                ], className="three columns")

            ], className="row", style={"margin-bottom": "35px"}),

            # Toggle Options Top
            html.Div([
                html.Button(
                    id="toggle_options",
                    children="Options: Off",
                    n_clicks=0,
                    type="button",
                    title=("Click to display options"),
                    style=BUTTON_STYLES["off"],
                    className="two columns"),
            ], className="row",
               style={"margin-left": "50px",
                      "margin-right": "1px",
                      "margin-bottom": "1px"}),

            html.Hr(className="row",
                    style={"width": "92%",
                           "margin-left": "53px",
                           "margin-right": "10px",
                           "margin-bottom": "-1px",
                           "margin-top": "-1px",
                           "border-bottom": "2px solid #fccd34",
                           "border-top": "3px solid #1663b5"}),

            # Data Options
            html.Div([

                # First Scenario
                html.Div([
                    html.H5("Scenario A"),
                    dcc.Dropdown(
                        id="scenario_a",
                        options=defaults.scenario_options,
                        value=defaults.scenario_choices["a"]
                    ),
                    dcc.Markdown(
                        id="scenario_a_specs",
                        style={"margin-left": "15px", "font-size": "11pt",
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
                                options=defaults.scenario_options,
                                value=defaults.scenario_choices["b"]
                            ),
                            dcc.Markdown(
                                id="scenario_b_specs",
                                style={"margin-left": "15px",
                                       "font-size": "11pt",
                                       "height": "300px",
                                       "overflow-y": "scroll"}
                            )
                        ], className="three columns")
                    ],
                    style={"margin-left": "50px"}),

                # Variable options
                html.Div([
                    html.H5("Variable"),
                    dcc.Dropdown(id="variable",
                                 options=defaults.variable_options,
                                 value="mean_lcoe"),
                ], className="two columns"),

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
                    dcc.Tabs(
                        id="difference_units",
                        value="percent",
                        style=TAB_STYLE,
                        children=[
                            dcc.Tab(value='percent',
                                    label='Percentage',
                                    style=TABLET_STYLE,
                                    selected_style=TAB_BOTTOM_SELECTED_STYLE),
                            dcc.Tab(value='original',
                                    label='Original Units',
                                    style=TABLET_STYLE,
                                    selected_style=TAB_BOTTOM_SELECTED_STYLE)
                        ]),
                    html.Hr()
                ], className="two columns"),

                # Turn off weighted aggregations for speed
                html.Div([
                    html.H5("Spatially Weighted Averages*",
                            title="Check that this is working."),
                    dcc.Tabs(
                        id="weights",
                        value="on",
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
                            title=("This will save and add the least cost "
                                   "table to the scenario A and B options. "
                                   "Submit below to generate the table, then "
                                   "select the resulting dataset in the "
                                   "dropdown. If recalculating, just use "
                                   "scenario A's inputs, we're still working "
                                   "on this part.")),
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
                                    dcc.Tab(
                                        value='total_lcoe',
                                        label='Total LCOE',
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE_CLOSED
                                    ),
                                    dcc.Tab(
                                        value='mean_lcoe',
                                        label='Site LCOE',
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE_CLOSED
                                    ),
                                ]
                            ),
                            dcc.Tabs(
                                id="low_cost_group_tab",
                                value="all",
                                style=TAB_STYLE,
                                children=[
                                    dcc.Tab(
                                        value="all",
                                        label="All",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE_CLOSED
                                    ),
                                    dcc.Tab(
                                        value="group",
                                        label="Group",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE_CLOSED
                                    ),
                                    dcc.Tab(
                                        value="list",
                                        label="List",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE_CLOSED
                                    )
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
                                                options=defaults.group_options,
                                                value=defaults.group_options[0]["value"]
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
                            title=("Recalculating will not re-sort "
                                   "transmission connections so there will be "
                                   "some error with Transmission Capital "
                                   "Costs, LCOT, and Total LCOE.")),
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
                                    dcc.Tab(
                                        value='scenario_a',
                                        label='Scenario A',
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE_CLOSED
                                    ),
                                    dcc.Tab(
                                        value='scenario_b',
                                        label='Scenario B',
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE_CLOSED
                                    ),
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

            html.Hr(style={"width": "92%",
                           "margin-left": "53px",
                           "margin-right": "10px",
                           "margin-bottom": "1px",
                           "margin-top": "-1px",
                           "border-top": "2px solid #fccd34",
                           "border-bottom": "3px solid #1663b5"}),

            # Submit Button to avoid repeated callbacks
            html.Div([
                html.Button(
                    id="submit",
                    children="Submit",
                    style=BUTTON_STYLES["on"],
                    title=("Click to submit options"),
                    className="two columns"
                ),
            ], style={"margin-left": "50px",
                      "margin-bottom": "25px",
                      "margin-top": "2px"},
               className="row"),


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
                                dcc.Tab(
                                    value='state',
                                    label='State',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE
                                ),
                                dcc.Tab(
                                    value='basemap',
                                    label='Basemap',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE
                                ),
                                dcc.Tab(
                                    value='color',
                                    label='Color Ramp',
                                    style=TABLET_STYLE,
                                    selected_style=TABLET_STYLE
                                )
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
                            "plotlyServerURL":
                                "https://chart-studio.plotly.com",
                            "toImageButtonOptions":
                                {"width": 1250, "height": 750},
                        }
                    ),

                    # Below Map Options
                    html.Div([

                        # Left options
                        html.Div([
                            html.P("Point Size:",
                                   style={"margin-left": 5, "margin-top": 7},
                                   className="two columns"),
                            dcc.Input(
                                id="map_point_size",
                                value=5,
                                type="number",
                                debounce=True,
                                className="one columns",
                                style={"margin-left": "-1px",
                                       "width": "10%"}
                            ),
                            html.P("Color Min: ",
                                   style={"margin-top": 7},
                                   className="two columns"),
                            dcc.Input(
                                id="map_color_min",
                                placeholder="",
                                type="number",
                                debounce=True,
                                className="one columns",
                                style={"margin-left": "-1px",
                                       "width": "10%"}
                            ),
                            html.P("Color Max: ",
                                   style={"margin-top": 7},
                                   className="two columns"),
                            dcc.Input(
                                id="map_color_max",
                                placeholder="",
                                debounce=True,
                                type="number",
                                className="one columns",
                                style={"margin-left": "-1px",
                                       "width": "10%"}
                            )
                        ], className="eight columns", style=BOTTOM_DIV_STYLE),

                        # Right option
                        html.Button(
                            id="rev_color",
                            children="Reverse Map Color: Off",
                            n_clicks=0,
                            type="button",
                            title=("Click to render the map with the inverse "
                                   "of the chosen color ramp."),
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
                                    dcc.Tab(value="chart",
                                            label="Chart Type",
                                            style=TABLET_STYLE,
                                            selected_style=TABLET_STYLE),
                                    dcc.Tab(value="xvariable",
                                            label="X Variable",
                                            style=TABLET_STYLE,
                                            selected_style=TABLET_STYLE),
                                    dcc.Tab(value="region",
                                            label="Region",
                                            style=TABLET_STYLE,
                                            selected_style=TABLET_STYLE),
                                    dcc.Tab(value="scenarios",
                                            label="Additional Scenarios",
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
                                    )
                                ]),

                            # X-axis Variable
                            html.Div(
                                id="chart_xvariable_options_div",
                                children=[
                                    dcc.Dropdown(
                                        id="chart_xvariable_options",
                                        clearable=False,
                                        options=defaults.variable_options,
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
                                        options=defaults.region_options,
                                        multi=False,
                                        value="national"
                                    )
                                ]),

                            # Scenario grouping
                            html.Div(
                                id="chart_scenarios_div",
                                children=[
                                    dcc.Dropdown(
                                        id="chart_scenarios",
                                        clearable=False,
                                        options=defaults.scenario_options,
                                        multi=True
                                    )
                                ]),
                        ]),
                    ], className="row"),

                    # The chart
                    dcc.Graph(
                        id="chart",
                        config={
                            "showSendToCloud": True,
                            "toImageButtonOptions":
                                {"width": 1250, "height": 750},
                            "plotlyServerURL":
                                "https://chart-studio.plotly.com"
                        }),

                    # Below Chart Options
                    html.Div(
                        id="chart_extra_div",
                        children=[
                            html.P("Point Size:",
                                   style={"margin-left": 5, "margin-top": 7},
                                   className="three columns"),
                            dcc.Input(
                                id="chart_point_size",
                                value=5,
                                type="number",
                                debounce=True,
                                className="two columns",
                                style={"margin-left": "-1px"}
                            ),
                            html.Div(
                                id="chart_xbin_div",
                                style={"margin-left": "10px"},
                                children=[
                                    html.P("Bin Size:",
                                           style={"margin-top": 7,
                                                  "margin-left": 5},
                                           className="three columns"),
                                    dcc.Input(
                                        className="two columns",
                                        style={"margin-left": 5},
                                        id="chart_xbin",
                                        debounce=True,
                                        value=None,
                                        type="number",
                                    )
                                ]
                            ),
                        ],
                        className="five columns", style=BOTTOM_DIV_STYLE
                    ),
                ], className="six columns"),

            ], className="row"),

            # Characterization Chart
            html.Div(
                id="char_div",
                children=[
                    html.Div([
                        # Chart options
                        html.H3("Characterization Layers*",
                                title=("Selections do not affect the map "
                                       "or chart above."),
                                style={"text-align": "center"}),
                        dcc.Tabs(
                            id="char_chart_options_tab",
                            value="char_option_1",
                            style=TAB_STYLE,
                            children=[
                                dcc.Tab(value="variable",
                                        label="Variable",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE),
                                dcc.Tab(value="char_option_2",
                                        label="Option #2",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE),
                                dcc.Tab(value="char_option_3",
                                        label="Option #3",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE),
                                dcc.Tab(value="char_option_4",
                                        label="Option #4",
                                        style=TABLET_STYLE,
                                        selected_style=TABLET_STYLE)
                                ]),

                        html.Div(
                            id="char_var_options_div",
                            children=[
                                dcc.Dropdown(
                                    id="char_variable",
                                    options=defaults.category_options,
                                    value=defaults.category_options[0]["value"]
                                )
                            ]),

                        # The chart
                        dcc.Graph(
                            id="char_chart",
                            config={
                                "showSendToCloud": True,
                                "toImageButtonOptions":
                                    {"width": 2400, "height": 350},
                                "plotlyServerURL":
                                    "https://chart-studio.plotly.com"
                            }),
                    ])
                ],
                className="row",
                style={"margin-top": "50px",
                       "margin-left": "50px",
                       "margin-right": "50px"}
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
                style={"display": "none"}
            ),

            # This table of recalc parameters
            html.Div(
                id="recalc_table",
                children=json.dumps(defaults.recalc_table),
                style={"display": "none"}
            ),

            # Capacity after make_map (avoiding duplicate calls)
            html.Div(
                id="mapcap",
                style={"display": "none"}
            )
        ]
    )

    return layout
