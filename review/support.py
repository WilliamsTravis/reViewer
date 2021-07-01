# -*- coding: utf-8 -*-
"""Support functions for the all reView projects.

Created on Sat Aug 15 15:47:40 2020

@author: travis
"""
import json
import os
import time

from collections import Counter

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import pathos.multiprocessing as mp
import plotly.colors as pcs
import plotly.express as px
import us

from colorama import Style, Fore
from review import Data_Path, print_args
from tqdm import tqdm

pd.set_option('mode.chained_assignment', None)


CONFIG_PATH = os.path.expanduser("~/.review_config")
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)
PROJECT = list(CONFIG.keys())[0]
AGGREGATIONS = {
    "area_sq_km": "sum",
    "capacity": "sum",
    "elevation": "mean",
    "dist_mi": "mean",
    "lcot": "mean",
    "mean_cf": "mean",
    "mean_lcoe": "mean",
    "mean_res": "mean",
    "total_lcoe": "mean",
    "trans_capacity": "sum",
    "trans_cap_cost": "mean",
    "trans_multiplier": "mean",
    "transmission_multiplier": "mean",
    "Hub Height": "mean",
    "capex": "mean",
    "shadow_flicker_120m": "sum",  # <----------------------------------------- Quick hack
    "shadow_flicker_120m_percent": "mean",
    "shadow_flicker_135m": "sum",
    "shadow_flicker_135m_percent": "mean"
}


BASEMAPS = [{"label": "Light", "value": "light"},
            {"label": "Dark", "value": "dark"},
            {"label": "Basic", "value": "basic"},
            {"label": "Outdoors", "value": "outdoors"},
            {"label": "Satellite", "value": "satellite"},
            {"label": "Satellite Streets", "value": "satellite-streets"}]

# Move to CSS
BUTTON_STYLES = {
    "on": {
        "height": "45px",
        "width": "200px",
        "padding": "4px",
        "background-color": "#FCCD34",
        "border-radius": "4px",
        "border-color": "#1663b5",
        "font-family": "Times New Roman",
        "font-size": "12px",
        "margin-top": "-2px"
        },
    "off": {
        "height": "45px",
        "width": "200px",
        "padding": "4px",
        "border-color": "#1663b5",
        "background-color": "#b89627",
        "border-radius": "4px",
        "font-family": "Times New Roman",
        "font-size": "12px",
        "margin-top": "-2px"
        }
    }

BOTTOM_DIV_STYLE = {
    "height": "45px",
    "float": "left",
    "margin-top": "-2px",
    "margin-left": -1,
    "border": "3px solid #1663b5",
    "border-radius": "4px",
    "border-width": "3px",
    "border-top-width": "0px",
    "border-radius-top-left": "0px",
    "border-radius-top-right": "0px"
}


CHART_OPTIONS = [{"label": "Cumulative Capacity", "value": "cumsum"},
                 {"label": "Bivariate - Scatterplot", "value": "scatter"},
                 {"label": "Bivariate - Binned Line Plot", "value": "binned"},
                 {"label": "Histogram", "value": "histogram"},
                 {"label": "Boxplot", "value": "box"}]

CUSTOM_COLORS = {
    "RdWhBu": [[0.00, "rgb(115,0,0)"],
               [0.10, "rgb(230,0,0)"],
               [0.20, "rgb(255,170,0)"],
               [0.30, "rgb(252,211,127)"],
               [0.40, "rgb(255, 255, 0)"],
               [0.45, "rgb(255, 255, 255)"],
               [0.55, "rgb(255, 255, 255)"],
               [0.60, "rgb(143, 238, 252)"],
               [0.70, "rgb(12,164,235)"],
               [0.80, "rgb(0,125,255)"],
               [0.90, "rgb(10,55,166)"],
               [1.00, "rgb(5,16,110)"]],
    "RdWhBu (Extreme Scale)": [[0.00, "rgb(115,0,0)"],
                               [0.02, "rgb(230,0,0)"],
                               [0.05, "rgb(255,170,0)"],
                               [0.10, "rgb(252,211,127)"],
                               [0.20, "rgb(255, 255, 0)"],
                               [0.30, "rgb(255, 255, 255)"],
                               [0.70, "rgb(255, 255, 255)"],
                               [0.80, "rgb(143, 238, 252)"],
                               [0.90, "rgb(12,164,235)"],
                               [0.95, "rgb(0,125,255)"],
                               [0.98, "rgb(10,55,166)"],
                               [1.00, "rgb(5,16,110)"]],
    "RdYlGnBu": [[0.00, "rgb(124, 36, 36)"],
                 [0.25, "rgb(255, 255, 48)"],
                 [0.5, "rgb(76, 145, 33)"],
                 [0.85, "rgb(0, 92, 221)"],
                 [1.00, "rgb(0, 46, 110)"]],
    "BrGn (cb)": [[0.00, "rgb(91, 74, 35)"],
                  [0.10, "rgb(122, 99, 47)"],
                  [0.15, "rgb(155, 129, 69)"],
                  [0.25, "rgb(178, 150, 87)"],
                  [0.30, "rgb(223,193,124)"],
                  [0.40, "rgb(237, 208, 142)"],
                  [0.45, "rgb(245,245,245)"],
                  [0.55, "rgb(245,245,245)"],
                  [0.60, "rgb(198,234,229)"],
                  [0.70, "rgb(127,204,192)"],
                  [0.75, "rgb(62, 165, 157)"],
                  [0.85, "rgb(52,150,142)"],
                  [0.90, "rgb(1,102,94)"],
                  [1.00, "rgb(0, 73, 68)"]],
    "YlGnBu (cb)": [[0.0, "rgb(255,255,217)"],
                    [0.125, "rgb(237,248,177)"],
                    [0.25, "rgb(199,233,180)"],
                    [0.375, "rgb(127,205,187)"],
                    [0.5, "rgb(65,182,196)"],
                    [0.625, "rgb(29,145,192)"],
                    [0.75, "rgb(34,94,168)"],
                    [0.875, "rgb(37,52,148)"],
                    [1.0, "rgb(8,29,88)"]],
    "YlOrBr (cb)": [[0.0, "rgb(255,255,229)"],
                    [0.125, "rgb(255,247,188)"],
                    [0.25, "rgb(254,227,145)"],
                    [0.375, "rgb(254,196,79)"],
                    [0.5, "rgb(254,153,41)"],
                    [0.625, "rgb(236,112,20)"],
                    [0.75, "rgb(204,76,2)"],
                    [0.875, "rgb(153,52,4)"],
                    [1.0, "rgb(102,37,6)"]],
    "YlGn (cb)": [[0.0, "rgb(255,255,229)"],
                  [0.125, "rgb(247,252,185)"],
                  [0.25, "rgb(217,240,163)"],
                  [0.375, "rgb(173,221,142)"],
                  [0.5, "rgb(120,198,121)"],
                  [0.625, "rgb(65,171,93)"],
                  [0.75, "rgb(35,132,67)"],
                  [0.875, "rgb(0,104,55)"],
                  [1.0, "rgb(0,69,41)"]]
}
COLORS = {**pcs.PLOTLY_SCALES, **CUSTOM_COLORS}
COLOR_OPTIONS = [{"label": k, "value": k} for k, _ in COLORS.items()]
COLORS_Q = {k: v for k, v in pcs.qualitative.__dict__.items() if "_" not in k}
COLORS_Q = {k: v for k, v in COLORS_Q.items() if k!= "swatches"}
COLOR_Q_OPTIONS = [{"label": k, "value": k} for k, _ in COLORS_Q.items()] 
DEFAULT_MAPVIEW = {
    "mapbox.center": {
        "lon": -96.50,
        "lat": 37.5
    },
    "mapbox.zoom": 3.5,
    "mapbox.bearing": 0,
    "mapbox.pitch": 0
}

