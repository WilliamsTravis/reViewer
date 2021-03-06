# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 15:47:40 2020

@author: travis
"""

import json
import os

from collections import Counter
from glob import glob

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import us

from colorama import Style, Fore
from dash.dependencies import Input
from review import Data_Path, print_args
from tqdm import tqdm


CONFIG_PATH = os.path.expanduser("~/.review_config")
NOPTIONS = 10
with open(CONFIG_PATH, "r") as file:
    CONFIG = json.load(file)


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
          # 'RdWhBu': [[0.00, 'rgb(115,0,0)'],
          #            [0.10, 'rgb(230,0,0)'],
          #            [0.20, 'rgb(255,170,0)'],
          #            [0.30, 'rgb(252,211,127)'],
          #            [0.40, 'rgb(255, 255, 0)'],
          #            [0.45, 'rgb(255, 255, 255)'],
          #            [0.55, 'rgb(255, 255, 255)'],
          #            [0.60, 'rgb(143, 238, 252)'],
          #            [0.70, 'rgb(12,164,235)'],
          #            [0.80, 'rgb(0,125,255)'],
          #            [0.90, 'rgb(10,55,166)'],
          #            [1.00, 'rgb(5,16,110)']],
          # 'RdWhBu (Extreme Scale)':  [[0.00, 'rgb(115,0,0)'],
          #                             [0.02, 'rgb(230,0,0)'],
          #                             [0.05, 'rgb(255,170,0)'],
          #                             [0.10, 'rgb(252,211,127)'],
          #                             [0.20, 'rgb(255, 255, 0)'],
          #                             [0.30, 'rgb(255, 255, 255)'],
          #                             [0.70, 'rgb(255, 255, 255)'],
          #                             [0.80, 'rgb(143, 238, 252)'],
          #                             [0.90, 'rgb(12,164,235)'],
          #                             [0.95, 'rgb(0,125,255)'],
          #                             [0.98, 'rgb(10,55,166)'],
          #                             [1.00, 'rgb(5,16,110)']],
          # 'RdYlGnBu':  [[0.00, 'rgb(124, 36, 36)'],
          #               [0.25, 'rgb(255, 255, 48)'],
          #               [0.5, 'rgb(76, 145, 33)'],
          #               [0.85, 'rgb(0, 92, 221)'],
          #               [1.00, 'rgb(0, 46, 110)']],
          # 'BrGn':  [[0.00, 'rgb(91, 74, 35)'],
          #           [0.10, 'rgb(122, 99, 47)'],
          #           [0.15, 'rgb(155, 129, 69)'],
          #           [0.25, 'rgb(178, 150, 87)'],
          #           [0.30, 'rgb(223,193,124)'],
          #           [0.40, 'rgb(237, 208, 142)'],
          #           [0.45, 'rgb(245,245,245)'],
          #           [0.55, 'rgb(245,245,245)'],
          #           [0.60, 'rgb(198,234,229)'],
          #           [0.70, 'rgb(127,204,192)'],
          #           [0.75, 'rgb(62, 165, 157)'],
          #           [0.85, 'rgb(52,150,142)'],
          #           [0.90, 'rgb(1,102,94)'],
          #           [1.00, 'rgb(0, 73, 68)']]
          }

COLOR_OPTIONS = [{"label": k, "value": v} for k, v in COLORS.items()]

DEFAULT_MAPVIEW = {
    "mapbox.center": {
        "lon": -85,
        "lat": 32.5
    },
    "mapbox.zoom": 5.0,
    "mapbox.bearing": 0,
    "mapbox.pitch": 0
}

LCOEOPTIONS = [{"label": "Site-Based", "value": "mean_lcoe"},
               {"label": "Transmission", "value": "lcot"},
               {"label": "Total", "value": "total_lcoe"}]

MAP_LAYOUT = dict(
    height=500,
    font=dict(color='white',
              fontweight='bold'),
    titlefont=dict(color='white',
                   size=35,
                   family='Time New Roman',
                   fontweight='bold'),
    margin=dict(l=20, r=115, t=70, b=20),
    hovermode="closest",
    plot_bgcolor="#083C04",
    paper_bgcolor="#1663B5",
    legend=dict(font=dict(size=10, fontweight='bold'), orientation='h'),
    title=dict(
        yref="paper",
        x=0.1,
        y=1,
        yanchor="bottom",
        pad=dict(b=10)
    ),
    mapbox=dict(
        accesstoken=("pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNkMnpt"
                     "aWlwcHZvdzdoIn0.9pxpgXxyyhM6qEF_dcyjIQ"),
        style="satellite-streets",
        center=dict(lon=-95.7, lat=37.1),
        zoom=2)
)

ORIGINAL_FIELDS = ['sc_gid', 'res_gids', 'gen_gids', 'gid_counts', 'n_gids',
                   'mean_cf', 'mean_lcoe', 'mean_res', 'capacity',
                   'area_sq_km', 'latitude', 'longitude', 'country', 'state',
                   'county', 'elevation', 'timezone', 'sc_point_gid',
                   'sc_row_ind', 'sc_col_ind', 'res_class', 'trans_multiplier',
                   'trans_gid', 'trans_capacity', 'trans_type',
                   'trans_cap_cost', 'dist_mi', 'lcot', 'total_lcoe']

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
    'trans_multiplier': 'Transmission Cost Multiplier',
    'trans_type': 'Transmission Feature Type'
}

STATES = [{"label": s.name, "value": s.name} for s in us.STATES]

UNITS = {
    'area_sq_km': 'square km',
    'elevation': 'm',  # Double check this
    'capacity': 'MW',
    'dist_mi': 'miles',
    'lcot': '$/MWh',
    'mean_cf': 'CF %',
    'mean_lcoe': '$/MWh',
    'mean_res': 'm/s',  # This will change based on resource
    'total_lcoe': '$/MWh',
    'trans_capacity': 'MW',
    'trans_cap_cost': '$/MW',
    'trans_multiplier': 'unitless',
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
            value=keys[0]
            )
        ], className="three columns"
    )

    return div


def chart_point_filter(df, chartsel, chartvar):
    """Filter a dataframe by points selected from the chart."""
    points = chartsel["points"]
    if "binNumber" in points[0]:
        vals = [p["x"] for p in points]
    else:
        vals = [p["y"] for p in points]
    try:
        df = df[(df[chartvar] >= min(vals)) &
                (df[chartvar] <= max(vals))]
    except ValueError:
        pass

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


def get_scales(project):
    """Read or create a value scale data frame for each variable."""  # <------ Parallelize and build into conifg
    project_config = CONFIG[project]
    dst = os.path.join(project_config["directory"], "review_scale.csv")
    if not os.path.exists(dst):
        data = pd.DataFrame(project_config["data"])
        groups = [c for c in data.columns if c not in ["file", "name"]]
        variables = get_variables(project_config)
        variables = [v for v in variables if v not in groups]
        scales = {}
        print("Calculating value scales for setting color ranges...")
        for variable in tqdm(variables):
            maxes = []
            mins = []
            for path in data["file"]:
                df = pd.read_csv(path)
                maxes.append(df[variable].max())
                mins.append(df[variable].min())
            scales[variable] = {}
            scales[variable]["max"] = max(maxes)
            scales[variable]["min"] = max(mins)    
        scales = pd.DataFrame(scales)
        scales.to_csv(dst, index=False)
    else:
        scales = pd.read_csv(dst)
        scales = scales.sort_values(list(scales.columns)[0])
        scales.index = ["min", "max"]
    return scales


def get_variables(project_config):
    """Create a dictionary of variables given the extras in the config."""
    variables = project_config["fields"]["titles"]
    return variables


def is_number(x):
    """check if a string is a number."""
    try:
        int(x)
        check = True
    except ValueError:
        check = False
    return check       


def bat_config(directory, config=None):
    """Build a sample configuration file that can be used as template to
    build custom ones and around which to structure configurable reView.

    directory = "/shared-projects/rev/projects/weto/bat_curtailment/rev_supply_curve"
    """
    cfs = {
        "0": "Jul 15 to Oct 16 - 5m/s (Variable: temp => ((15 / 7) * (ws) + 10)",
        "1": "Jul 15 to Oct 16 - 6m/s (Variable: temp => ((10 / 7) * (ws) + 10)",
        "2": "Jul 15 to Oct 16 - 6.9m/s (Variable: temp => ((5 / 7) * (ws) + 10)",
        "3": "Jul 01 to Nov 01 - 5m/s",
        "4": "Jul 01 to Nov 01 - 6m/s",
        "5": "Jul 01 to Nov 01 - 6.9m/s",
        "6": "Apr 01 Nov 01 - 5m/s",
        "7": "Apr 01 Nov 01 - 6m/s",
        "8": "Apr 01 Nov 01 - 6.9m/s",
        "no_curtailment": "no_curtailment"
    }

    sds = {
        "0": "50",
        "1": "100",
        "2": "200"
        }

    dp = Data_Path(directory)

    if not config:
        config = {}

    template = {}
    files = glob(dp.join(directory, "*/*_sc.csv"))
    files.sort()
    template["file"] = files

    fdf = pd.DataFrame(template)

    def strategy(x):
        if "no_curtailment" in x:
            return "no_curtailment"
        else:
            return os.path.basename(x).split("_")[0]        

    def curtailment(x):
        if "no_curtailment" in x:
            code = "no_curtailment"
        else:
            code = os.path.basename(x).split("_")[1].replace("cf", "")
        return cfs[code]

    def ps(x):
        code = os.path.basename(x).split("_")[2].replace("sd", "")
        return sds[code]

    fdf["Strategy"] = fdf["file"].apply(strategy)
    fdf["Curtailment"] = fdf["file"].apply(curtailment)
    fdf["Plant Size"] = fdf["file"].apply(ps)

    entry = {}
    entry["data"] = fdf.to_dict()
    entry["units"] = {"Strategy": " Category",
                      "Curtailment": " Category",
                      "Plant Size": " Category"}
    entry["directory"] = directory
    entry["extra_fields"] = {
            "titles": {
                "aep": "AEP",
                "b_aep": "Baseline AEP",
                "pr_aep": "Percent Reduction in AEP"
            },
            "units": {
                "aep": "MWh",
                "b_aep": "MWh",
                "pr_aep": "Ratio"
            }
    }
    config["WETO Bat Curtailment"] = entry
    with open(os.path.expanduser("~/.review_config"), "w") as file:
        file.write(json.dumps(config, indent=4))

    return entry


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

    # Create entry
    entry = {}
    entry["data"] = fdf.to_dict()
    entry["units"] = units
    entry["titles"] = titles
    entry["directory"] = directory
    entry["fields"] = {
        "titles": titles,
        "units": units
        }

    config["Southern Company"] = entry
    with open(os.path.expanduser("~/.review_config"), "w") as file:
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
    def __init__(self, project):
        """Initialize plotting object for a reV project."""
        self.project_config = CONFIG[project]
        self.title_size = 20

    def map_title(self, variable, op_values):
        """Make a title for the map given a variable name and option values."""
        var_title = self.titles[variable]
        for op, val in op_values.items():
            units = self.project_config["fields"]["units"][op]
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
            units = self.project_config["fields"]["units"][op]
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
        titles = self.project_config["fields"]["titles"]
        return titles

    @property
    def units(self):
        """Return a units dictionary with extra fields."""
        units = self.project_config["fields"]["units"]
        return units


class Plots:
    def __init__(self, data, project, group, point_size):
        """Initialize plotting object for a reV project."""
        self.data = data
        self.group = group
        self.point_size = point_size
        self.project = project
        self.project_config = CONFIG[project]
        self.units = self.project_config["fields"]["units"]

    def ccap(self):
        """Return a cumulative capacity scatterplot."""
        main_df = None
        for key, df in self.data.items():
            df = self._fix_doubles(df)
            if main_df is None:
                main_df = df.copy()
                y = main_df.columns[1]  # <------------------------------ Fix case where y =="capacity"
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

        main_df = main_df.sort_values(self.group)
        fig = px.scatter(main_df,
                         x="ccap",
                         y=y,
                         labels={"ccap": UNITS["capacity"], y: UNITS[labely]},
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

        main_df = main_df.sort_values(self.group)
        fig = px.scatter(main_df,
                         x=x,
                         y=y,
                         labels={x: UNITS[x], y: UNITS[labely]},
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

        main_df = main_df.sort_values(self.group)
        fig = px.histogram(main_df,
                           x=y,
                           labels={y: UNITS[labely]},
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

        units = self.project_config["units"][self.group]
        def fix_key(key, units):
            """It can't display numbers and strings together."""
            if is_number(key):
                key = str(key) + units
            return key

        main_df = None
        data = self.data.copy()
        for key, df in data.items():
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

        if all(main_df[self.group].apply(lambda x: is_number(x))):
            main_df[self.group] = main_df[self.group].astype(int)
        main_df = main_df.sort_values(self.group)
        main_df[self.group] = main_df[self.group].apply(fix_key, units=units)

        fig = px.box(main_df,
                     x=self.group,
                     y=y,
                     labels={y: UNITS[labely]},
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
