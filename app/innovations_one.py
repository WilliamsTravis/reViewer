# -*- coding: utf-8 -*-
"""Secret presentation specific slide #1

https://slides.com/twillia2/national-wind-innovations-2021

National Innovations, baseline case, LCOE


Created on Tue Jul  6 13:30:17 2021

@author: twillia2
"""
from scenario_page import *


# Default object for initial layout
PROJECT = "Transition"
DEFAULTS = Defaults(project=PROJECT,
                    scenario_a="scenario_02_sc.csv",
                    scenario_b="scenario_03_sc.csv"
                    )

layout = scenario_layout(DEFAULTS)