LCOEOPTIONS = [{"label": "Site-Based", "value": "mean_lcoe"},
               {"label": "Transmission", "value": "lcot"},
               {"label": "Total", "value": "total_lcoe"}]

MAP_LAYOUT = dict(
    dragmode="select",
    font_family="Time New Roman",
    font_size=15,
    height=700,
    hovermode="closest",
    legend=dict(size=20),
    margin=dict(l=20, r=115, t=115, b=20),
    paper_bgcolor="#1663B5",
    plot_bgcolor="#083C04",
    titlefont=dict(color="white", size=18, family="Time New Roman"),
    title=dict(
        # color="white",
        # size=18,
        # font_family="Times New Roman",
        yref="container",
        x=0.05,
        y=0.95,
        yanchor="top",
        pad=dict(b=10)
    ),
    mapbox=dict(
        accesstoken=("pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNkMnpt"
                     "aWlwcHZvdzdoIn0.9pxpgXxyyhM6qEF_dcyjIQ"),
        style="satellite-streets",
        center=dict(lon=-100.75, lat=39.5),
        zoom=5)
)

ORIGINAL_FIELDS = ["sc_gid", "res_gids", "gen_gids", "gid_counts", "n_gids",
                   "mean_cf", "mean_lcoe", "mean_res", "capacity",
                   "area_sq_km", "latitude", "longitude", "country", "state",
                   "county", "elevation", "timezone", "sc_point_gid",
                   "sc_row_ind", "sc_col_ind", "res_class", "trans_multiplier",
                   "trans_gid", "trans_capacity", "trans_type",
                   "trans_cap_cost", "dist_mi", "lcot", "total_lcoe",
                   "windspeed_class"]

REGIONS = {
    "Pacific": [
        "Oregon",
        "Washington"
    ],
    "Mountain": [
        "Colorado",
        "Idaho",
        "Montana",
        "Wyoming"
    ],
    "Great Plains": [
        "Iowa",
        "Kansas",
        "Missouri",
        "Minnesota",
        "Nebraska",
        "North Dakota",
        "South Dakota"
    ],
    "Great Lakes": [
        "Illinois",
        "Indiana",
        "Michigan",
        "Ohio",
        "Wisconsin"
    ],
    "Northeast": [
        "Connecticut",
        "New Jersey",
        "New York",
        "Maine",
        "New Hampshire",
        "Massachusetts",
        "Pennsylvania",
        "Rhode Island",
        "Vermont"
    ],
    "California": [
        "California"
    ],
    "Southwest": [
        "Arizona",
        "Nevada",
        "New Mexico",
        "Utah"
    ],
    "South Central": [
        "Arkansas",
        "Louisiana",
        "Oklahoma",
        "Texas"
    ],
    "Southeast": [
        "Alabama",
        "Delaware",
        "District of Columbia",
        "Florida",
        "Georgia",
        "Kentucky",
        "Maryland",
        "Mississippi",
        "North Carolina",
        "South Carolina",
        "Tennessee",
        "Virginia",
        "West Virginia"
    ]
}

RESOURCE_CLASSES = {
    "windspeed": {
        "onshore": {
            1: [9.01, 100],
            2: [8.77, 9.01],
            3: [8.57, 8.77],
            4: [8.35, 8.57],
            5: [8.07, 8.35],
            6: [7.62, 8.07],
            7: [7.10, 7.62],
            8: [6.53, 7.10],
            9: [5.90, 6.53],
            10: [0, 5.90],
        },
        "offshore": {
            "fixed": {
                1: [9.98, 100],
                2: [9.31, 9.98],
                3: [9.13, 9.31],
                4: [8.85, 9.13],
                5: [7.94, 8.85],
                6: [7.07, 7.94],
                7: [0, 7.07]
            },
            "floating": {
                1: [10.30, 1000],
                2: [10.01, 10.30],
                3: [9.60, 10.01],
                4: [8.84, 9.60],
                5: [7.43, 8.84],
                6: [5.98, 7.43],
                7: [0, 5.98]
            }
        }
    }
}

SCALE_OVERRIDES = {
    "total_lcoe": [0, 200],
    "mean_lcoe": [0, 200]
}

STATES = [{"label": s.name, "value": s.name} for s in us.STATES]
STATES.append({"label": "Onshore", "value": "onshore"})
STATES.append({"label": "Offshore", "value": "offshore"})

STYLESHEET = "https://codepen.io/chriddyp/pen/bWLwgP.css"

TAB_STYLE = {"height": "25px", "padding": "0"}

TABLET_STYLE = {"line-height": "25px", "padding": "0"}

