#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brainstorming the best way to configure a rev run for review. Try to build
review using this template and then write something that will build this
config for other projects.

Created on Fri Sep 11 11:13:04 2020

@author: twillia2
"""

import json

config_template = {
 "soco": {
     "project_directory": ("/shared-projects/rev/projects/soco/rev/runs/"
                           "aggregation"),
     "groups": {
         "Land Use": {
             "values": ["open", "reference", "restricted"],
             "units": "unitless"
         },
         "Hub Height": {
             "values": [120, 140, 160],
             "units": "m"
         },
         "Plant Size": {
             "values": [20, 150],
             "units": "m"
         },
         "Include Coast": {
             "values": ["yes", "no"],
             "units": "unitless"
         }
     },
     "files": {
         'open_120hh_150ps_coast/open_120hh_150ps_coast_sc.csv':
             ["open", 120, 150, "yes"],
         'open_140hh_150ps_coast/open_140hh_150ps_coast_sc.csv':
             ["open", 140, 150, "yes"],
         'open_160hh_150ps_coast/open_160hh_150ps_coast_sc.csv':
             ["open", 160, 150, "yes"],
         'open_120hh_20ps_coast/open_120hh_20ps_coast_sc.csv':
             ["open", 120, 20, "yes"],
         'open_140hh_20ps_coast/open_140hh_20ps_coast_sc.csv':
             ["open", 120, 20, "yes"],
         'open_160hh_20ps_coast/open_160hh_20ps_coast_sc.csv':
             ["open", 120, 20, "yes"],
         'open_120hh_150ps_nocoast/open_120hh_150ps_nocoast_sc.csv':
             ["open", 120, 150, "no"],
         'open_140hh_150ps_nocoast/open_140hh_150ps_nocoast_sc.csv':
             ["open", 140, 150, "no"],
         'open_160hh_150ps_nocoast/open_160hh_150ps_nocoast_sc.csv':
             ["open", 160, 150, "no"],
         'open_120hh_20ps_nocoast/open_120hh_20ps_nocoast_sc.csv':
             ["open", 120, 20, "no"],
         'open_160hh_20ps_nocoast/open_160hh_20ps_nocoast_sc.csv':
             ["open", 140, 20, "no"],
         'open_140hh_20ps_nocoast/open_140hh_20ps_nocoast_sc.csv':
             ["open", 160, 20, "no"],
         'reference_120hh_150ps_coast/reference_120hh_150ps_coast_sc.csv':
             ["reference", 120, 150, "yes"],
         'reference_140hh_150ps_coast/reference_140hh_150ps_coast_sc.csv':
             ["reference", 140, 150, "yes"],
         'reference_160hh_150ps_coast/reference_160hh_150ps_coast_sc.csv':
             ["reference", 150, 150, "yes"],
         'reference_120hh_20ps_coast/reference_120hh_20ps_coast_sc.csv':
             ["reference", 120, 20, "yes"],
         'reference_140hh_20ps_coast/reference_140hh_20ps_coast_sc.csv':
             ["reference", 140, 20, "yes"],
         'reference_160hh_20ps_coast/reference_160hh_20ps_coast_sc.csv':
             ["reference", 160, 20, "yes"],
         'reference_120hh_150ps_nocoast/reference_120hh_150ps_nocoast_sc.csv':
             ["reference", 120, 150, "no"],
         'reference_140hh_150ps_nocoast/reference_140hh_150ps_nocoast_sc.csv':
             ["reference", 140, 120, "no"],
         'reference_160hh_150ps_nocoast/reference_160hh_150ps_nocoast_sc.csv':
             ["reference", 160, 150, "no"],
         'reference_120hh_20ps_nocoast/reference_120hh_20ps_nocoast_sc.csv':
             ["reference", 120, 20, "no"],
         'reference_140hh_20ps_nocoast/reference_140hh_20ps_nocoast_sc.csv':
             ["reference", 140, 20, "no"],
         'reference_160hh_20ps_nocoast/reference_160hh_20ps_nocoast_sc.csv':
             ["reference", 160, 20, "no"],
         'restricted_120hh_150ps_coast/restricted_120hh_150ps_coast_sc.csv':
             ["restricted", 120, 150, "yes"],
         'restricted_140hh_150ps_coast/restricted_140hh_150ps_coast_sc.csv':
             ["restricted", 140, 150, "yes"],
         'restricted_160hh_150ps_coast/restricted_160hh_150ps_coast_sc.csv':
             ["restricted", 160, 150, "yes"],
         'restricted_120hh_20ps_coast/restricted_120hh_20ps_coast_sc.csv':
             ["restricted", 120, 20, "yes"],
         'restricted_140hh_20ps_coast/restricted_140hh_20ps_coast_sc.csv':
             ["restricted", 140, 20, "yes"],
         'restricted_160hh_20ps_coast/restricted_160hh_20ps_coast_sc.csv':
             ["restricted", 160, 20, "yes"],
         'restricted_120hh_150ps_nocoast/restricted_120hh_150ps_nocoast_sc.csv':
             ["restricted", 120, 150, "no"],
         'restricted_140hh_150ps_nocoast/restricted_140hh_150ps_nocoast_sc.csv':
             ["restricted", 140, 150, "no"],
         'restricted_160hh_150ps_nocoast/restricted_160hh_150ps_nocoast_sc.csv':
             ["restricted", 160, 150, "no"],
         'restricted_120hh_20ps_nocoast/restricted_120hh_20ps_nocoast_sc.csv':
             ["restricted", 120, 20, "no"],
         'restricted_140hh_20ps_nocoast/restricted_140hh_20ps_nocoast_sc.csv':
             ["restricted", 140, 20, "no"],
         'restricted_160hh_20ps_nocoast/restricted_160hh_20ps_nocoast_sc.csv':
             ["restricted", 180, 20, "no"]
         }
    }
}

    
with open("review_config.json", "w") as file:
    file.write(json.dumps(config_template, indent=4))
