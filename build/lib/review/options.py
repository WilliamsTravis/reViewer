#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All option dictionaries for reViewer

Created on Sat May 23 12:32:12 2020

@author: travis
"""

# Map type options
BASEMAPS = [{'label': 'Light', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
            {'label': 'Basic', 'value': 'basic'},
            {'label': 'Outdoors', 'value': 'outdoors'},
            {'label': 'Satellite', 'value': 'satellite'},
            {'label': 'Satellite Streets', 'value': 'satellite-streets'}]

# Data Set Options
DATAFOLDERS = [{"label": "Florida Sample", "value": "ipm_wind_florida"}]

# Color scale options - not everyone is built in
COLORS = ['Default', 'Blackbody', 'Bluered', 'Blues', 'Earth', 'Electric',
          'Greens', 'Greys', 'Hot', 'Jet', 'Picnic', 'Portland',
          'Rainbow', 'RdBu', 'Reds', 'Viridis', 'RdWhBu',
          'RdWhBu (Extreme Scale)', 'RdYlGnBu', 'BrGn']
COLORSCALES = [{'label': c, 'value': c} for c in COLORS]
ZOOMLEVELS = {
    1: 1,
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 2,
    7: 2,
    8: 3,
    9: 3,
    10: 3,
    11: 4,
    12: 4,
    13: 4,
    14: 4,
    15: 5,
    16: 5,
    17: 5,
    18: 5,
    19: 5,
    20: 5
}

# Date options
def date_options(min_year, max_year):
    """
    min_year = 1998
    max_year = 2018
    """
    years = [int(y) for y in range(min_year, max_year + 1)]
    months = [int(m) for m in range(1, 13)]
    yearmarks = {y: {'label': y, 'style': {"transform": "rotate(45deg)"}} for
                 y in years}
    monthmarks = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                  7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov',
                  12: 'Dec'}
    monthoptions = [{'label': monthmarks[i], 'value': i} for i in range(1, 13)]
    months_slanted = {i: {'label': monthmarks[i],
                          'style': {"transform": "rotate(45deg)"}} for i in months}

    # Only display every 5 years for space
    for y in years:
        if y % 5 != 0:
            yearmarks[y] = ""