TITLES = {
    "area_sq_km": "Supply Curve Point Area",
    "capacity": "Total Capacity",
    "elevation": "Elevation",
    "dist_mi": "Distance to Transmission",
    "lcot": "LCOT",
    "mean_cf": "Mean Capacity Factor",
    "mean_lcoe": "Mean Site-Based LCOE",
    "mean_res": "Mean Windspeed",
    "total_lcoe": "Total LCOE",
    "trans_capacity": "Total Transmission Capacity",
    "trans_cap_cost": "Transmission Capital Costs",
    "transmission_multiplier": "Transmission Cost Multiplier",
    "trans_multiplier": "Transmission Cost Multiplier",
    "trans_type": "Transmission Feature Type",
    "windspeed_class": "Windspeed Class"
}


UNITS = {
    "area_sq_km": "square km",
    "elevation": "m",  # Double check this
    "capacity": "MW",
    "dist_mi": "miles",
    "lcot": "$/MWh",
    "mean_cf": "ratio",
    "mean_lcoe": "$/MWh",
    "mean_res": "m/s",  # This will change based on resource
    "total_lcoe": "$/MWh",
    "trans_capacity": "MW",
    "trans_cap_cost": "$/MW",
    "transmission_multiplier": "category",
    "trans_multiplier": "category",
    "trans_type": "category",
    "windspeed_class": "category"
}

VARIABLES = [
    {"label": "Distance to Transmission", "value": "dist_mi"},
    {"label": "Elevation", "value": "elevation"},
    {"label": "LCOT", "value": "lcot"},
    {"label": "Mean Capacity Factor", "value": "mean_cf"},
    {"label": "Mean Site-Based LCOE", "value": "mean_lcoe"},
    {"label": "Mean Windspeed", "value": "mean_res"},
    {"label": "Supply Curve Point Area", "value": "area_sq_km"},
    {"label": "Total Generation Capacity", "value": "capacity"},
    {"label": "Total LCOE", "value": "total_lcoe"},
    {"label": "Total Transmission Capacity", "value": "trans_capacity"},
    {"label": 'Transmission Capital Costs', "value": 'trans_cap_cost'},
    {"label": "Transmission Cost Multiplier", "value": "trans_multiplier"},
    {"label": "Tranmission Feature Type", "value": "trans_type"},
    {"label": "Windspeed Class", "value": "windspeed_class"}
]


def config_div(config_path):
    """Build the project html div using the review configuration json."""
    with open(config_path, "r") as file:
        config = json.load(file)

    keys = list(config.keys())
    options = []
    for key in keys:
        option = {"label": key, "value": key}
        options.append(option)

    div = html.Div([
        html.H3("Project"),
        dcc.Dropdown(
            id="project",
            options=options,
            value=keys[1]
            )
        ], className="three columns"
    )

    return div


def point_filter(df, selection):
    """Filter a dataframe by points selected from the chart."""
    if selection:
        points = selection["points"]
        gids = [p["customdata"][0] for p in points]
        df = df[df["sc_point_gid"].isin(gids)]
    return df


def find_scenario(path):
    """Find a scenario in the config from its path."""
    # Infer scenario
    scenario = os.path.basename(path).replace("_sc.csv", "")

    # Find its scenario
    for project in Config().projects:
        config = Config(project).project_config
        if "parameters" in config:
            params = config["parameters"]
            if scenario in params:
                break
    return project, scenario


def get_dataframe_path(project, op_values):
    """Get the table for a set of options."""
    # print_args(get_dataframe_path, project, op_values)
    with open(CONFIG_PATH) as cfile:
        config = json.load(cfile)

    # There will be Nones
    if op_values:
        # Extract the project config and its data frame
        project_config = config[project]
        data = pd.DataFrame(project_config["data"])

        # Find the matching path
        for col, option in op_values.items():
            if option not in data[col].values:
                print(option + " not in data.")
            else:
                data = data[data[col] == option]

        try:
            assert data.shape[0] == 1
            path = data["file"].values[0]
        except Exception:
            raise AssertionError(
                Fore.RED
                + "The options did not result in a single selection:"
                + "\n"
                + Style.RESET_ALL
            )
        return path


def get_scales(file_df, field_units):
    """Create a value scale dictionary for each field-unit pair."""
    def get_range(args):
        file, fields = args
        ranges = {}
        df = pd.read_csv(file, low_memory=False)
        for field in fields:
            ranges[field] = {}
            if field in df.columns:
                try:
                    values = df[field].dropna()
                    values = values[values != -np.inf]
                    ranges[field]["min"] = values.min()
                    ranges[field]["max"] = values.max()
                except KeyError:
                    print("KeyError")
                    del ranges[field]
            else:
                ranges[field]["min"] = 0
                ranges[field]["max"] = 9999
        return ranges

    # Get all the files
    files = file_df["file"].values
    numbers = [k for k, v in field_units.items() if v != "category"]
    categories = [k for k, v in field_units.items() if v == "category"]

    # Setup numeric scale runs
    arg_list = [[file, numbers] for file in files]
    ranges = []
    with mp.Pool(mp.cpu_count()) as pool:
        for rng in tqdm(pool.imap(get_range, arg_list), total=len(arg_list)):
            ranges.append(rng)

    # Adjust
    rdf = pd.DataFrame(ranges).T
    mins = rdf.apply(lambda x: min([e["min"] for e in x]), axis=1)
    maxes = rdf.apply(lambda x: max([e["max"] for e in x]), axis=1)

    scales = {}
    for field in rdf.index:
        scales[field] = {}
        vmin = mins[field]
        vmax = maxes[field]
        if isinstance(vmin, np.int64):
            vmin = int(vmin)
            vmax = int(vmax)
        scales[field]["min"] = vmin
        scales[field]["max"] = vmax

    # Add in qualifier for categorical fields
    for field in categories:
        scales[field] = {"min": "na", "max": "na"}

    return scales


def is_number(x):
    """Check if a string is a number."""
    try:
        int(x)
        check = True
    except ValueError:
        check = False
    return check


def map_range(x, range_dict):
    """Assign a key to x given a list of key, value ranges."""
    keys = []
    for key, values in range_dict.items():
        if x >= values[0] and x < values[1]:
            keys.append(key)
    key = keys[0]
    return key


def reshape_regions():
    """Reshape region dictionary."""
    regions = {}
    for region, states in REGIONS.items():
        for state in states:
            regions[state] = region
    return regions


