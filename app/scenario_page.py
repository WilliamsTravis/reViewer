"""View reV results using a configuration file.

Things to do:
    - Move styling to CSS
    - Improve caching
    - Speed up everything
    - Download option
    - Automate startup elements
    - Build categorical variable charts
"""
import copy
import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px

from app import app, cache, cache2, cache3
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from layouts import scenario_layout, RC_STYLES
from review import print_args
from review.support import (AGGREGATIONS, BUTTON_STYLES, COLOR_OPTIONS,
                            COLOR_Q_OPTIONS, COLORS, COLORS_Q, DEFAULT_MAPVIEW,
                            MAP_LAYOUT, TABLET_STYLE)
from review.support import (Categories, Config, Data, Data_Path, Defaults,
                            Difference, Least_Cost, Plots, point_filter, wmean)


# Default object for initial layout
PROJECT = "Transition"
DEFAULTS = Defaults(project=PROJECT)
layout = scenario_layout(DEFAULTS)


# More Support functions  <--------------------------------------------------- Move to module
def build_map_layout(mapview, title, basemap, showlegend, ymin, ymax,
                     title_size=18):
    """Build the map data layout dictionary."""
    layout = copy.deepcopy(MAP_LAYOUT)
    layout["mapbox"]["center"] = mapview["mapbox.center"]
    layout["mapbox"]["zoom"] = mapview["mapbox.zoom"]
    layout["mapbox"]["bearing"] = mapview["mapbox.bearing"]
    layout["mapbox"]["pitch"] = mapview["mapbox.pitch"]
    layout["mapbox"]["style"] = basemap
    layout["showlegend"] = showlegend
    layout["title"]["text"] = title
    layout["yaxis"] = dict(range=[ymin, ymax])
    layout["legend"] = dict(
        title_font_family="Times New Roman",
        bgcolor="#E4ECF6",
        font=dict(
            family="Times New Roman",
            size=15,
            color="black"
        )
    )
    return layout


def build_name(path):
    """Infer scenario name from path."""
    name = os.path.basename(path).replace("_sc.csv", "")
    name = " ".join([n.capitalize() for n in name.split("_")])
    return name


class Scatter():
    """Methods for building scatter plots.  NOT DONE YET."""

    def __init__(self, project, dfs, x, y, color, rev_color, ymin, ymax,
                 point_size, title, mapview, mapsel, basemap, title_size=18):
        """Initialize Scatter object."""
        self.project = project
        self.df = dfs
        self.x = x
        self.y = y
        self.rev_color
        self.ymin
        self.ymax
        self.point_size
        self.title
        self.mapview
        self.mapsel
        self.basemap
        self.title_size

    @property
    def config(self):
        """Return project Config object."""
        return Config(self.project)

    @property
    def formatted_df(self):
        """Format the data frame for use in the Plotly figure."""
        self.df["text"] = self.hover_text

    @property
    def hover_text(self):
        """Return hovertext for points."""
        text = self.df["county"] + " County, " + self.df["state"] + ": <br>   "
        if self.units == "category":
            text = text + self.df[self.y].astype(str) + " " + self.units
        else:
            text = (text + self.df[self.y].round(2).astype(str) + " "
                    + self.units)

        return text

    @property
    def units(self):
        """Return y-units."""
        return self.config.units[self.y]

    def build(self):
        """Build the Plotly figure object."""
        dfs = self.formatted_df


