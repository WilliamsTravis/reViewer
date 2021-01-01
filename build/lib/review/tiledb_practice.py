#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 20:55:55 2020

@author: travis
"""

import gdal
import tiledb
from tiledb import sql

from reviewer import Data_Path, To_Tiledb
from gdalmethods import gdal_options

# Set up Data Base
DP = Data_Path("~/github/reviewer/data")

# Sample files
h5 = DP.join("samples", "ipm_wind_cfp_fl_2012.h5")
csv = DP.join("samples", "outputs_sc.csv")
tif = DP.join("samples", "us_states_0_125.tif")
nc = DP.join("samples", "spei6.nc")
tdb = DP.join("samples", "spei6_tbd")

# Using API
maker = To_Tiledb("test", DP.join("tbdbs"))
path1 = maker.netcdf(nc, overwrite=True)

# Using GDAL
ops = dict(format="tiledb")
src = gdal.Open(nc)
path2 = DP.join("tbdbs", "test2")
gdal.Translate(destName=path2, srcDS=src, **ops)

test1 = tiledb.DenseArray(path1)
test2 = tiledb.DenseArray(path2)
