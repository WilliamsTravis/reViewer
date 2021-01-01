#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapbox elements.

Created on Sat May 23 12:39:52 2020

@author: travis
"""


ACCESS_TOKEN = ("pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNkMnptaWlwc"
                "HZvdzdoIn0.9pxpgXxyyhM6qEF_dcyjIQ")

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
        accesstoken=ACCESS_TOKEN,
        style="satellite-streets",
        center=dict(lon=-95.7, lat=37.1),
        zoom=2))