def build_scatter(df, y, x, units, color, rev_color, ymin, ymax, point_size,
                  title, mapview, mapsel, basemap, title_size=18):
    """Build a Plotly scatter plot dictionary for the map.

    Notes
    -----
    We should set this up in the same fashion as for the chart plots. We have
    to move any assignment of color parameters from the marker object to the
    plot object and manually reverse scales.
    """
    # Create hover text
    if units == "category":
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[y].astype(str) + " " + units)
    else:
        df["text"] = (df["county"] + " County, " + df["state"] + ": <br>   "
                      + df[y].round(2).astype(str) + " " + units)

    # Offshore points will be nans since they don't have states or counties
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

    # Categorical data will be made of multiple traces
    if units == "category":
        # We need to grab the actual rgb sequence for this
        pcolor = COLORS_Q[color]
        showlegend = True
        marker = dict(
            opacity=1.0,
            reversescale=rev_color,
            size=point_size,
        )

        # If y is a json dict, find the mode
        if Categories.is_json(df, y):
            # This will all be incorporated into the same class, so this is a
            # bit odd atm
            df[y] = Categories().mode(df, y)

        # Create data object
        figure = px.scatter_mapbox(
            data_frame=df,
            color=y,
            color_discrete_sequence=pcolor,
            lon="longitude",
            lat="latitude",
            custom_data=["sc_point_gid", "print_capacity"],
            hover_name="text",
        )

    # Continuous data will be just one trace
    else:
        pcolor = COLORS[color]
        showlegend = False
        marker = dict(
            color=df[y],
            colorscale=pcolor,
            cmax=float(ymax),
            cmin=float(ymin),
            opacity=1.0,
            reversescale=rev_color,
            size=point_size,
            colorbar=dict(
                title=dict(text=units,
                           font=dict(size=15, color="white",
                                     family="New Times Roman")),
                tickfont=dict(color="white", family="New Times Roman")
            )
        )

        # Create data object
        figure = px.scatter_mapbox(
            data_frame=df,
            lon="longitude",
            lat="latitude",
            custom_data=["sc_point_gid", "print_capacity"],
            hover_name="text",
        )

    # Update the layout
    layout = build_map_layout(mapview, title, basemap, showlegend,
                              ymin, ymax, title_size=18)
    figure.update_layout(**layout)
    figure.update_traces(marker=marker)

    return figure


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
    percentages = [round(p * 100, 4) for p in percentages]
    pdf = pd.DataFrame(dict(p=percentages, s=scenarios))
    pdf = pdf.sort_values("p", ascending=False)
    table = """| Scenario | Percentage |\n|----------|------------|\n"""
    for _, row in pdf.iterrows():
        row = "| {} | {}% |\n".format(row["s"], row["p"])
        table = table + row
    return table


def infer_recalc(title):
    """Quick title fix for recalc least cost paths."""  # <-------------------- Do better
    variables = ["fcr", "capex", "opex", "losses"]
    if "least cost" in title.lower():
        if any([v in title for v in variables]):
            title = title.replace("-", ".")
            first_part = title.split("  ")[0]
            recalc_part = title.split("  ")[1]
            new_part = []
            for part in recalc_part.split():
                letters = "".join([c for c in part if c.isalpha()])
                numbers = part.replace(letters, "")
                new_part.append(letters + ": " + numbers)
            title = first_part + " (" + ", ".join(new_part) + ")"
    return title



def build_title(df, signal_dict, weights=True): # ---------------------------> This needs to be its own class
    """Create chart title."""
    # print_args(build_title, df, signal_dict, weights)
    diff = signal_dict["diff"]
    units = signal_dict["units"]
    path = signal_dict["path"]
    path2 = signal_dict["path2"]
    project = signal_dict["project"]
    recalc = signal_dict["recalc"]
    y = signal_dict["y"]
    if recalc == "off":
        recalc_table = None
    else:
        recalc_table = signal_dict["recalc_table"]

    # Project configuration object
    config = Config(project)

    # Infer scenario name from path
    s1 = build_name(path)

    # User specified FCR?
    if recalc_table and "least cost" not in s1.lower():
        msgs = []
        for k, v in recalc_table["scenario_a"].items():
            if v:
                msgs.append(f"{k}: {v}")
        if msgs:
            reprint = ", ".join(msgs)
            s1 += f" ({reprint})"

    # Least Cost
    if "least cost" in s1.lower():
        s1 = infer_recalc(s1)

    # Append variable title
    title = s1 + "  |  " + config.titles[y]

    # Add variable aggregation value
    if y in AGGREGATIONS:
        ag_fun = AGGREGATIONS[y]
        if ag_fun == "mean":
            conditioner = "Average"
        else:
            conditioner = "Total"

        # Difference title
        if diff == "on":
            ag = "mean"
            s2 = os.path.basename(path2).replace("_sc.csv", "")
            s2 = " ".join([s.capitalize() for s in s2.split("_")])
            if recalc_table:
                msgs = []
                for k, v in recalc_table["scenario_b"].items():
                    if v:
                        msgs.append(f"{k}: {v}")
                if msgs:
                    reprint = ", ".join(msgs)
                    s2 += f" ({reprint})"

            title = "{} vs <br>{} <br>".format(s1, s2) + config.titles[y]
            conditioner = f"{units} Difference | Average"
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
                if ag_fun == "mean":
                    if weights == "on":
                        on = True
                    else:
                        on = False
                    ag = round(wmean(df, y, weight="n_gids", on=on), 2)
                    # ag = round(df[y].apply(ag_fun), 2)
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
              [Input("mapcap", "children"),
               Input("map", "selectedData")])
