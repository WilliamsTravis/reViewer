# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 15:47:40 2020

@author: travis
"""

from glob import glob
import json
import os

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import us

from dash.dependencies import Input
from review import Data_Path
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

STYLESHEET = 'https://codepen.io/chriddyp/pen/bWLwgP.css'

TAB_STYLE = {'height': '25px', 'padding': '0'}

TABLET_STYLE = {'line-height': '25px', 'padding': '0'}

TITLES = {'mean_cf': 'Mean Capacity Factor',
          'mean_lcoe': 'Mean Site-Based LCOE',
          'mean_res': 'Mean Windspeed',
          'capacity': 'Total Generation Capacity',
          'area_sq_km': 'Supply Curve Point Area',
          'trans_capacity': 'Total Transmission Capacity',
          'trans_cap_cost': 'Transmission Capital Costs',
          'lcot': 'LCOT',
          'total_lcoe': 'Total LCOE'}

STATES = [{"label": s.name, "value": s.name} for s in us.STATES]

UNITS = {'mean_cf': 'CF %',
         'mean_lcoe': '$/MWh',
         'mean_res': 'm/s',
         'capacity': 'MW',
         'area_sq_km': 'square km',
         'trans_capacity': 'MW',
         'trans_cap_cost': '$/MW',
         'lcot': '$/MWh',
         'total_lcoe': '$/MWh'}

VARIABLES = [
    {"label": "Mean Capacity Factor", "value": "mean_cf"},
    {"label": "Mean Windspeed", "value": "mean_res"},
    {"label": "Total Generation Capacity", "value": "capacity"},
    {"label": "Supply Curve Point Area", "value": "area_sq_km"},
    {"label": "Total Transmission Capacity", "value": "trans_capacity"},
    {"label": 'Transmission Capital Costs', "value": 'trans_cap_cost'},
    {"label": "Mean Site-Based LCOE", "value": "mean_lcoe"},
    {"label": "LCOT", "value": "lcot"},
    {"label": "Total LCOE", "value": "total_lcoe"}

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


def get_dataframe_path(project, *options):
    """Get the table for a set of options."""
    # There will be Nones
    options = [str(o) for o in options if o]
    if options:
        # Extract the project config and its data frame
        project_config = CONFIG[project]
        directory = project_config["directory"]
        data = pd.DataFrame(project_config["data"])
        cols = data.columns
    
        # Find the matching path
        for i, option in enumerate(options):
            data = data[data[cols[i + 1]] == option]
        try:
            assert data.shape[0] == 1
            path = os.path.join(directory, data["file"].values[0])
        except:
            raise AssertionError(
                "The options did not result in a single selection."
                )
        return path


def get_scales(project):
    """Read or create a value scale data frame for each variable."""
    project_config = CONFIG[project]
    dst = os.path.join(project_config["directory"], "review_scale.csv")
    if not os.path.exists(dst):
        variables = get_variables(project_config)
        data = pd.DataFrame(project_config["data"])
        scales = {}
        print("Calculating value scales for setting color ranges...")
        for variable in tqdm(variables):
            maxes = []
            mins = []
            for file in data["file"]:
                path = os.path.join(project_config["directory"], file)
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
        scales.index = ["min", "max"]
    return scales


def get_variables(project_config):
    """Create a dictionary of variables given the extras in the config."""
    extra_fields = project_config["extra_fields"]["titles"]
    variables = {**TITLES, **extra_fields}
    return variables


def is_number(x):
    """check if a string is a number."""
    try:
        int(x)
        check = True
    except ValueError:
        check = False
    return check       


def sample_config(directory, config=None):
    """Build a sample configuration file that can be used as template to
    build custom ones and around which to structure configurable reView.
    
    directory = "/home/travis/github/reView/projects/configurable/data"
    """

    dp = Data_Path(directory)

    if not config:
        config = {}

    template = {}
    files = [os.path.basename(f) for f in glob(dp.join(directory, "*csv"))]
    files.sort()
    files.remove("scales.csv")
    template["file"] = files

    fdf = pd.DataFrame(template)

    def hh(x):
        if not "lcoe" in x:
            return x[:3]
        else:
            return x[:11]

    def ps(x):
        if not "lcoe" in x:
            ps = x.split("_")[1].replace("ps", "")
        else:
            ps = x.split("_")[2].replace("ps", "")
        return ps

    fdf["Hub Height"] = fdf["file"].apply(hh)
    fdf["Plant Size"] = fdf["file"].apply(ps)

    entry = {}
    entry["data"] = fdf.to_dict()
    entry["units"] = {"Hub Height": "m", "Plant Size": "MW"}
    entry["directory"] = directory
    entry["extra_fields"] = {
        "titles": {
            "hh": "Hub Height",
            "rd": "Rotor Diameter",
            "mw": "Plant Size",
            "rs": "Relative Spacing"
            },
        "units": {
            "hh": "m",
            "rd": "m",
            "mw": "MW",
            "rs": "unitless"
            }
        }

    config["Southern Company"] = entry
    with open(os.path.expanduser("~/.review_config"), "w") as file:
        file.write(json.dumps(config, indent=4))

    return entry


def setup_options(n):
    """Setup option inputs and placeholder options."""
    opt_inputs = [Input("option_{}".format(i), "value") for i in range(n)]
    option_placeholders = []
    for i in range(n):
        op = html.Div(dcc.Dropdown(id="option_{}".format(i)),
                      style={"display": "none"})
        option_placeholders.append(op)
    var = html.Div(dcc.Dropdown(id="variable", value="placeholder"),
                   style={"display": "none"})
    option_placeholders = option_placeholders + [var]
    return opt_inputs, option_placeholders


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



class Plots:
    def __init__(self, data, project, group, point_size):
        """Initialize plotting object for a reV project."""
        self.data = data
        self.group = group
        self.point_size = point_size
        self.project = project
        self.project_config = CONFIG[project]
        self.units = self.project_config["units"]

    def ccap(self):
        """Return a cumulative capacity scatterplot."""
        main_df = None
        for key, df in self.data.items():
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

        main_df = main_df.sort_values(self.group)
        fig = px.scatter(main_df,
                         x="ccap",
                         y=y,
                         labels={"ccap": UNITS["capacity"], y: UNITS[y]},
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
            if main_df is None:
                x = df.columns[0]
                y = df.columns[1]
                main_df = df.copy()
                main_df[self.group] = key
            else:
                df[self.group] = key
                main_df = pd.concat([main_df, df])

        main_df = main_df.sort_values(self.group)
        fig = px.scatter(main_df,
                         x=x,
                         y=y,
                         labels={x: UNITS[x], y: UNITS[y]},
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
            if main_df is None:
                y = df.columns[1]
                main_df = df.copy()
                main_df[self.group] = key
            else:
                df[self.group] = key
                main_df = pd.concat([main_df, df])

        main_df = main_df.sort_values(self.group)

        fig = px.histogram(main_df,
                           x=y,
                           labels={y: UNITS[y]},
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
            if main_df is None:
                y = df.columns[1]
                main_df = df.copy()
                main_df[self.group] = key
            else:
                df[self.group] = key
                main_df = pd.concat([main_df, df])

        if all(main_df[self.group].apply(lambda x: is_number(x))):
            main_df[self.group] = main_df[self.group].astype(int)
        main_df = main_df.sort_values(self.group)
        main_df[self.group] = main_df[self.group].apply(fix_key, units=units)

        fig = px.box(main_df,
                     x=self.group,
                     y=y,
                     labels={y: UNITS[y]},
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


def get_boxplot(paths, y, mapsel, point_size, state, reset, trig):
    """Return a set of boxplots."""
    df = None
    for key, path in paths.items():
        if df is None:
            df = DATASETS[path].copy()
            df["gid"] = df.index
            df = df[["gid", "state", y]]
            if "Winner" not in key:
                df["HH"] = key + " m"
            else:
                df["HH"] = key
            df = df[["gid", "state", y, "HH"]]
        else:
            df2 = DATASETS[path].copy()
            df2["gid"] = df2.index
            df2 = df2[["gid", "state", y]]
            if "Winner" not in key:
                df2["HH"] = key + " m"
            else:
                df2["HH"] = key
            df2 = df2[["gid", "state", y, "HH"]]
            df = pd.concat([df, df2])

    # Sort consistently
    df = df.sort_values("HH")

    if "reset" not in trig:

        if mapsel:
            idx = [p["pointIndex"] for p in mapsel["points"]]
            df = df[df["gid"].isin(idx)]
        if state:
            df = df[df["state"].isin(state)]

    fig = px.box(df,
                 x="HH",
                 y=y,
                 labels={y: UNITS[y]},
                 color="HH",
                 color_discrete_sequence=px.colors.qualitative.Safe)

    fig.update_traces(
        marker=dict(
            size=point_size,
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