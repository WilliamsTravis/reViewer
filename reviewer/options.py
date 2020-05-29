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

FILES = [{"label": "CONUS Sample", "value": "conus_sc.csv"},
         {"label": "Florida Sample", "value": "florida_sc.csv"}]

# Color scale options - not everyone is built in
COLORS = ['Default', 'Blackbody', 'Bluered', 'Blues', 'Earth', 'Electric',
          'Greens', 'Greys', 'Hot', 'Jet', 'Picnic', 'Portland',
          'Rainbow', 'RdBu', 'Reds', 'Viridis', 'RdWhBu',
          'RdWhBu (Extreme Scale)', 'RdYlGnBu', 'BrGn']
COLORSCALES = [{'label': c, 'value': c} for c in COLORS]


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
