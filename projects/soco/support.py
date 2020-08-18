# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 15:47:40 2020

@author: travis
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from revruns import Data_Path


DATAPATH = Data_Path("./data")


BASEMAPS = [{'label': 'Light', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
            {'label': 'Basic', 'value': 'basic'},
            {'label': 'Outdoors', 'value': 'outdoors'},
            {'label': 'Satellite', 'value': 'satellite'},
            {'label': 'Satellite Streets', 'value': 'satellite-streets'}]

BUTTON_STYLES = {
    "on": {
        'height': '45px',
        "width": "225px",
        'padding': '4px',
        'background-color': '#FCCD34',
        'border-radius': '4px',
        'font-family': 'Times New Roman',
        'font-size': '13px',
        'margin-top': '-2px'
        },
    "off": {
        'height': '45px',
        "width": "225px",
        'padding': '4px',
        'background-color': '#b89627',
        'border-radius': '4px',
        'font-family': 'Times New Roman',
        'font-size': '13px',
        'margin-top': '-2px'
        }
    }

CHARTOPTIONS = [{"label": "Cumulative Capacity", "value": "cumsum"},
                {"label": "Scatterplot", "value": "scatter"},
                {"label": "Histogram", "value": "histogram"},
                {"label": "Boxplot", "value": "box"}]

COLORS = {'Blackbody': 'Blackbody', 'Bluered': 'Bluered', 'Blues': 'Blues',
          'Default': 'Default', 'Earth': 'Earth', 'Electric': 'Electric',
          'Greens': 'Greens', 'Greys': 'Greys', 'Hot': 'Hot', 'Jet': 'Jet',
          'Picnic': 'Picnic', 'Portland': 'Portland', 'Rainbow': 'Rainbow',
          'RdBu': 'RdBu',  'Viridis': 'Viridis', 'Reds': 'Reds',
          # 'RdWhBu': [[0.00, 'rgb(115,0,0)'],
          #             [0.10, 'rgb(230,0,0)'],
          #             [0.20, 'rgb(255,170,0)'],
          #             [0.30, 'rgb(252,211,127)'],
          #             [0.40, 'rgb(255, 255, 0)'],
          #             [0.45, 'rgb(255, 255, 255)'],
          #             [0.55, 'rgb(255, 255, 255)'],
          #             [0.60, 'rgb(143, 238, 252)'],
          #             [0.70, 'rgb(12,164,235)'],
          #             [0.80, 'rgb(0,125,255)'],
          #             [0.90, 'rgb(10,55,166)'],
          #             [1.00, 'rgb(5,16,110)']],
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

DATASETS = [
    {"label": "120m Hub Height", "value": DATAPATH.join("120hh_20ps.csv")},
    {"label": "140m Hub Height", "value": DATAPATH.join("140hh_20ps.csv")},
    {"label": "160m Hub Height", "value": DATAPATH.join("160hh_20ps.csv")}
    ]

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

MAPTOKEN = ('pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNkMnptaWlwcHZvd'
            'zdoIn0.9pxpgXxyyhM6qEF_dcyjIQ')

MAPLAYOUT = dict(
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
        accesstoken=MAPTOKEN,
        style="satellite-streets",
        center=dict(lon=-95.7, lat=37.1),
        zoom=2)
)

RESET_BUTTON_STYLE = {
        'height': '100%',
        'background-color': '#FCCD34',
        "display": "table-cell"
        }

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

SCALES = {
    "mean_cf": {},
    "mean_lcoe": {},
    "mean_res": {},
    "capacity": {},
    "area_sq_km": {},
    "trans_capacity": {},
    "trans_cap_cost": {},
    "lcot": {},
    "total_lcoe": {}
    }

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


def fix_cfs(files):
    """Convert capacity factors to percents if needed."""
    for f in files:
        df = pd.read_csv(f)
        if "ps" in f and "mean_cf" in df.columns:
            if df["mean_cf"].max() < 1:
                df["mean_cf"] = round(df["mean_cf"] * 100, 2)
                df.to_csv(f, index=False)


def get_label(options, value):
    """Get the label of a DASH list of options, given the value."""
    option = [d for d in options if d["value"] == value]
    return option[0]["label"]


def make_scales(files, dst):
    """Find the minimum and maximum values for each variable in all files."""
    if not os.path.exists(dst):
        dfs = []
        for f in files:
            df = pd.read_csv(f)
            df["mean_cf"] = round(df["mean_cf"] * 100, 2)
            dfs.append(df)

        ranges = {}
        for variable in TITLES.keys():
            mins = []
            maxes = []
            for df in dfs:
                var = df[variable]
                mins.append(var.min())
                maxes.append(var.max())
            ranges[variable] = [min(mins), max(maxes)]

        ranges = pd.DataFrame(ranges)
        ranges.to_csv(dst, index=False)

    ranges = pd.read_csv(dst)
    ranges.index = ["min", "max"]

    return ranges


# Chart functions
def get_ccap(paths, y, mapsel, point_size):
    """Return a cumulative capacity scatterplot."""
    df = None
    for key, path in paths.items():
        if df is None:
            df = pd.read_csv(path)
            df["gid"] = df.index
            df = df[["gid", "capacity", y]]
            if y == "capacity":
                df.columns = ["gid", "capacity", "capacity2"]
                var = "capacity2"
            else:
                var = y
            df = df.sort_values(var)
            df["ccap"] = df["capacity"].cumsum()
            df["value"] = df[var]
            df["hh"] = key
            df = df[["gid", "ccap", "value", "hh"]]
        else:
            df2 = pd.read_csv(path)
            df2["gid"] = df2.index
            df2 = df2[["gid", "capacity", y]]
            if y == "capacity":
                df2.columns = ["gid", "capacity", "capacity2"]
                var = "capacity2"
            else:
                var = y
            df2 = df2.sort_values(var)
            df2["hh"] = key
            df2["ccap"] = df2["capacity"].cumsum()
            df2["value"] = df2[var]
            df2["hh"] = key
            df2 = df2[["gid", "ccap", "value", "hh"]]
            df = pd.concat([df, df2])

    df = df.sort_values("ccap")

    if mapsel:
        idx = [p["pointIndex"] for p in mapsel["points"]]
        df = df[df["gid"].isin(idx)]

    fig = px.scatter(df,
                     x="ccap",
                     y="value",
                     title=(get_label(VARIABLES, y) +
                            " by Cumulative Capacity"),
                     labels={"ccap": UNITS["capacity"],
                             "value": UNITS[y]},
                     color='hh')

    fig.update_traces(
        marker=dict(
            size=point_size,
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


def get_scatter(paths, x, y, mapsel, point_size):
    """Return a regular scatterplot."""
    df = None
    for key, path in paths.items():
        if df is None:
            df = pd.read_csv(path)
            df["gid"] = df.index
            df = df[["gid", x, y]]
            if x == y:
                df.columns = ["gid", x, y + "2"]
                var = y + "2"
            else:
                var = y
            df = df.sort_values(var)
            df["x"] = df[x]
            df["value"] = df[var]
            df["hh"] = key
            df = df[["gid", "x", "value", "hh"]]
        else:
            df2 = pd.read_csv(path)
            df2["gid"] = df2.index
            df2 = df2[["gid", x, y]]
            if x == y:
                df2.columns = ["gid",  x, y + "2"]
                var = y + "2"
            else:
                var = y
            df2 = df2.sort_values(var)
            df2["x"] = df2[x]
            df2["value"] = df2[var]
            df2["hh"] = key
            df2 = df2[["gid", "x", "value", "hh"]]
            df = pd.concat([df, df2])

    df = df.sort_values("x")

    if mapsel:
        idx = [p["pointIndex"] for p in mapsel["points"]]
        df = df[df["gid"].isin(idx)]

    fig = px.scatter(df,
                     x="x",
                     y="value",
                     title=(get_label(VARIABLES, y) + " by " +
                            get_label(VARIABLES, x)),
                     labels={"x": UNITS[x],
                             "value": UNITS[y]},
                     color='hh')

    fig.update_traces(
        marker=dict(
            size=point_size,
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


def get_histogram(paths, y, mapsel, point_size):
    """Return a histogram."""
    df = None
    for key, path in paths.items():
        if df is None:
            df = pd.read_csv(path)
            df["gid"] = df.index
            df = df[["gid", y]]
            df["hh"] = key
            df = df[["gid", y, "hh"]]
        else:
            df2 = pd.read_csv(path)
            df2["gid"] = df2.index
            df2 = df2[["gid", y]]
            df2["hh"] = key
            df2 = df2[["gid", y, "hh"]]
            df = pd.concat([df, df2])

    if mapsel:
        idx = [p["pointIndex"] for p in mapsel["points"]]
        df = df[df["gid"].isin(idx)]

    fig = px.histogram(df,
                       x=y,
                       color="hh",
                       title=get_label(VARIABLES, y) + " Histogram",
                       labels={y: UNITS[y]})

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


def get_boxplot(paths, y, mapsel, point_size):
    """Return a set of boxplots."""
    df = None
    for key, path in paths.items():
        if df is None:
            df = pd.read_csv(path)
            df["gid"] = df.index
            df = df[["gid", y]]
            df["hh"] = key
            df = df[["gid", y, "hh"]]
        else:
            df2 = pd.read_csv(path)
            df2["gid"] = df2.index
            df2 = df2[["gid", y]]
            df2["hh"] = key
            df2 = df2[["gid", y, "hh"]]
            df = pd.concat([df, df2])

    if mapsel:
        idx = [p["pointIndex"] for p in mapsel["points"]]
        df = df[df["gid"].isin(idx)]

    fig = px.box(df, x="hh", y=y, color="hh",
                 title=get_label(VARIABLES, y) + " Boxplots",
                 labels={y: UNITS[y]})

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