def sort_mixed(values):
    """Sort a list of values accounting for possible mixed types."""
    numbers = []
    strings = []
    for v in values:
        if is_number(v):
            numbers.append(float(v))
        else:
            strings.append(v)
    numbers.sort(key=float)
    strings.sort()
    sorted_values = numbers + strings
    return sorted_values


def wmean(df, y, weight="n_gids", on=True):  # <------------------------------------ How to incorporate partial inclusions?
    """Return the weighted average of a column.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        A reV supply-curve module output table.
    y : str
        Column name of the variable to calculate.
    weight : str
        Column name of the variable to use as the weights. The default is
        'n_gids'.
    on : bool
        Wether or not to apply weights.

    Returns
    -------
    int | float
        Weighted mean of input field.
    """
    values = df[y].values
    if on:
        weights = df[weight].values

        # weights might all be nans or 0s
        if np.nansum(weights) == 0:
            x = np.nanmean(values)
        else:
            # Ignore nan values
            values = values[~np.isnan(weights)]
            weights = weights[~np.isnan(weights)]

            weights = weights[~np.isnan(values)]
            values = values[~np.isnan(values)]

            # Calculate
            x = np.average(values, weights=weights)
    else:
        x = np.nanmean(values)

    return x


class Categories:

    def __init__(self):
        """Initialize Scatter object."""

    def mode(self, df, y):
        """Return the mode for a json dictionary with categorical counts."""
        values = df[y].apply(lambda d: self._mode(d))
        return values

    def counts(self, df, y):
        """Return counts for each category from all rows."""  # <-------------- Need to account for partial exclusions translate to area
        dicts = df[y].apply(json.loads)
        counters = [Counter(d) for d in dicts]
        c1 = counters[0]
        for c in counters[1:]:
            c1.update(c)
        counts = dict(c1)
        return counts

    def _mode(self, d):
        """Return the most common key in a dictionary with counts."""
        d = json.loads(d)
        return max(d, key=d.get)


class Config:
    """Class for handling configuration variables."""

    def __init__(self, project=None, config_path="~/.review_config"):
        """Initialize plotting object for a reV project."""
        self.project = project
        self.config_path = os.path.expanduser(config_path)
        self.title_size = 20

    def __repr__(self):
        """Print the project and config path."""
        path = self.config_path
        project = self.project
        if project:
            files = len(self.project_config["data"]["file"])
        else:
            files = 0
        msg = (f"<reView Config object: path='{path}', project='{project}', "
               f"{files} files>")
        return msg

    def map_title(self, variable, op_values):
        """Make a title for the map given a variable name and option values."""
        if self.project:
            var_title = self.titles[variable]
            for op, val in op_values.items():
                if op in self.project_config["units"]:
                    units = self.project_config["units"][op]
                else:
                    units = ""
                op_title = str(val) + units + " " + op
                var_title = var_title + " - " + op_title
            if len(var_title.split(" - ")) > 3:
                self.title_size = 12
            elif len(var_title.split(" - ")) > 5:
                self.title_size = 10
            elif len(var_title.split(" - ")) > 7:
                self.title_size = 8
            return var_title

    def chart_title(self, var_title, op_values, group):
        """Make a title for the chart with variable/group name and options."""
        if self.project:
            if group in op_values:
                del op_values[group]
            for op, val in op_values.items():
                units = self.project_config["units"][op]
                op_title = str(val) + units + " " + op
                var_title = var_title + " - " + op_title
            var_title = var_title + ", All " + group + "s"
            if len(var_title.split(" - ")) > 3:
                self.title_size = 12
            elif len(var_title.split(" - ")) > 5:
                self.title_size = 10
            elif len(var_title.split(" - ")) > 7:
                self.title_size = 8
            return var_title

    @property
    def config(self):
        """Return the full config dictionary."""
        with open(self.config_path, "r") as file:
            config = json.load(file)
        return config

    @property
    def data(self):
        """Return a pandas data frame with fuill file paths."""
        if self.project:
            data = pd.DataFrame(self.project_config["data"])
            return data

    @property
    def directory(self):
        """Return the project directory."""
        if self.project:
            return self.project_config["directory"]

    @property
    def files(self):
        """Return a dictionary of scenario with full paths to files."""
        files = {}
        for file in self.data["file"]:
            scenario = file.replace("_sc.csv", "")
            files[scenario] = os.path.join(self.directory, file)
        return files

    @property
    def options(self):
        """Not all options will be available for every grouping variable."""
        if self.project:
            options = {}
            data = pd.DataFrame(self.project_config["data"])
            del data["file"]
            for col in data.columns:
                options[col] = list(data[col].unique())
            return options

    @property
    def projects(self):
        """Return a list of available projects."""
        return list(self.config.keys())

    @property
    def project_config(self):
        """Return the project config dictionary."""
        if self.project:
            return self.config[self.project]

    @property
    def scales(self):
        """Return a titles dictionary with extra fields."""
        if self.project:
            scales = self.project_config["scales"]
            for override, scale in SCALE_OVERRIDES.items():
                scales[override]["min"] = scale[0]
                scales[override]["max"] = scale[1]
            return scales

    @property
    def scenarios(self):
        """Return just a list of scenario names."""
        scenarios = []
        for file in self.data["file"]:
            scenarios.append(file.replace("_sc.csv", ""))
        return scenarios

    @property
    def titles(self):
        """Return a titles dictionary with extra fields."""
        if self.project:
            titles = self.project_config["titles"]
            return titles

    @property
    def units(self):
        """Return a units dictionary with extra fields."""
        if self.project:
            units = self.project_config["units"]

            # In case we update the standard set
            addons = {k: u for k, u in UNITS.items() if k not in units}
            units = {**units, **addons}
            return units


