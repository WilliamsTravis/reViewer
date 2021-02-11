#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calculate difference between any two supply curve tables.

Created on Wed Feb 10 17:22:23 2021

@author: travis
"""
import os

import numpy as np
import pandas as pd


class Difference:
    """Class to handle supply curve difference calculations."""

    def difference(self, rows, field):
        """return the percent difference between two values."""
        row1 = rows.iloc[0]
        if rows.shape[0] == 1:
            pct = np.nan
        else:
            x1 = row1[field]
            x2 = rows.iloc[1][field]
            pct = (x1 / x2) * 100
        row1["difference"] = pct
        return row1

    def calc(self, df1, df2, field, dst):
        """Calculate difference between each row in two data frames."""
        if not os.path.exists(dst):
            df1 = df1[["sc_point_gid", "latitude", "longitude", field]]
            df2 = df2[["sc_point_gid", "latitude", "longitude", field]]
            df = pd.concat([df1, df2])
            df = df.sort_values("sc_point_gid").reset_index(drop=True)
            fdf = df.groupby("sc_point_gid").apply(self.difference, field=field)
            fdf.to_csv(dst, index=False)
