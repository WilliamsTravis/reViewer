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