class Data(Config):
    """Class to handle data access and recalculations."""

    def __init__(self, project, config_path="~/.review_config"):
        """Initialize Data object."""
        super().__init__(project)

    def __repr__(self):
        """Build representation string."""
        path = self.config_path
        project = self.project
        files = len(self.project_config["data"]["file"])
        msg = (f"<reView Data object: path='{path}', project='{project}', "
               f"{files} files>")
        return msg

    def build(self, scenario, fcr=None, capex=None, opex=None, losses=None):
        """Read in a data table given a scenario with recalc.

        Parameters
        ----------
        scenario : str
            The scenario key or data path for the desired data table.
        fcr : str | numeric
            Fixed charge as a percentage.
        capex : str | numeric
            Capital expenditure in USD / KW
        opex : str | numeric
            Fixed operating costs in USD / KW
        losses : str | numeric
            Generation losses as a percentage.

        Returns
        -------
        pd.core.frame.DataFrame
            A supply-curve data frame with either the original values or
            recalculated values if new parameters are given.
        """
        # This can be a path or a scenario
        if ".csv" in scenario:
            if "_agg" in scenario:
                scenario = os.path.basename(scenario).replace("_agg.csv", "")
            else:
                scenario = os.path.basename(scenario).replace("_sc.csv", "")

        # Recalculate if needed, else return original table
        recalcs = dict(fcr=fcr, capex=capex, opex=opex, losses=losses)
        if any(recalcs.values()):
            df = self.recalc(scenario, recalcs)
        else:
            df = self.read(scenario)

        return df

    def lcoe(self, capacity, mean_cf, recalcs, ovalues):
        """Recalculate LCOE.

        Parameters
        ----------
        capacity : pd.core.series.Series | np.ndarray
            A series of capacity values.
        mean_cf : pd.core.series.Series | np.ndarray
            A series of capacity factor values.
        recalcs : dict
            A dictionary with new entries for capex, opex, and fcr.
        ovalues : dict
            A dicitonary with the original values for capex, opex, and fcr.

        Returns
        -------
        np.ndarray
            A series of LCOE values.
        """
        capacity_kw = capacity * 1000
        cc = recalcs["capex"] * capacity_kw
        om = recalcs["opex"] * capacity_kw
        fcr = recalcs["fcr"]
        lcoe = ((fcr * cc) + om) / (capacity * mean_cf * 8760)
        return lcoe

    def lcot(self, capacity, trans_cap_cost, mean_cf, recalcs, ovalues):
        """Recalculate LCOT.

        Parameters
        ----------
        capacity : pd.core.series.Series | np.ndarray
            A series of capacity values.
        trans_cap_cost : pd.core.series.Series | np.ndarray
            A series of transmission capital cost values.
        mean_cf : pd.core.series.Series | np.ndarray
            A series of capacity factor values.
        recalcs : dict
            A dictionary with new entries for capex, opex, and fcr.
        ovalues : dict
            A dicitonary with the original values for capex, opex, and fcr.

        Returns
        -------
        np.ndarray
            A series of LCOT values.
        """
        fcr = recalcs["fcr"]
        cc = trans_cap_cost * capacity
        lcot = (cc * fcr) / (capacity * mean_cf * 8760)
        return lcot

    def original_parameters(self, scenario):
        """Return the original parameters for fcr, capex, opex, and losses."""
        fields = self._find_fields(scenario)
        config = self.project_config
        params = config["parameters"][scenario]
        ovalues = dict()
        for key in ["fcr", "capex", "opex", "losses"]:
            ovalues[key] = self._fix_format(params[fields[
                key]])
        return ovalues

    def read(self, path):
        """Read in the needed columns of a supply-curve csv.

        Parameters
        ----------
        scenario : str
            The scenario key for the desired data table.

        Returns
        -------
        pd.core.frame.DataFrame
            A supply-curve table with original vlaues.
        """
        # Find the path and columns associated with this scenario
        try:
            if not os.path.isfile(path):
                path = self.files[path]
        except Exception:
            print("Problem of some sort found~!")
        fields = list(self.units.keys())
        ids = ["sc_gid", "sc_point_gid", "res_gids", "gid_counts", "n_gids",
               "state", "nrel_region", "county", "offshore", "latitude",
               "longitude"]
        columns = ids + fields

        # We might need to add fields before we can these in
        df_columns = pd.read_csv(path, index_col=0, nrows=0).columns
        df_columns = df_columns.tolist()
        # if not all([c in df_columns for c in columns]):
        #     self._set_fields(path)

        # There is a discrepancy in transmission multiplier's naming
        if "transmission_multiplier" in df_columns:
            columns.remove("trans_multiplier")
        else:
            columns.remove("transmission_multiplier")
        if "scenario" in df_columns:
            columns += ["scenario"]

        # Read in table
        columns = [c for c in columns if c in self._cols(path)]
        df = pd.read_csv(path, usecols=columns, low_memory=False)

        return df

    def recalc(self, scenario, recalcs):
        """Recalculate LCOE for a data frame given a specific FCR.

        Parameters
        ----------
        scenario : str
            The scenario key for the desired data table.
        recalcs : dict
            A dictionary of parameter-value pairs needed to recalculate
            variables.

        Returns
        -------
        pd.core.frame.DataFrame
            A supply-curve module data frame with recalculated values.
        """
        # Read in data
        df = self.read(scenario)

        # If any of these aren't specified, use the original values
        ovalues = self.original_parameters(scenario)
        for key, value in recalcs.items():
            if not value:
                recalcs[key] = ovalues[key]
            else:
                recalcs[key] = self._fix_format(recalcs[key])

        # Get the right units for percentages
        ovalues["fcr"] = self._check_percentage(ovalues["fcr"])
        recalcs["fcr"] = self._check_percentage(recalcs["fcr"])
        ovalues["losses"] = self._check_percentage(ovalues["losses"])
        recalcs["losses"] = self._check_percentage(recalcs["losses"])

        # Extract needed variables as vectors
        capacity = df["capacity"].values
        mean_cf = df["mean_cf"].values
        mean_lcoe = df["mean_lcoe"].values
        trans_cap_cost = df["trans_cap_cost"].values

        # Adjust capacity factor for LCOE
        mean_cf_adj = self._get_cf(mean_cf, capacity, mean_lcoe, recalcs,
                                   ovalues, adjust=True)
        mean_cf = self._get_cf(mean_cf, capacity, mean_lcoe, recalcs, ovalues,
                               adjust=False)

        # Recalculate figures
        df["mean_cf"] = mean_cf  # What else will this affect?
        df["mean_lcoe"] = self.lcoe(capacity, mean_cf_adj, recalcs, ovalues)
        df["lcot"] = self.lcot(capacity, trans_cap_cost, mean_cf, recalcs,
                               ovalues)
        df["total_lcoe"] = df["mean_lcoe"] + df["lcot"]

        return df

    def _check_percentage(self, value):
        """Check if a value is a decimal or percentage (Assuming here)."""
        if value > 1:
            value = value / 100
        return value

    def _find_fields(self, scenario):
        """Find input fields with pattern recognition."""
        config = self.project_config
        params = config["parameters"][scenario]
        patterns = {k.lower().replace(" ", ""): k for k in params.keys()}
        matches = {}
        for key in ["capex", "opex", "fcr", "losses"]:
            match = [v for k, v in patterns.items() if key in str(k)][0]
            matches[key] = match
        return matches

    def _fix_format(self, value):
        """Remove commas and dollar signs from value, return as float."""
        if isinstance(value, str):
            value = value.replace(",", "").replace("$", "").replace("%", "")
            value = float(value)
        return value

    def _get_cf(self, mean_cf, capacity, mean_lcoe, recalcs, ovalues, adjust):
        """Return a properly rounded capacity factor from a table row."""
        # Back out cf from lcoe to fix rounding error, if needed
        if adjust:
            capacity_kw = capacity * 1000
            cc = ovalues["capex"] * capacity_kw
            om = ovalues["opex"] * capacity_kw
            fcr = ovalues["fcr"]
            mean_cf = ((fcr * cc) + om) / (mean_lcoe * capacity * 8760)

        # Recalculate losses, if needed
        if recalcs["losses"] != ovalues["losses"]:
            l1 = ovalues["losses"]
            l2 = recalcs["losses"]
            gross_cf = mean_cf / (1 - l1)
            mean_cf = gross_cf - (gross_cf * l2)

        return mean_cf

    def _set_field(self, path, field):
        """Assign a particular resource class to an sc df."""
        df = pd.read_csv(path, low_memory=False)
        col = f"{field}_class"
        if field == "windspeed":  # <------------------------------------------ How can we distinguish solar from wind?
            if "mean_ws_mean-means" in df.columns:
                dfield = "mean_ws_mean-means"
            else:
                dfield = "mean_res"
        else:
            dfield = field
        if col not in df.columns:
            print("Updating fields for " + path + "...")
            onmap = RESOURCE_CLASSES[field]["onshore"]
            offmap = RESOURCE_CLASSES[field]["offshore"]
            if dfield in df.columns:
                if "offshore" in df.columns and dfield == "windspeed":
                    # onshore
                    ondf = df[df["offshore"] == 0]
                    clss = df[dfield].apply(map_range, range_dict=onmap)
                    ondf[col] = clss

                    # offshore
                    offdf = df[df["offshore"] == 1]

                    # Fixed
                    fimap = offmap["fixed"]
                    fidf = offdf[offdf["sub_type"] == "fixed"]
                    clss = fidf[dfield].apply(map_range, range_dict=fimap)

                    # Floating
                    flmap = offmap["floating"]
                    fldf = offdf[offdf["sub_type"] == "floating"]
                    clss = fldf[dfield].apply(map_range, range_dict=flmap)
                    fldf[col] = clss

                    # Recombine
                    offdf = pd.concat([fidf, fldf])
                    df = pd.concat([ondf, offdf])
                else:
                    clss = df[dfield].apply(map_range, range_dict=onmap)
                    df[col] = clss
            df.to_csv(path, index=False)
        return df

    def _set_fields(self, path):
        """Assign resource classes if possible to an sc df."""
        for field in RESOURCE_CLASSES.keys():
            self._set_field(path, field)

    def _cols(self, file):
        """Return only the columns of a csv file."""
        return pd.read_csv(file, index_col=0, nrows=0).columns