def calc_remaining_capacity(mapcap, mapsel):
    """Calculate total remaining capacity after all filters are applied."""
    # Calling this from make_map where the chartsel has already been applied
    # print_args(calc_remaining_capacity, mapcap, mapsel)
    if mapcap:
        df = pd.DataFrame(json.loads(mapcap))
        if mapsel:
            gids = [p["customdata"][0] for p in mapsel["points"]]
            df = df[df["sc_point_gid"].isin(gids)]
        total = round(df["print_capacity"].sum() / 1_000_000, 4)
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
def cache_map_data(signal_dict):
    """Read and store a data frame from the config and options given."""
    # Get signal elements
    diff = signal_dict["diff"]
    mask = signal_dict["mask"]
    path = signal_dict["path"]
    path2 = signal_dict["path2"]
    project = signal_dict["project"]
    recalc_table = signal_dict["recalc_table"]
    recalc = signal_dict["recalc"]
    states = signal_dict["states"]
    threshold = signal_dict["threshold"]
    units = signal_dict["units"]
    x = signal_dict["x"]
    y = signal_dict["y"]

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
               "latitude", "longitude", "sc_point_gid", "n_gids", "gid_counts",
               "index", "offshore"]
    if "offshore" not in df1.columns:
        keepers.remove("offshore")

    df1 = df1[keepers]

    # For other functions this data frame needs an x field
    if y == x:
        df1 = df1.iloc[:, 1:]

    # If there's a second table, read/cache the difference
    if path2:
        # Match the format of the first dataframe
        df2 = cache_table(project, path2, recalc_b, recalc)
        df2 = df2[keepers]
        if y == x:
            df2 = df2.iloc[:, 1:]

        # If the difference option is specified difference
        if diff == "on":
            calculator = Difference(units)
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
        if any([s in df["state"].values for s in states]):
            df = df[df["state"].isin(states)]

        if "offshore" in states:
            df = df[df["offshore"] == 1]
        if "onshore" in states:
            df = df[df["offshore"] == 0]

    return df


@cache3.memoize()
def cache_chart_tables(signal_dict, region="national", idx=None):
    """Read and store a data frame from the config and options given."""
    signal_copy = signal_dict.copy()

    # Unpack subsetting information
    states = signal_copy["states"]
    x = signal_copy["x"]
    y = signal_copy["y"]

    # If multiple tables selected, make a list of those files
    if signal_copy["added_scenarios"]:
        files = [signal_copy["path"]] + signal_copy["added_scenarios"]
    else:
        files = [signal_copy["path"]]

    # Remove additional scenarios from signal_dict for the cache's sake
    del signal_copy["added_scenarios"]

    # Make a signal copy for each file
    signal_dicts = []
    for file in files:
        signal = signal_copy.copy()
        signal["path"] = file
        signal_dicts.append(signal)

    # Get the requested data frames
    dfs = {}
    for signal in signal_dicts:
        name = build_name(signal["path"])
        df = cache_map_data(signal)
        if "offshore" in df.columns:
            df = df[[x, y, "state", "nrel_region", "print_capacity", "index",
                     "sc_point_gid", "gid_counts", "n_gids", "offshore"]]
        else:
            df = df[[x, y, "state", "nrel_region", "print_capacity", "index",
                     "sc_point_gid", "gid_counts", "n_gids"]]

        # Subset by index selection
        if idx:
            df = df.iloc[idx]

        # Subset by state selection
        if states:
            if any([s in df["state"] for s in states]):
                df = df[df["state"].isin(states)]

            if "offshore" in states:
                df = df[df["offshore"] == 1]
            if "onshore" in states:
                df = df[df["offshore"] == 0]

        # Divide into regions if one table (cancel otherwise for now)
        if region != "national" and len(signal_dicts) == 1:
            regions = df[region].unique()
            dfs = {r: df[df[region] == r] for r in regions}
        else:
            dfs[name] = df

    return dfs


