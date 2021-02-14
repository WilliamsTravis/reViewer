#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 09:42:23 2021

@author: travis
"""

import cuxfilter
import cudf
df = cudf.read_parquet('./data/census_data.parquet/*')
#create cuxfilter dataframe
cux_df = cuxfilter.DataFrame.from_dataframe(df)
chart0 = cuxfilter.charts.scatter_geo(x='x', y='y')
chart1 = cuxfilter.charts.bar('age')
chart2 = cuxfilter.charts.bar('sex')
d = cux_df.dashboard([chart0, chart1, chart2], layout=cuxfilter.layouts.feature_and_double_base
)
d.show()