class Difference:
    """Class to handle supply curve difference calculations."""

    def __init__(self, units):
        """Initialize Difference object."""
        self.units = units

    def diff(self, x):
        """Return the percent difference between two values."""
        if x.shape[0] == 1:
            return np.nan
        else:
            diff = x.iloc[0] - x.iloc[1]
            if self.units == "%":
                diff = 100 * (diff / x.iloc[1])
            return diff

    def calc(self, df1, df2, field):
        """Calculate difference between each row in two data frames."""
        print("Calculating difference...")
        group = "sc_point_gid"
        df = pd.concat([df1, df2])
        pcts = df.groupby(group)[field].apply(self.diff)
        ndf = df1.copy()
        ndf.index = df1["sc_point_gid"]
        del ndf[field]
        ndf = ndf.merge(pcts.to_frame(), left_index=True, right_index=True)
        print("Difference calculated.")
        return ndf


class LCOE(Config):  # <------------------------------------------------------- This will only work for the Transition/ATB projects, the parameter names are standardized yet
    """Class to recalculate LCOE with different parameters."""

    def __init__(self, project):  # <------------------------------------------ Move losses functions to CF object and inherit both Config and CF classes
        super().__init__(project)

    def __repr__(self):
        msg = f"<LCOE object: path={self.config_path}, project={self.project}>"
        return msg

    def lcoe(self, row, nvalues, ovalues):
        """Calculate LCOE for a single row.

        Parameters
        ----------
        row: pd.core.series.Series
            A row in a pandas data frame.
        nvalues: dict
            A dictionary with new entries for capex, opex, and fcr.
        ovalues: dict
            A dicitonary with the original entries for capex, opex, and fcr.
        """
        capacity = row["capacity"] * 1000
        cc = nvalues["capex"] * capacity
        om = nvalues["opex"] * capacity
        fcr = nvalues["fcr"]
        cf = self._get_cf(row, ovalues)
        lcoe = ((fcr * cc) + om) / (row["capacity"] * cf * 8760)
        return lcoe

    def lcot(self, row, nvalues, ovalues):
        """Calculate LCOT for a single row."""
        capacity = row["capacity"]
        fcr = nvalues["fcr"]
        cc = row["trans_cap_cost"] * capacity