@app.callback([Output("chart_options_tab", "children"),
               Output("chart_options_div", "style"),
               Output("chart_xvariable_options_div", "style"),
               Output("chart_region_div", "style"),
               Output("chart_scenarios_div", "style")],
              [Input("chart_options_tab", "value"),
               Input("chart_options", "value")])
def options_chart_tabs(tab_choice, chart_choice):
    """Choose which map tab dropown to display."""
    # print_args(chart_tab_options, tab_choice, chart_choice)
    styles = [{"display": "none"}] * 4
    order = ["chart", "xvariable", "region", "scenarios"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}

    # If Cumulative capacity only show the y variable
    if chart_choice in ["cumsum", "histogram", "box"]:
        children = [
            dcc.Tab(value="chart",
                    label="Chart Type",
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE),
            dcc.Tab(value="region",
                    label="Region",
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE),
            dcc.Tab(value="scenarios",
                    label="Additional Scenarios ",
                    style=TABLET_STYLE,
                    selected_style=TABLET_STYLE)
        ]
    else:
        children = [
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
        ]

    return children, styles[0], styles[1], styles[2], styles[3]


@app.callback([Output("low_cost_split_group_options", "options"),
               Output("low_cost_split_group_options", "value")],
              [Input("low_cost_split_group", "value"),
               Input("filedf", "children")])
def options_lchh_group(group, filedf):
    """Display the available options for a chosen group."""
    trig = dash.callback_context.triggered[0]['prop_id'].split(".")[0]
    if filedf and group in filedf:
        # print_args(options_lchh_group, group, filedf, trig=trig)
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
               Output("basemap_options_div", "style"),
               Output("color_options_div", "style")],
              [Input("map_options_tab", "value")])
def options_map_tab(tab_choice, ):
    """Choose which map tab dropdown to display."""
    # Styles
    styles = [{'display': 'none'}] * 3
    order = ["state", "basemap", "color"]
    idx = order.index(tab_choice)
    styles[idx] = {"width": "100%", "text-align": "center"}
    return styles[0], styles[1], styles[2]


@app.callback([Output("scenario_a", "options"),
               Output("scenario_b", "options"),
               Output("chart_scenarios", "options"),
               Output("low_cost_list", "options"),
               Output("scenario_a", "value"),
               Output("scenario_b", "value"),
               Output("low_cost_list", "value"),
               Output("variable", "options"),
               Output("chart_xvariable_options", "options"),
               Output("low_cost_split_group", "options"),
               Output("filedf", "children")],
              [Input("project", "value"),
               Input("catch_low_cost", "children")],
              [State("submit", "n_clicks")])
def options_options(project, lc_update, n_clicks):
    """Update the options given a project."""
    # Catch the trigger
    trig = dash.callback_context.triggered[0]['prop_id'].split(".")[0]
    print_args(options_options, project, lc_update, n_clicks, trig=trig)

    # Don't update if project hasn't changed and no submissions made
    if project == PROJECT and n_clicks is None:
        raise PreventUpdate

    # We need the project configuration
    config = Config(project)

    # Find the files
    DP = Data_Path(config.project_config["directory"])
    filedf = pd.DataFrame(config.project_config["data"])
    scenario_outputs = DP.contents("review_outputs", "least_cost*_sc.csv")
    scenario_originals = list(filedf["file"].values)
    files = scenario_originals + scenario_outputs
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
        if file in config.project_config["data"]["file"].values():
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

    return so, so, so, lco, sva, svb, sva, vo, vo, go, fdf


