#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 15:47:40 2020

@author: travis
"""

import os

import pandas as pd


BASEMAPS = [{'label': 'Light', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
            {'label': 'Basic', 'value': 'basic'},
            {'label': 'Outdoors', 'value': 'outdoors'},
            {'label': 'Satellite', 'value': 'satellite'},
            {'label': 'Satellite Streets', 'value': 'satellite-streets'}]

MAPTOKEN = ('pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNkMnptaWlwcHZvd'
            'zdoIn0.9pxpgXxyyhM6qEF_dcyjIQ')

MAPLAYOUT = dict(
    height=500,
    font=dict(color='#CCCCCC',
              fontweight='bold'),
    titlefont=dict(color='#CCCCCC',
                   size='20',
                   family='Time New Roman',
                   fontweight='bold'),
    margin=dict(l=55, r=35, b=65, t=90, pad=4),
    hovermode="closest",
    plot_bgcolor="#083C04",
    paper_bgcolor="black",
    legend=dict(font=dict(size=10, fontweight='bold'), orientation='h'),
    title='<b>Index Values/b>',
    mapbox=dict(
        accesstoken=MAPTOKEN,
        style="satellite-streets",
        center=dict(lon=-95.7, lat=37.1),
        zoom=2)
)

TITLES = {'mean_cf': 'Mean Capacity Factor',
          'mean_lcoe': 'Mean Site-Based LCOE',
          'mean_res': 'Mean Windspeed',
          'capacity': 'Total Generation Capacity',
          'area_sq_km': 'Supply Curve Point Area',
          'trans_capacity': 'Total Transmission Capacity',
          'trans_cap_cost': 'Transmission Capital Costs',
          'lcot': 'LCOT',
          'total_lcoe': 'Total LCOE'}

UNITS = {'mean_cf': 'unitless',
         'mean_lcoe': '$/MWh',
         'mean_res': 'm/s',
         'capacity': 'MW',
         'area_sq_km': 'square km',
         'trans_capacity': 'MW',
         'trans_cap_cost': '$/MW',
         'lcot': '$/MWh',
         'total_lcoe': '$/MWh'}

STYLESHEET = 'https://codepen.io/chriddyp/pen/bWLwgP.css'


def make_scales(files, dst):
    """find the minimum and maximum values for each variable in all files."""

    if not os.path.exists(dst):
        dfs = []
        for f in files:
            dfs.append(pd.read_csv(f))
    
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


def get_label(options, value):
    option = [d for d in options if d["value"] == value]
    return option[0]["label"]

    
    
    