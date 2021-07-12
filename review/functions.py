# -*- coding: utf-8 -*-
"""Functions for reView.

Created on Sun Mar  8 16:12:01 2020

@author: travis
"""
import datetime as dt
import inspect
import os
import requests

from glob import glob

import pandas as pd


# FUNCTIONS
def print_args(func, *args, **kwargs):
    """Print a functions key word argument inputs for easy assignment."""
    print("\nARGUMENTS for " + func.__name__ + ":")
    sig = inspect.signature(func)
    keys = sig.parameters.keys()
    if kwargs:
        kwargs = {**dict(zip(keys, args)), **kwargs}
    else:
        kwargs = dict(zip(keys, args))
    for key, arg in kwargs.items():
        if isinstance(arg, str):
            arg = "'" + arg + "'"
        print("  {} = {}".format(key, arg))
    print("\n")


class LBNL:
    """Class for handling the retrieval and reformatting of LBNL atasets."""

    def __init__(self, home="~/.lbnl"):
        """Initialize LBNL class object.

        Parameters
        ----------
        home : str
            The path to the local directory in which to store files.
        """
        self.home = home
        self.url = "https://eersc.usgs.gov/api/uswtdb/v1/turbines"

    def retrieve(self, version=None, fname="lbnl_uswtdb_{}.csv"):
        """Retrieve the LBNL Wind Turbine database.

        Parameters
        ----------
        version : int | str
            The version of the dataset to retrieve. Default of None results
            in the most recent version.
        path : str
            The file name to assign to the retrieved dataset. Will default to
            a string containing the year and version number.

        Returns
        -------
        str
            Path to resulting csv file.
        """
        response = requests.get(self.url, stream=True)
        dst = self._build_dst(response, fname)
        if not os.path.exists(dst):
            df = pd.DataFrame(response.json())
            df.to_csv(dst, index=False)
        return dst

    # def supply_curve(self, resolution=128):
    #     """Build a supply curve table with existing wind turbine features."""
    #     dst = self.retrieve()

    def _build_dst(self, response, fname):
        """Build the file path from a request and file name template."""
        home = os.path.expanduser(self.home)
        os.makedirs(home, exist_ok=True)
        date_str = " ".join(response.headers["Date"].split()[1: 4])
        date = dt.datetime.strptime(date_str, "%d %b %Y")
        date_str = date.strftime("%Y_%m_%d")
        dst = fname.format(date_str)
        return dst


# class To_Tiledb:
#     """Convert a spatially referenced dataset to a tiledb array data base."""

#     def __init__(self, name, db_dir="./"):
#         """Inititalize a TileDB file converter.
        
#         Parameters
#         ----------
#         name : str
#             The name of the data base to create/add to.
#         db_dir : str, optional
#             The directory containing the data base files. The default is
#             "./database".
#         """
#         self.name = name
#         self.db_dir = db_dir

#     def __repr__(self):

#         attrs = ["{}='{}'".format(k, v) for k, v in self.__dict__.items()]
#         attrs_str = " ".join(attrs)
#         msg = "<To_Tiledb {}> ".format(attrs_str)
#         return msg

#     def hdf(self, file):
#         """Import an HDF file to the tildb database.

#         Parameters
#         ----------
#         file : str
#             Path to an HDF file.

#         Returns
#         -------
#         None.
#         """

#     def netcdf(self, file, overwrite=False):
#         """Import an NetCDF file to the tildb database.

#         Parameters
#         ----------
#         file : str
#             Path to an NetCDF file.

#         Returns
#         -------
#         str
#             Path to data frame files.

#         Sample Arguments
#         ----------------
#         file = '/home/travis/github/reviewer/data/samples/spei6.nc'
#         """
    
#         # Target path
#         output = Data_Path(self.db_dir).join(self.name)

#         if overwrite:
#             if os.path.exists(output):
#                 shutil.rmtree(output)
#         else:
#             if os.path.exists(output):
#                 print(output + " exists, use overwrite=True.")
#                 return output

#         # Get meta data
#         profile = self._raster_profile(file)
 
#         # Open dask/xarray 
#         chunks = {"band": profile["count"], "x": profile["width"], # Automate this
#                   "y": profile["height"]}
#         array = xr.open_rasterio(file, chunks=chunks)

#         # Get the partition sizes for each dimension
#         count = profile["count"]
#         height = profile["height"]
#         width = profile["width"]
#         zdomain = (0, profile["count"] - 1)
#         ydomain = (0, profile["height"] - 1)
#         xdomain = (0, profile["width"] - 1)

#         # Create the domain
#         zdim = tiledb.Dim(name='BANDS', domain=zdomain, tile=count, dtype=np.uint32)
#         ydim = tiledb.Dim(name='Y', domain=ydomain, tile=height, dtype=np.uint32)
#         xdim = tiledb.Dim(name='X', domain=xdomain, tile=width, dtype=np.uint32)
#         domain = tiledb.Domain(zdim,  ydim, xdim)

#         # Create the schema
#         attrs = [tiledb.Attr(name='values', dtype=profile["dtype"])]
#         schema = tiledb.ArraySchema(domain=domain, sparse=False, attrs=attrs)
       
#         # Initialize the database
#         tiledb.DenseArray.create(output, schema)

#         # Write the data array to the database  <------------------------------ Why does this create such an enormous file?
#         with tiledb.DenseArray(output, 'w') as arr_output:
#             array.data.to_tiledb(arr_output)

#         # return output
#         return output
    
    
#     def _raster_profile(self, file):
#         """Generate meta data for a rasterio accessible file."""

#         # Open file
#         with rasterio.open(file) as nc:
#             profile = nc.profile
#             dtype = np.dtype(nc.dtypes[0])
            
#         # Reset the driver to tiledb
#         profile["driver"] = "TileDB"

#         # Get the numpy version of this dtype
#         profile["dtype"] = dtype

#         # Our target chunk size
#         tile_size = 1024.0

#         # Get chunk number of chunks
#         w = profile["width"]
#         h = profile["height"]
#         z = profile["count"]
#         profile["blocks"] = {}
#         profile["blocks"]["band"] = math.ceil(z / tile_size)        
#         profile["blocks"]["x"] = math.ceil(w / tile_size)
#         profile["blocks"]["y"] = math.ceil(h / tile_size)

#         return profile
