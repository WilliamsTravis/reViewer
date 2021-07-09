# -*- coding: utf-8 -*-
"""Secret presentation pages.

https://slides.com/twillia2/national-wind-innovations-2021

Created on Tue Jul  6 13:30:17 2021

@author: twillia2
"""
from review.support import Defaults
from layouts import scenario_layout
# from scenario_page import *


# Default object for initial layout
def innovation_layouts():
    """Build a list of layouts for our innovation presenation slides."""
    # 1 - Most Baseline Turbine  
    defaults1 = Defaults(
        project="Transition",
        scenario_a="scenario_01_sc.csv",
    )

    # 2 - Most Advanced Turbine
    defaults2 = Defaults(
        project="Transition",
        scenario_a="scenario_44_sc.csv",
    )

    # 3 - Least Cost All
    defaults3 = Defaults(
        project="Transition",
        scenario_a="least_cost_by_mean_lcoe_all_sc.csv"
    )

    # 4 - Diff Least Cost Baseline vs Least Cost All (or advanced?)

    # 5 - Least-Cost Scenario Choices (scenario number first)

    # 6 - Least-Cost Explanations (ws first)

    # 7 - Lower FCR

    layout1 = scenario_layout(defaults1)
    layout2 = scenario_layout(defaults2)
    layout3 = scenario_layout(defaults3)

    layouts = {
        "/innovations_one": layout1,
        "/innovations_two": layout2,
        "/innovations_three": layout3,

    }

    return layouts