@app.callback([Output("project", "options"),
               Output("project", "value")],
              [Input("url", "pathname")],
              [State("submit", "n_clicks")])
def options_project(pathname, n_clicks):
    """Update project options. Triggered by navbar."""
    # Open config json
    print_args(options_project, pathname, n_clicks)
    fconfig = Config()
    options = []
    for project in fconfig.projects:
        pconfig = Config(project)
        if "parameters" in pconfig.project_config:
            options.append({"label": project, "value": project})
    if n_clicks == 0 or n_clicks is None:
        project = PROJECT
    else:
        project = options[0]["value"]
    return options, project


@app.callback(Output("recalc_a_options", "children"),
              [Input("project", "value"),
               Input("scenario_a", "value")],
              [State("recalc_table", "children")])
def options_recalc_a(project, scenario, recalc_table):
    """Update the drop down options for each scenario."""
    # print_args(options_recalc_a, project, scenario, recalc_table)
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
    # print_args(options_recalc_b, project, scenario, recalc_table)
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


@app.callback([Output("color_options", "options"),
               Output("color_options", "value")],
              [Input("submit", "n_clicks")],
              [State("variable", "value"),
               State("project", "value"),
               State("map_signal", "children"),
               State("color_options", "value")])
def options_toggle_color(submit, variable, project, signal, old_value):
    """Provide Qualitative color options for categorical data."""
    # print_args(options_toggle_color, variable, project, signal,
    #            old_value)

    # To figure out if we need to update we need these
    if not signal:
        raise PreventUpdate
    old_variable = json.loads(signal)["y"]
    config = Config(project)
    units = config.units[variable]
    old_units = config.units[old_variable]

    # There is only one condition where we have to do this
    if old_variable == variable:
        raise PreventUpdate
    if old_units == units:
        raise PreventUpdate
    if old_units != "category" and units != "category":
        raise PreventUpdate

    # Now return the appropriate options
    if units == "category":
        options = COLOR_Q_OPTIONS
        value = "T10"
    else:
        options = COLOR_OPTIONS
        value = "Viridis"

    return options, value


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
        button_style = BUTTON_STYLES["on"]

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


@app.callback(Output("chart_xbin_div", "style"),
              [Input("chart_options", "value")])
def options_toggle_bins(chart_type):
    """Show the bin size option under the chart."""
    # print_args(options_toggle_bins, chart_type)
    style = {"display": "none"}
    if chart_type == "binned":
        style = {"margin-left": "10px"}
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
               State("recalc_table", "children"),
               State("recalc_tab", "value")])
