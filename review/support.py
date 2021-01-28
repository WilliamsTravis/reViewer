# -*- coding: utf-8 -*-
"""Support functions for the configurable review project.

Keepers to be moved to reView package.

Created on Sat Aug 15 15:47:40 2020

@author: travis
"""
import json
import os

from collections import Counter

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import pathos.multiprocessing as mp
import plotly.express as px
import us

from colorama import Style, Fore
from review import Data_Path, print_args
from tqdm import tqdm


CONFIG_PATH = os.path.expanduser("~/.review_config")  # <---------------------- This needs to be accessed dynamically
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)

AGGREGATIONS = {
    'area_sq_km': 'sum',
    'capacity': 'sum',
    'elevation': 'mean',
    'dist_mi': 'mean',
    'lcot': 'mean',
    'mean_cf': 'mean',
    'mean_lcoe': 'mean',
    'mean_res': 'mean',
    'total_lcoe': 'mean',
    'trans_capacity': 'sum',
    'trans_cap_cost': 'mean',
    'trans_multiplier': 'mean',
    'Hub Height': 'mean'
}


BASEMAPS = [{'label': 'Light', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
            {'label': 'Basic', 'value': 'basic'},
            {'label': 'Outdoors', 'value': 'outdoors'},
            {'label': 'Satellite', 'value': 'satellite'},
            {'label': 'Satellite Streets', 'value': 'satellite-streets'}]

BUTTON_STYLES = {
    "on": {
        'height': '45px',
        "width": "200px",
        'padding': '4px',
        'background-color': '#FCCD34',
        'border-radius': '4px',
        'font-family': 'Times New Roman',
        'font-size': '12px',
        'margin-top': '-2px'
        },
    "off": {
        'height': '45px',
        "width": "200px",
        'padding': '4px',
        'background-color': '#b89627',
        'border-radius': '4px',
        'font-family': 'Times New Roman',
        'font-size': '12px',
        'margin-top': '-2px'
        }
    }

CHART_OPTIONS = [{"label": "Cumulative Capacity", "value": "cumsum"},
                 {"label": "Scatterplot", "value": "scatter"},
                 {"label": "Histogram", "value": "histogram"},
                 {"label": "Boxplot", "value": "box"}]

COLORS = {'Blackbody': 'Blackbody', 'Bluered': 'Bluered', 'Blues': 'Blues',
          'Default': 'Default', 'Earth': 'Earth', 'Electric': 'Electric',
          'Greens': 'Greens', 'Greys': 'Greys', 'Hot': 'Hot', 'Jet': 'Jet',
          'Picnic': 'Picnic', 'Portland': 'Portland', 'Rainbow': 'Rainbow',
          'RdBu': 'RdBu',  'Viridis': 'Viridis', 'Reds': 'Reds',
          'RdWhBu': [[0.00, 'rgb(115,0,0)'],
                     [0.10, 'rgb(230,0,0)'],
                     [0.20, 'rgb(255,170,0)'],
                     [0.30, 'rgb(252,211,127)'],
                     [0.40, 'rgb(255, 255, 0)'],
                     [0.45, 'rgb(255, 255, 255)'],
                     [0.55, 'rgb(255, 255, 255)'],
                     [0.60, 'rgb(143, 238, 252)'],
                     [0.70, 'rgb(12,164,235)'],
                     [0.80, 'rgb(0,125,255)'],
                     [0.90, 'rgb(10,55,166)'],
                     [1.00, 'rgb(5,16,110)']],
          'RdWhBu (Extreme Scale)': [[0.00, 'rgb(115,0,0)'],
                                     [0.02, 'rgb(230,0,0)'],
                                     [0.05, 'rgb(255,170,0)'],
                                     [0.10, 'rgb(252,211,127)'],
                                     [0.20, 'rgb(255, 255, 0)'],
                                     [0.30, 'rgb(255, 255, 255)'],
                                     [0.70, 'rgb(255, 255, 255)'],
                                     [0.80, 'rgb(143, 238, 252)'],
                                     [0.90, 'rgb(12,164,235)'],
                                     [0.95, 'rgb(0,125,255)'],
                                     [0.98, 'rgb(10,55,166)'],
                                     [1.00, 'rgb(5,16,110)']],
          'RdYlGnBu': [[0.00, 'rgb(124, 36, 36)'],
                       [0.25, 'rgb(255, 255, 48)'],
                       [0.5, 'rgb(76, 145, 33)'],
                       [0.85, 'rgb(0, 92, 221)'],
                       [1.00, 'rgb(0, 46, 110)']],
          'BrGn (cb)': [[0.00, 'rgb(91, 74, 35)'],
                        [0.10, 'rgb(122, 99, 47)'],
                        [0.15, 'rgb(155, 129, 69)'],
                        [0.25, 'rgb(178, 150, 87)'],
                        [0.30, 'rgb(223,193,124)'],
                        [0.40, 'rgb(237, 208, 142)'],
                        [0.45, 'rgb(245,245,245)'],
                        [0.55, 'rgb(245,245,245)'],
                        [0.60, 'rgb(198,234,229)'],
                        [0.70, 'rgb(127,204,192)'],
                        [0.75, 'rgb(62, 165, 157)'],
                        [0.85, 'rgb(52,150,142)'],
                        [0.90, 'rgb(1,102,94)'],
                        [1.00, 'rgb(0, 73, 68)']],
          'YlGnBu (cb)': [[0.0, 'rgb(255,255,217)'],
                          [0.125, 'rgb(237,248,177)'],
                          [0.25, 'rgb(199,233,180)'],
                          [0.375, 'rgb(127,205,187)'],
                          [0.5, 'rgb(65,182,196)'],
                          [0.625, 'rgb(29,145,192)'],
                          [0.75, 'rgb(34,94,168)'],
                          [0.875, 'rgb(37,52,148)'],
                          [1.0, 'rgb(8,29,88)']],
          'YlOrBr (cb)': [[0.0, 'rgb(255,255,229)'],
                          [0.125, 'rgb(255,247,188)'],
                          [0.25, 'rgb(254,227,145)'],
                          [0.375, 'rgb(254,196,79)'],
                          [0.5, 'rgb(254,153,41)'],
                          [0.625, 'rgb(236,112,20)'],
                          [0.75, 'rgb(204,76,2)'],
                          [0.875, 'rgb(153,52,4)'],
                          [1.0, 'rgb(102,37,6)']],
          'YlGn (cb)': [[0.0, 'rgb(255,255,229)'],
                        [0.125, 'rgb(247,252,185)'],
                        [0.25, 'rgb(217,240,163)'],
                        [0.375, 'rgb(173,221,142)'],
                        [0.5, 'rgb(120,198,121)'],
                        [0.625, 'rgb(65,171,93)'],
                        [0.75, 'rgb(35,132,67)'],
                        [0.875, 'rgb(0,104,55)'],
                        [1.0, 'rgb(0,69,41)']]
          }

COLOR_OPTIONS = [{"label": k, "value": v} for k, v in COLORS.items()]

DEFAULT_MAPVIEW = {
    "mapbox.center": {
        "lon": -96.50,
        "lat": 39.5
    },
    "mapbox.zoom": 3.5,
    "mapbox.bearing": 0,
    "mapbox.pitch": 0
}

LCOEOPTIONS = [{"label": "Site-Based", "value": "mean_lcoe"},
               {"label": "Transmission", "value": "lcot"},
               {"label": "Total", "value": "total_lcoe"}]

MAP_LAYOUT = dict(
    height=700,
    font=dict(color='white',
              fontweight='bold'),
    titlefont=dict(color='white',
                   size=35,
                   family='Time New Roman',
                   fontweight='bold'),
    margin=dict(l=20, r=115, t=90, b=20),
    hovermode="closest",
    plot_bgcolor="#083C04",
    paper_bgcolor="#1663B5",
    legend=dict(font=dict(size=10, fontweight='bold'), orientation='h'),
    title=dict(
        yref="paper",
        x=0.1,
        y=1.4,
        yanchor="bottom",
        pad=dict(b=10)
    ),
    mapbox=dict(
        accesstoken=("pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNkMnpt"
                     "aWlwcHZvdzdoIn0.9pxpgXxyyhM6qEF_dcyjIQ"),
        style="satellite-streets",
        center=dict(lon=-100.75, lat=39.5),
        zoom=5)
)

ORIGINAL_FIELDS = ['sc_gid', 'res_gids', 'gen_gids', 'gid_counts', 'n_gids',
                   'mean_cf', 'mean_lcoe', 'mean_res', 'capacity',
                   'area_sq_km', 'latitude', 'longitude', 'country', 'state',
                   'county', 'elevation', 'timezone', 'sc_point_gid',
                   'sc_row_ind', 'sc_col_ind', 'res_class', 'trans_multiplier',
                   'trans_gid', 'trans_capacity', 'trans_type',
                   'trans_cap_cost', 'dist_mi', 'lcot', 'total_lcoe']

SCALE_OVERRIDES = {
    "total_lcoe": [0, 200],
    "mean_lcoe": [0, 200]
}

STYLESHEET = 'https://codepen.io/chriddyp/pen/bWLwgP.css'

TAB_STYLE = {'height': '25px', 'padding': '0'}

TABLET_STYLE = {'line-height': '25px', 'padding': '0'}

TITLES = {
    'area_sq_km': 'Supply Curve Point Area',
    'capacity': 'Total Generation Capacity',
    'elevation': 'Elevation',
    'dist_mi': 'Distance to Transmission',
    'lcot': 'LCOT',
    'mean_cf': 'Mean Capacity Factor',
    'mean_lcoe': 'Mean Site-Based LCOE',
    'mean_res': 'Mean Windspeed',
    'total_lcoe': 'Total LCOE',
    'trans_capacity': 'Total Transmission Capacity',
    'trans_cap_cost': 'Transmission Capital Costs',
    'transmission_multiplier': 'Transmission Cost Multiplier',
    'trans_type': 'Transmission Feature Type'
}

STATES = [{"label": s.name, "value": s.name} for s in us.STATES]

UNITS = {
    'area_sq_km': 'square km',
    'elevation': 'm',  # Double check this
    'capacity': 'MW',
    'dist_mi': 'miles',
    'lcot': '$/MWh',
    'mean_cf': 'ratio',
    'mean_lcoe': '$/MWh',
    'mean_res': 'm/s',  # This will change based on resource
    'total_lcoe': '$/MWh',
    'trans_capacity': 'MW',
    'trans_cap_cost': '$/MW',
    'transmission_multiplier': 'category',
    'trans_type': 'category'
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
    {"label": "Transmission Cost Multiplier", "value": "trans_ultiplier"},
    {"label": "Tranmission Feature Type", "value": "trans_type"},
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


def chart_point_filter(df, chartsel, chartvar):
    """Filter a dataframe by points selected from the chart."""
    points = chartsel["points"]
    idx = [p["pointIndex"] for p in points]
    df = df.iloc[idx]
    return df


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
        except:
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
        df = pd.read_csv(file)
        for field in fields:
            ranges[field] = {}
            try:
                values = df[field].dropna()
                values = values[values != -np.inf]
                ranges[field]["min"] = values.min()
                ranges[field]["max"] = values.max()
            except KeyError:
                print("KeyError")
                del ranges[field]
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


def get_variables(project_config):
    """Create a dictionary of variables given the extras in the config."""
    variables = project_config["titles"]
    return variables


def is_number(x):
    """check if a string is a number."""
    try:
        int(x)
        check = True
    except ValueError:
        check = False
    return check


def soco_config(directory, config=CONFIG):
    """Build a sample configuration file that can be used as template to
    build custom ones and around which to structure configurable reView.

    directory = "/shared-projects/rev/projects/soco/rev/final/wind/aggregation"
    """
    # Create data path object
    dp = Data_Path(directory)

    # Append to existing config or create new one
    if not config:
        config = {}

    # Find paths to all file
    template = {}
    files = dp.contents("*/*_sc.csv")  # <------------------------------------- Paramterize pattern recognition
    files.sort()
    template["file"] = files
    fdf = pd.DataFrame(template)

    # File grouping variables
    def lu(x):
        return os.path.basename(x).split("_")[0]

    def mw(x):
        return os.path.basename(x).split("_")[1].replace("mw", "")

    def hh(x):
        return os.path.basename(x).split("_")[2].replace("hh", "")

    def rs(x):
        return os.path.basename(x).split("_")[3].replace("rs", "")

    def ps(x):
        return os.path.basename(x).split("_")[4].replace("ps", "")

    def cc(x):
        cc_str = os.path.basename(x).split("_")[5].replace("cc", "")
        return "{:.2f}".format(int(cc_str) / 100)

    fdf["Land Use"] = fdf["file"].apply(lu)
    fdf["Rating"] = fdf["file"].apply(mw)
    fdf["Hub Height"] = fdf["file"].apply(hh)
    fdf["Relative Spacing"] = fdf["file"].apply(rs)
    fdf["Plant Size"] = fdf["file"].apply(ps)
    fdf["CAPEX Scale"] = fdf["file"].apply(cc)
    fdf["name"] = fdf["file"].apply(lambda x: os.path.basename(x))

    # Extra fields
    extra_titles = {
        "hh": "Hub Height",
        "rd": "Rotor Diameter",
        "Land Use": " Land Use",
        "Rating": "Rating",
        "Hub Height": "Hub Height",
        "Relative Spacing": "Relative Spacing",
        "Plant Size": "Plant Size",
        "CAPEX Scale": "CAPEX Scale"
        }
    extra_units = {
        "hh": "m",
        "rd": "m",
        "Land Use": " Category",
        "Rating": "MW",
        "Hub Height": "m",
        "Relative Spacing": "D",
        "Plant Size": "MW",
        "CAPEX Scale": ""
        }
    titles = {**TITLES, **extra_titles}
    units = {**UNITS, **extra_units}

    # Find scales for each field
    fields = list(units.keys())
    scales = get_scales(fdf, fields)

    # Create entry
    entry = {}
    entry["data"] = fdf.to_dict()
    entry["units"] = units
    entry["titles"] = titles
    entry["directory"] = directory
    entry["scales"] = scales

    config["Southern Company"] = entry
    with open(os.path.expanduser(CONFIG_PATH), "w") as file:
        file.write(json.dumps(config, indent=4))

    return entry


def transition_config(directory, config=CONFIG):
    """Build a sample configuration file that can be used as template to
    build custom ones and around which to structure configurable reView.

    directory = "/shared-projects/rev/projects/weto/fy21/transition/"
    directory = "/home/travis/nrel/transition/"
    """
    from revruns import rr

    # Create data path object
    dp = rr.Data_Path(directory)

    # Append to existing config or create new one
    if not config:
        config = {}

    # Find paths to all file
    template = {}
    # files = dp.contents("rev/results/*_sc.csv")
    files = dp.contents("data/*_sc.csv")
    files.sort()
    template["file"] = files
    fdf = pd.DataFrame(template)

    # Get lookup table for scenario variables
    fname = ("National Impact Innovations - Land Based WInd Scenario "
             "Matrix.xlsx")
    master = rr.get_sheet(dp.join("data", "tables", fname),
                          sheet_name="Rev_full_matrix")
    keepers = ["Rating (MW)", "Hub Height (m)", "Rotor diameter (m)",
               "Erection", "Tower Type", "Wake steering benefit", "O&M Crane",
               "Exclusion layer"]
    master = master[["Scenario number"] + keepers]

    fdf["name"] = fdf["file"].apply(lambda x: os.path.basename(x))
    fdf["Scenario number"] = fdf["name"].apply(lambda x: int(x.split("_")[1]))
    fdf = pd.merge(fdf, master, on="Scenario number")
    fields = master.columns
    master.columns = [f[:f.index("(") - 1] if "(" in f else f for f in fields]
    fdf.columns = [f[:f.index("(") - 1] if "(" in f else f for f in fdf.columns]

    del master["Scenario number"]
    del fdf["Scenario number"]
    for col in fdf.columns:
        fdf[col] = fdf[col].astype(str)

    # Extra fields
    extra_titles = {t: t for t in master.columns}
    extra_titles = {**extra_titles, **{"scenario": "Scenario"}}
    extra_units = {
        'Rating': 'category',
        'Hub Height': 'category',
        'Rotor diameter': 'caategory',
        'Erection': 'category',
        'Tower Type': 'category',
        'Wake steering benefit': 'category',
        'O&M Crane': 'category',
        'Exclusion layer': 'category',
        "scenario": "category"
    }
    titles = {**TITLES, **extra_titles}
    units = {**UNITS, **extra_units}

    # Find scales for each field
    scales = get_scales(fdf, units)

    # Create entry
    entry = {}
    entry["data"] = fdf.to_dict()
    entry["units"] = units
    entry["titles"] = titles
    entry["directory"] = directory
    entry["scales"] = scales

    config["Transition"] = entry
    with open(os.path.expanduser(CONFIG_PATH), "w") as file:
        file.write(json.dumps(config, indent=4))

    return entry


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


class Config:
    """Class for handling configuration variables."""

    def __init__(self, project):
        """Initialize plotting object for a reV project."""
        self.project_config = CONFIG[project]
        self.title_size = 20

    def map_title(self, variable, op_values):
        """Make a title for the map given a variable name and option values."""
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
    def options(self):
        """Not all options will be available for every grouping variable."""
        options = {}
        data = pd.DataFrame(self.project_config["data"])
        del data["file"]
        for col in data.columns:
            options[col] = list(data[col].unique())

    @property
    def data(self):
        """Return a pandas data frame with fuill file paths."""
        data = pd.DataFrame(self.project_config["data"])
        return data

    @property
    def titles(self):
        """Return a titles dictionary with extra fields."""
        titles = self.project_config["titles"]
        return titles

    @property
    def scales(self):
        """Return a titles dictionary with extra fields."""
        scales = self.project_config["scales"]
        for override, scale in SCALE_OVERRIDES.items():
            scales[override]["min"] = scale[0]
            scales[override]["max"] = scale[1]
        return scales

    @property
    def units(self):
        """Return a units dictionary with extra fields."""
        units = self.project_config["units"]
        return units


class Plots():
    """Class for handling grouped plots (needs work)."""

    def __init__(self, data, project, group, point_size, yunits=None,
                 xunits=None):
        """Initialize plotting object for a reV project."""
        self.data = data
        self.group = group
        self.point_size = point_size
        self.project = project
        self.project_config = CONFIG[project]
        self.config = Config(project)
        self.units = self.project_config["units"]
        self.yunits = yunits
        self.xunits = xunits

    def ccap(self):
        """Return a cumulative capacity scatterplot."""
        main_df = None
        for key, df in self.data.items():
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
        fig = px.scatter(main_df,
                         x="ccap",
                         y=y,
                         labels={"ccap": "TW",
                                 y: units},
                         color=self.group,
                         color_discrete_sequence=px.colors.qualitative.Safe)

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
        for key, df in self.data.items():
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
        fig = px.scatter(main_df,
                         x=x,
                         y=y,
                         labels={x: xunits, y: yunits},
                         color=self.group,
                         color_discrete_sequence=px.colors.qualitative.Safe)

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
        for key, df in self.data.items():
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
        fig = px.histogram(main_df,
                           x=y,
                           labels={y: yunits},
                           color=self.group,
                           color_discrete_sequence=px.colors.qualitative.Safe)

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
        dfs = self.data
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

        if "_2" in y:
            labely = y.replace("_2", "")
        else:
            labely = y

        if all(main_df[self.group].apply(lambda x: is_number(x))):
            main_df[self.group] = main_df[self.group].astype(int)
        main_df = main_df.sort_values(self.group)
        main_df[self.group] = main_df[self.group].apply(fix_key, units=units)

        fig = px.box(main_df,
                     x=self.group,
                     y=y,
                     labels={y: self.units[labely]},
                     color=self.group,
                     color_discrete_sequence=px.colors.qualitative.Safe)

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

    def _fix_doubles(self, df):
        """Check and or fix columns names when they match."""
        cols = np.array(df.columns)
        counts = Counter(cols)
        for col, count in counts.items():
            if count > 1:
                idx = np.where(cols == col)[0]
                cols[idx[1]] = col + "_2"
        df.columns = cols
        return df
