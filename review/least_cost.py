#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Least Cost methods.

We need to be able to calculate a least cost data frame for any number of
supply curve data frames for any number of different shapes.

When finding the least cost entry between data frames of different shapes,
it is important that they were developed with the same extent and aggregation
factor.

Created on Wed Feb 10 15:11:10 2021

@author: travis
"""
import os
import time

import numpy as np
import pandas as pd
import pathos.multiprocessing as mp

from tqdm import tqdm


class Least_Cost:
    """Class to handle various elements of calculating a least cost table."""

    def least_cost(self, dfs, by="total_lcoe"):
        """Return a single df from a list of same-shaped dfs."""
        # Unpack arguments and retrieve the proper field from each df
        value_list = [df[by].values for df in dfs]

        # Stack these together and find the indices of the smallest value
        values = np.stack(value_list)
        df_indices = np.argmin(values, axis=0)

        # Extract the row of the smallest value from each df
        row_indices = [np.where(df_indices == i)[0] for i in range(len(dfs))]
        dfs = [dfs[i].iloc[idx] for i, idx in enumerate(row_indices)]

        # Concatenate this into a single data frame
        df = pd.concat(dfs)
        return df

    def _retrieve(self, path):
        """Retrieve a single data frame."""
        scenario = os.path.basename(path).replace(".csv", "")
        df = pd.read_csv(path, low_memory=False)
        df["scenario"] = scenario
        time.sleep(0.2)
        return df

    def calc(self, paths, dst,by="total_lcoe"):
        """Build the single least cost table from a list of tables."""
        # Not including an overwrite option for now
        if os.path.exists(dst):
            print(f"{dst} exists.")
            return

        # Collect all data frames - biggest lift of all
        paths.sort()
        dfs = []
        with mp.Pool(10) as pool:
            for df in tqdm(pool.imap(self._retrieve, paths), total=len(paths)):
                dfs.append(df)

        # Make one big data frame
        bdf = pd.concat(dfs)
        bdf = bdf.reset_index(drop=True)

        # Group, find minimum, and subset
        idx = bdf.groupby("sc_point_gid")[by].idxmin()
        fdf = bdf.iloc[idx]
        fdf.to_csv(dst, index=False)

