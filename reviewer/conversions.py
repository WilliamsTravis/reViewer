#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversion functions for reV outputs.

Created on Fri May 29 22:15:54 2020

@author: travis
"""

import multiprocessing as mp
import os

import dask.array as da
import dask.dataframe as dd
import geopandas as gpd
import h5py
import numpy as np
import pandas as pd
import xarray as xr

from geocube.api.core import make_geocube
from dask.distributed import Client
from scipy.spatial import cKDTree
from shapely.geometry import Point
from tqdm import tqdm


NONDATA = ["meta", "time_index"]
ALBERS = ("+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 "
          "+ellps=GRS80 +datum=NAD83 +units=m no_defs")


def single_cube(arg):
    """
    

    Parameters
    ----------
    arg : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    sdf, res = arg
    sdf = make_geocube(sdf, resolution=res)

    return sdf


def par_cube(gdf, res, ncpu=os.cpu_count()):
    """
    

    Parameters
    ----------
    gdf : TYPE
        DESCRIPTION.
    resolution : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    gdfs = np.array_split(gdf, ncpu)
    args = [(df, res) for df in gdfs]
    ncs = []
    with mp.Pool(ncpu) as pool:
        for sdf in tqdm(pool.imap(single_cube, args), total=ncpu):
            ncs.append(sdf)

    return ncs


def par_apply(df, fun, axis, ncpu):
    """
    Apply a function to an axis of a pandas data set in parallel. 

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    fun : TYPE
        DESCRIPTION.
    axis : TYPE
        DESCRIPTION.
    ncpu : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    Sampel Arguments
    ----------------
    fun = to_point
    axis = 1
    ncpu = os.cpu_count()
    """

    dfs = []
    args = np.array_split(df, ncpu)
    with mp.Pool(ncpu) as pool:
        for sdf in pool.imap(fun, args):
            dfs.append(sdf)
    df = pd.concat(dfs)

    return df


def to_point(row):
    """Make a point out of each row of a pandas data frame."""
    return Point((row["lon"], row["lat"]))


def to_geo(df):
    """
    Create a GeoDataFrame out of a Pandas Data Frame with coordinates.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Pandas data frame with lat/lon coordinates.

    Returns
    -------
    gdf:
        geopandas.
    """

    # Coordinate could be any of these
    lons = ["longitude", "lon", "long",  "x"]
    lats = ["latitude", "lat", "y"]

    # Make sure everything is lower case
    df.columns = [c.lower() for c in df.columns]
    df.columns = [c if c not in lons else "lon" for c in df.columns ]
    df.columns = [c if c not in lats else "lat" for c in df.columns ]

    # Now make a point out of each row and creat the geodataframe
    df["geometry"] = df.apply(to_point, axis=1)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="epsg:4326")

    return gdf



def to_grid(df, res):
    """
    Convert coordinates from an irregular point dataset into an even grid.

    Parameters
    ----------
    df : pandas.core.Frame.DataFrame
        A pandas data frame with x/y coordinates.
    res: int | float
        The x and y resolution of the target grid.

    Returns
    -------
    pandas.core.Frame.DataFrame
    """

    # At the end of this the actual data will be inbetween these columns
    non_values = ["lat", "lon", "y", "x", "geometry", "gx", "gy", "ix", "iy"]

    # Get the extent
    minx = df["x"].min()
    miny = df["y"].min()
    maxx = df["x"].max()
    maxy = df["y"].max()

    # Estimate target grid coordinates
    gridx = np.arange(minx, maxx + res, res)
    gridy = np.arange(miny, maxy + res, res)
    grid_points = np.array(np.meshgrid(gridy, gridx)).T.reshape(-1, 2)

    # Get source points
    pdf = df[["y" ,"x"]]
    points = pdf.values

    # Build kdtree (watch out for repeats)
    ktree = cKDTree(grid_points)
    dist, indices = ktree.query(points)

    # Those indices associate grid point locations of the original point
    df["gx"] = grid_points[indices, 1]
    df["gy"] = grid_points[indices, 0]

    # And these indices indicate the 2D cartesion coordinates of theses points
    df["ix"] = df["gx"].apply(lambda x: np.where(gridx == x)[0][0])
    df["iy"] = df["gy"].apply(lambda x: np.where(gridy == x)[0][0])

    # Now we want just the values from the data frame, no coordinates
    value_cols = [c for c in df.columns if c not in non_values]
    values = df[value_cols].values

    # Okay, now use this to create our #D empty target grid
    grid = np.zeros((gridy.shape[0], gridx.shape[0], values.shape[1])) - 9999

    # Now, use the cartesian indices to add the values to the new grid
    grid[df["iy"].values, df["ix"].values, :] = values
    grid[grid == -9999] = np.nan

    # Holy cow, did that work?
    return grid, grid_points



def to_netcdf(file):
    """Covert a point data frame into a 3D gridded dataset.

    Parameters
    ----------
    file : str
        Path to an HDF5 or csv reV output file.


    Sample Arguments:
    ----------------
    file = "/home/travis/github/reViewer/data/ipm_wind_cfp_fl_2012.h5"
    """

    # Open dataset and build data frame (watch memory)
    datasets = {}
    with h5py.File(file, "r") as ds:
        keys = list(ds.keys())
        if "meta" in keys:
            crds = pd.DataFrame(ds["meta"][:])
        elif "coordinates" in datasets:
            crds = pd.DataFrame(ds["coordinates"][:])
        elif "latitude" in datasets:
            lats = pd.DataFrame(ds["latitude"][:])
            lons = pd.DataFrame(ds["longitude"][:])
            crds = pd.merge(lats, lons)
        else:
            raise ValueError("No coordinate data found in " + file)

        crds["gid"] = crds.index
        crds = crds[["latitude", "longitude", "gid"]]
        time = [t.decode() for t in ds["time_index"][:]]
        keys = [k for k in ds.keys() if k not in NONDATA]
        for k in keys:
            df = pd.DataFrame(ds[k][:])
            df.index = time
            df.columns = crds["gid"].values
            df = df.T
            df = crds[["latitude", "longitude"]].join(df)  
            datasets[k] = df

    # Create geo data frame so we can reproject
    df = to_geo(df)

    # Reproject so we can use a consistent grid bin size  # <------------------ Find a way to use a custom CRS?
    df = df.to_crs(ALBERS)
    df["x"] = df["geometry"].apply(lambda x: x.x)
    df["y"] = df["geometry"].apply(lambda x: x.y)

    # With geocube?
    # cube_dfs = par_cube(df, res=(2100, 2100))  # <----------------------------- This comes out in an unfortunate format

    # With custom rounding function?
    grid, coords = to_grid(df, res=2100)



def resamples(file, n):
    """Resample a gridded dataset to n resolutions.

    Parameters
    ----------
    file : str
        Path to an HDF5 or csv reV output file.
    n : int
        The number of different resolutions in which to resample the file.

    Returns
    -------
    list
        A list of paths to output files.
    
    Sample Arguments
    ----------------
    file = "/home/travis/github/reViewer/data/ipm_wind_cfp_fl_2012.nc"
    n = 6
    """

    # Expand path
    file = os.path.expanduser(file)


    # Open highest resolution original file    
    ds = xr.open_dataset(file)



def main(file, outdir=None):
    """Take an HDF5 or csv reV output (or perhaps a resource file), grid it
    into an NC file, take that and resample into 4-5 progressively coarser
    resolutions, and write each to file. It might be more efficient for the
    scatter mapbox to save back to HDF5 format.

    file = "/home/travis/github/reViewer/data/ipm_wind_cfp_fl_2012.nc"
    """

    # The original output
    # df = 