def retrieve_low_cost(submit, project, how, lst, group, group_choice, options,
                      by, recalc_table, recalc):
    """Calculate low cost fields based on user decision."""
    print_args(retrieve_low_cost, submit, project, how, lst, group,
                group_choice, options, by, recalc_table, recalc)

    if not submit:
        raise PreventUpdate

    config = Config(project)
    filedf = pd.DataFrame(config.project_config["data"])
    DP = Data_Path(config.directory)

    # Make a tag for all of our recalc values
    if recalc_table:
        recalc_table = json.loads(recalc_table)
    if recalc == "on":
        tags = []
        for k, v in recalc_table["scenario_a"].items():
            if v:
                tag = str(v).replace(".", "-") + k
                tags.append(tag)
        recalc_tag = "_".join(tags)
        recalc_tag = f"{recalc_tag}"

    # Build the appropriate paths and target file name
    if how == "all":
        # Just one output
        if recalc_table and recalc == "on":
            fname = f"least_cost_by_{by}__{recalc_tag}__all_sc.csv"
        else:
            fname = f"least_cost_by_{by}_all_sc.csv"
        paths = filedf["file"].values

    elif how == "list":
        # Just one output
        paths = lst
        scenarios = [os.path.basename(path).split("_")[1] for path in paths]
        scen_key = "_".join(scenarios)
        if recalc_table and recalc == "on":
            fname = f"least_cost_by_{by}_{scen_key}__{recalc_tag}__sc.csv"
        else:
            fname = f"least_cost_by_{by}_{scen_key}_sc.csv"

    else:
        # This could create multiple outputs, but we'll do one at a time
        grp_key = group_choice.replace(".", "")
        if recalc_table and recalc == "on":
            fname = (f"least_cost_by_{by}_{group}_{grp_key}__{recalc_tag}_"
                     "_sc.csv")
        else:
            fname = f"least_cost_by_{by}_{group}_{grp_key}_sc.csv"
        paths = filedf["file"][filedf[group] == group_choice].values

    # Build full paths and create the target file
    paths = [DP.join(path) for path in paths]
    lchh_path = DP.join("review_outputs", fname, mkdir=True)
    # print("calculating" + " " + lchh_path + "...")
    if recalc == "on":
        calculator = Least_Cost(project, recalc_table=recalc_table)
    else:
        calculator = Least_Cost(project)
    calculator.calc(paths, lchh_path, by=by)

    # Update the scenario file options
    label = " ".join([f.capitalize() for f in fname.split("_")[:-1]])
    option = {"label": label, "value": lchh_path}
    if label not in [o["label"] for o in options]:
        options.append(option)
    else:
        options.remove(option)
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
    # print("signal = " + signal)
    return signal


@app.callback(Output("map_signal", "children"),
              [Input("submit", "n_clicks"),
               Input("state_options", "value"),
               Input("chart_options", "value"),
               Input("chart_xvariable_options", "value"),
               Input("chart_scenarios", "value")],
              [State("project", "value"),
               State("upper_lcoe_threshold", "value"),
               State("threshold_field", "value"),
               State("scenario_a", "value"),
               State("scenario_b", "value"),
               State("lchh_path", "children"),
               State("variable", "value"),
               State("difference", "value"),
               State("low_cost_tabs", "value"),
               State("threshold_mask", "value"),
               State("recalc_table", "children"),
               State("recalc_tab", "value"),
               State("difference_units", "value")])
def retrieve_signal(submit, states, chart, x, scenarios, project, threshold,
                    threshold_field, path, path2, lchh_path, y, diff,
                    lchh_toggle, mask, recalc_table, recalc, diff_units):
    """Create signal for sharing data between map and chart with dependence."""
    trig = dash.callback_context.triggered[0]['prop_id']
    # print_args(retrieve_signal, submit, states, chart, x, scenarios, project,
    #            threshold, threshold_field, path, path2, lchh_path, y, diff,
    #            lchh_toggle, mask, recalc_table, recalc, diff_units,
    #            trig=trig)

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
    pdir = config.directory
    path = os.path.join(pdir, path)
    if path2:
        path2 = os.path.join(pdir, path2)
    if scenarios:
        scenarios = [os.path.join(pdir, s) for s in scenarios]

    # Create y mask and difference dependent variables
    ymin = scales[y]["min"]
    ymax = scales[y]["max"]
    units = config.units[y]
    if diff == "off" and mask == "mask_off":
        path2 = None
    elif diff == "on":
        ymin = -50
        ymax = 50

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

    # Return appropriate difference units
    if diff == "on":
        if diff_units == "original":
            units = config.units[y]
        else:
            units = "%"

    # Let's just recycle all this for the chart
    signal = {
        "diff": diff,
        "mask": mask,
        "path": path,
        "path2": path2,
        "project": project,
        "recalc": recalc,
        "recalc_table": recalc_table,
        "added_scenarios": scenarios,
        "states": states,
        "threshold": threshold,
        "units": units,
        "x": x,
        "y": y,
        "ymin": ymin,
        "ymax": ymax,
    }
    return json.dumps(signal)


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
            "scenario_a": {
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
    # Return a blank space if no parameters entry found
    params = Config(project).project_config["parameters"]
    if not params:
        specs1 = ""
        specs2 = ""
    else:
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
               Output("mapview_store", "children"),
               Output("mapcap", "children")],
              [Input("map_signal", "children"),
               Input("basemap_options", "value"),
               Input("color_options", "value"),
               Input("chart", "selectedData"),
               Input("map_point_size", "value"),
               Input("rev_color", "n_clicks"),
               Input("map_color_min", "value"),
               Input("map_color_max", "value")],
              [State("project", "value"),
               State("map", "selectedData"),
               State("map", "relayoutData"),
               State("weights", "value")])