#        cf = self._get_cf(row, ovalues)  # <---------------------------------- LCOT uses the table's cf (not as accurate), lcoe uses the original unrounded cf (more accurate)
        cf = row["mean_cf"]
        lcot = (cc * fcr) / (capacity * cf * 8760)
        return lcot

    def recalc(self, scenario, fcr=None, capex=None, opex=None, losses=None):
        """Recalculate LCOE for a data frame given a specific FCR."""
        # Get our constants
        fields = self._find_fields(scenario)
        config = self.project_config
        params = config["parameters"][scenario]

        # initiate new and original values dictionaries
        nvalues = dict(fcr=fcr, capex=capex, opex=opex, losses=losses)
        ovalues = dict()

        # If any or all of these are specified, use the user-specified version
        for key, value in nvalues.items():
            ovalues[key] = self._fix_format(params[fields[key]])
            if not value:
                nvalues[key] = ovalues[key]

        # Have to give FCR in percent and convert to ratio
        ovalues["fcr"] = ovalues["fcr"] / 100
        nvalues["fcr"] = nvalues["fcr"] / 100

        # Read in the table
        files = pd.DataFrame(config["data"])
        fname = files["file"][files["file"].str.contains(scenario)].values[0]
        directory = config["directory"]
        path = os.path.join(directory, fname)
        df = pd.read_csv(path, low_memory=False)

        # Recalculate LCOE figures
        df["mean_lcoe"] = df.apply(self.lcoe, nvalues=nvalues, ovalues=ovalues,
                                   axis=1)
        df["lcot"] = df.apply(self.lcot, nvalues=nvalues, ovalues=ovalues,
                              axis=1)
        df["total_lcoe"] = df["mean_lcoe"] + df["lcot"]

        return df

    def _find_fields(self, scenario):
        """Find input fields with pattern recognition."""
        config = self.project_config
        params = config["parameters"][scenario]
        patterns = {k.lower().replace(" ", ""): k for k in params.keys()}
        matches = {}
        for key in ["capex", "opex", "fcr", "losses"]:
            match = [v for k, v in patterns.items() if key in str(k)][0]
            matches[key] = match
        return matches

    def _fix_format(self, value):
        """Remove commas and dollar signs from value, return as float."""
        if isinstance(value, str):
            value = value.replace(",", "").replace("$", "").replace("%", "")
            value = float(value)
        return value

    def _get_cf(self, row, ovalues):
        """Return a properly rounded capacity factor from a table row."""
        capacity = row["capacity"] * 1000
        cc = ovalues["capex"] * capacity
        om = ovalues["opex"] * capacity
        fcr = ovalues["fcr"]
        lcoe = row["mean_lcoe"]
        return ((fcr * cc) + om) / (lcoe * row["capacity"] * 8760)


class Least_Cost():
    """Class to handle various elements of calculating a least cost table."""

    def __init__(self, project, recalc_table=None):
        """Initialize Least_Cost object."""
        self.project = project
        self.recalc_table = recalc_table

    def __repr__(self):
        """Print representation string."""
        msg = ("<reView Least_Cost object>")
        return msg

    def least_cost(self, dfs, by="total_lcoe"):
        """Return a single least cost df from a list dfs."""
        # Make one big data frame
        bdf = pd.concat(dfs)
        bdf = bdf.reset_index(drop=True)

        # Group, find minimum, and subset
        idx = bdf.groupby("sc_point_gid")[by].idxmin()
        df = bdf.iloc[idx]

        return df

    def calc(self, paths, dst, by="total_lcoe"):
        """Build the single least cost table from a list of tables."""
        # Not including an overwrite option for now
        if not os.path.exists(dst):

            # Collect all data frames - biggest lift of all
            paths.sort()
            dfs = []
            with mp.Pool(10) as pool:
                for df in tqdm(pool.imap(self.read_df, paths),
                               total=len(paths)):
                    dfs.append(df)

            # Make one big data frame and save
            df = self.least_cost(dfs, by=by)
            df.to_csv(dst, index=False)

    def read_df(self, path):
        """Retrieve a single data frame."""
        _, scenario = find_scenario(path)
        if self.recalc_table:
            table = self.recalc_table["scenario_a"]
            df = Data(self.project).build(scenario, **table)
        else:
            df = pd.read_csv(path, low_memory=False)
        df["scenario"] = scenario
        time.sleep(0.2)
        return df


