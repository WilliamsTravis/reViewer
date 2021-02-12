#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recalculate all of the LCOE figures with new FCR figures.

LCOE = (FCR * CAPEX + FOM)/(CF × 8,760)


This excludes Variable Operating Costs and fuel costs

Created on Thu Feb 11 14:14:32 2021

@author: twillia2
"""
import os

import pandas as pd

from review.support import Config


FCR = 0.072


def recalc():
    # Get a sample data frame
    config = Config("Transition").project_config
    fname = config["data"]["file"]["0"]
    scenario = fname.replace("_sc.csv", "")
    path = os.path.join(config["directory"], fname)
    df = pd.read_csv(path)

    # get a sample row
    sample = df.iloc[0]
    tlcoe = sample["total_lcoe"]
    slcoe = sample["mean_lcoe"]
    lcot = sample["lcot"]

    # Get the parameters for this guy
    params = config["parameters"][scenario]
    capacity = sample["capacity"] * 1000
    capex = params["Total Capex ($/kW)"] * capacity
    fom = params["Opex ($/kW/yr)"] * capacity
    cf = sample["mean_cf"]

    # Okay we know the denominator
    denominator = sample["mean_cf"] * 8760

    # And so we know the numerator
    numerator = slcoe * denominator

    # But we might still need to use the figures from the paramters
    lcoe = ((FCR * capex) + fom) / (cf * 8760)

    # Not quite, what are we missing?