def make_map(signal, basemap, color, chartsel, point_size, rev_color, uymin,
             uymax, project, mapsel, mapview, weights):
    """Make the scatterplot map.

    To fix the point selection issue check this out:
        https://community.plotly.com/t/clear-selecteddata-on-figurechange/37285
    """
    trig = dash.callback_context.triggered[0]['prop_id']
    print_args(make_map, signal, basemap, color, chartsel, point_size,
               rev_color, uymin, uymax, project, mapsel, mapview, weights,
               trig=trig)
    print("'MAP'; trig = '" + str(trig) + "'")

    # Get map elements from data signal
    signal_dict = json.loads(signal)
    df = cache_map_data(signal_dict)
    df.index = df["index"]
    units = signal_dict["units"]
    x = signal_dict["x"]
    y = signal_dict["y"]
    ymin = signal_dict["ymin"]
    ymax = signal_dict["ymax"]

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
    if chartsel and len(chartsel["points"]) > 0:
        df = point_filter(df, chartsel)

    # Store the capacity values up to this point
    mapcap = df[["sc_point_gid", "print_capacity"]].to_dict()

    # Convert weights to boolean
    if weights == "on":
        weights = True
    else:
        weights = False

    # Build map elements
    title = build_title(df, signal_dict, weights)
    figure = build_scatter(df, y, x, units, color, rev_color, ymin, ymax,
                           point_size, title, mapview, mapsel, basemap)

    return figure, json.dumps(mapview), json.dumps(mapcap)


@app.callback(Output('chart', 'figure'),
              [Input("map_signal", "children"),
               Input("chart_options", "value"),
               Input("map", "selectedData"),
               Input("chart_point_size", "value"),
               Input("chosen_map_options", "children"),
               Input("chart_region", "value"),
               Input("map_color_min", "value"),
               Input("map_color_max", "value"),
               Input("chart_xbin", "value")],
              [State("project", "value"),
               State("chart", "relayoutData"),
               State("chart", "selectedData"),
               State("weights", "value")])
def make_chart(signal, chart, mapsel, point_size, op_values, region, uymin,
               uymax, xbin, project, chartview, chartsel, weights):
    """Make one of a variety of charts."""
    trig = dash.callback_context.triggered[0]['prop_id']
    print_args(make_chart, signal, chart, mapsel, point_size, op_values,
               region, uymin, uymax, xbin, project, chartview, chartsel,
               weights, trig=trig)

    # Unpack the signal
    signal_dict = json.loads(signal)
    project = signal_dict["project"]
    units = signal_dict["units"]
    ymin = signal_dict["ymin"]
    ymax = signal_dict["ymax"]

    # Turn the map selection object into indices
    if mapsel:
        if len(mapsel["points"]) > 0:
            idx = [d["pointIndex"] for d in mapsel["points"]]
        else:
            idx = None
    else:
        idx = None

    # Get the data frames
    group = "Scenario"
    dfs = cache_chart_tables(signal_dict, region, idx)
    plotter = Plots(project, dfs, point_size, group=group, yunits=units,
                    xbin=xbin)

    if chart == "cumsum":
        fig = plotter.ccap()
    elif chart == "scatter":
        fig = plotter.scatter()
    elif chart == "binned":
        fig = plotter.binned()
    elif chart == "histogram":
        ylim = [0, 2000]
        fig = plotter.histogram()
    elif chart == "box":
        fig = plotter.box()

    # Build chart title
    title = build_title(dfs, signal_dict, weights)

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
        hovermode="closest",
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