class Plots(Config):
    """Class for handling grouped plots (needs work)."""

    def __init__(self, project, datasets, point_size, group="Scenarios",
                 yunits=None, xunits=None, xbin=None,
                 config_path="~/.review_config"):
        """Initialize plotting object for a reV project."""
        super().__init__(project, config_path)
        self.datasets = datasets
        self.group = group
        self.point_size = point_size
        self.yunits = yunits
        self.xunits = xunits
        self.xbin = xbin

    def __repr__(self):
        """Print representation string."""
        m = f"<Plots object: path={self.config_path}, project={self.project}>"
        return m

    def ccap(self):
        """Return a cumulative capacity scatterplot."""
        main_df = None
        for key, df in self.datasets.items():
            df = self._fix_doubles(df)
            if main_df is None:
                main_df = df.copy()
                y = main_df.columns[1]
                main_df = main_df.sort_values(y)
                main_df["ccap"] = main_df["capacity"].cumsum()
                main_df[self.group] = key
            else:
                y = df.columns[1]
                df = df.sort_values(y)
                df["ccap"] = df["capacity"].cumsum()
                df[self.group] = key
                main_df = pd.concat([main_df, df])

        if "_2" in y:
            labely = y.replace("_2", "")
        else:
            labely = y

        if self.yunits:
            units = self.yunits
        else:
            units = self.units[labely]

        main_df = main_df.sort_values(self.group)
        main_df["ccap"] = main_df["ccap"] / 1_000_000
        fig = px.scatter(
            main_df,
            x="ccap",
            y=y,
            custom_data=["sc_point_gid", "print_capacity"],
            labels={"ccap": "TW", y: units},
            color=self.group,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig.update_traces(
            marker=dict(
                size=self.point_size,
                line=dict(
                    width=0
                    )
                ),
            unselected=dict(
                marker=dict(
                    color="grey")
                )
            )

        return fig

    def binned(self):
        """Return a line plot."""
        # The clustered scatter plot part
        main_df = None
        for key, df in self.datasets.items():
            df = self._fix_doubles(df)
            if main_df is None:
                x = df.columns[0]
                y = df.columns[1]
                bins = self._bins(df[x])
                df = df.sort_values(x)
                df["xbin"] = df[x].apply(self._binit, bins=bins)
                df["ybin"] = df.groupby("xbin")[y].transform("mean")
                main_df = df.copy()
                main_df[self.group] = key
            else:
                df[self.group] = key
                df = df.sort_values(x)
                df["xbin"] = df[x].apply(self._binit, bins=bins)
                df["ybin"] = df.groupby("xbin")[y].transform("mean")
                main_df = pd.concat([main_df, df])

        # The simpler line plot part
        main_df = main_df.sort_values([x, self.group])
        main_df["ysum"] = main_df.groupby("xbin")[y].transform("sum")
        line_df = main_df.copy()
        line_df = line_df[["xbin", "ysum", self.group]].drop_duplicates()

        if "_2" in y:
            labely = y.replace("_2", "")
        else:
            labely = y

        if self.yunits:
            yunits = self.yunits
        else:
            yunits = self.units[labely]

        if self.xunits:
            xunits = self.xunits
        else:
            xunits = self.units[x]

        xlabel = f"{self.titles[x]} ({xunits})"

        # Points
        fig = px.scatter(
            main_df,
            x="xbin",
            y="ysum",  # Plot all y's so we can share selections with map
            custom_data=["sc_point_gid", "print_capacity"],
            labels={x: xlabel, y: yunits},
            color=self.group,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        # Lines
        colors = px.colors.qualitative.Safe
        for i, group in enumerate(line_df[self.group].unique()):
            df = line_df[line_df[self.group] == group]
            lines = px.line(df, x="xbin", y="ysum", color=self.group,
                            color_discrete_sequence=[colors[i]])  # <---------- We could run out of colors this way
            fig.add_trace(lines.data[0])

        fig.layout["xaxis"]["title"]["text"] = xlabel
        fig.layout["yaxis"]["title"]["text"] = labely

        fig.update_traces(
            marker=dict(
                size=self.point_size,
                line=dict(
                    width=0
                    )
                ),
            unselected=dict(
                marker=dict(
                    color="grey")
                )
            )

        return fig

    def scatter(self):
        """Return a regular scatterplot."""
        main_df = None
        for key, df in self.datasets.items():
            df = self._fix_doubles(df)
            if main_df is None:
                x = df.columns[0]
                y = df.columns[1]
                main_df = df.copy()
                main_df[self.group] = key
            else:
                df[self.group] = key
                main_df = pd.concat([main_df, df])

        if "_2" in y:
            labely = y.replace("_2", "")
        else:
            labely = y

        if self.yunits:
            yunits = self.yunits
        else:
            yunits = self.units[labely]

        if self.xunits:
            xunits = self.xunits
        else:
            xunits = self.units[x]

        main_df = main_df.sort_values(self.group)
        xlabel = f"{self.titles[x]} ({xunits})"
        fig = px.scatter(
            main_df,
            x=x,
            y=y,
            custom_data=["sc_point_gid", "print_capacity"],
            labels={x: xlabel, y: yunits},
            color=self.group,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig.update_traces(
            marker=dict(
                size=self.point_size,
                line=dict(
                    width=0
                    )
                ),
            unselected=dict(
                marker=dict(
                    color="grey")
                )
            )

        return fig

    def histogram(self):
        """Return a histogram."""
        main_df = None
        for key, df in self.datasets.items():
            df = self._fix_doubles(df)
            if main_df is None:
                y = df.columns[1]
                main_df = df.copy()
                main_df[self.group] = key
            else:
                df[self.group] = key
                main_df = pd.concat([main_df, df])

        if "_2" in y:
            labely = y.replace("_2", "")
        else:
            labely = y

        if self.yunits:
            yunits = self.yunits
        else:
            yunits = self.units[labely]

        main_df = main_df.sort_values(self.group)

        # Use preset scales for the x axis and max count for y axis
        limx = list(self.scales[y].values())

        fig = px.histogram(
            main_df,
            x=y,
            range_x=limx,
            range_y=[0, 4000],
            labels={y: yunits},
            color=self.group,
            color_discrete_sequence=px.colors.qualitative.Safe,
            barmode="overlay"
        )

        fig.update_traces(
            marker=dict(
                line=dict(
                    width=0
                )
            ),
            unselected=dict(
                marker=dict(
                    color="grey")
                )
            )

        return fig

    def box(self):
        """Return a boxplot."""
        def fix_key(key, units):
            """Display numbers and strings together."""
            if is_number(key):
                key = str(key) + units
            return key

        # Infer the y variable and units
        dfs = self.datasets
        df = dfs[list(dfs.keys())[0]]
        y = df.columns[1]

        if self.yunits:
            units = self.yunits
        else:
            units = self.project_config["units"][y]

        main_df = None
        for key, df in dfs.items():
            df = self._fix_doubles(df)
            if main_df is None:
                main_df = df.copy()
                main_df[self.group] = key
            else:
                df[self.group] = key
                main_df = pd.concat([main_df, df])

        if "_2" in y:  # What's this for?
            labely = y.replace("_2", "")
        else:
            labely = y

        if all(main_df[self.group].apply(lambda x: is_number(x))):
            main_df[self.group] = main_df[self.group].astype(int)
        main_df = main_df.sort_values(self.group)
        main_df[self.group] = main_df[self.group].apply(fix_key, units=units)

        fig = px.box(
            main_df,
            x=self.group,
            y=y,
            custom_data=["sc_point_gid", "print_capacity"],
            labels={y: units},
            color=self.group,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig.update_traces(
            marker=dict(
                size=self.point_size,
                opacity=1,
                line=dict(
                    width=0,
                    )
                ),
            unselected=dict(
                marker=dict(
                    color="grey")
                )
            )

        return fig

    def _bins(self, values):
        """Create a list of bins given a size and array of values."""
        minv = min(values)
        maxv = max(values)
        if self.xbin is None or self.xbin > maxv:
            self.xbin = maxv / 20
        n = int(np.ceil((maxv - minv) / self.xbin))
        steps = [round(minv + (i * self.xbin), 2) for i in range(n + 1)]
        bins = [(steps[i], steps[i + 1]) for i in range(len(steps) - 1)]
        return bins

    def _binit(self, x, bins):
        """Assign binned value to values."""
        try:
            xbin = [b for b in bins if x >= b[0] and x < b[1]][0]  # <------------- Ask if you want to use the top or bottom bin value
            return xbin[1]
        except IndexError:
            print("Index Error: " + str(x))

    def _fix_doubles(self, df):
        """Check and or fix columns names when they match."""
        if not isinstance(df, pd.core.frame.Series):
            cols = np.array(df.columns)
            counts = Counter(cols)
            for col, count in counts.items():
                if count > 1:
                    idx = np.where(cols == col)[0]
                    cols[idx[1]] = col + "_2"
            df.columns = cols
        return df
