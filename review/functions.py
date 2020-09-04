#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for reViewer.

Created on Sun Mar  8 16:12:01 2020

@author: travis
"""

import inspect
import os

from glob import glob


# FUNCTIONS
def h5_to_df(file, dataset):
    """Convert h5 dataset to dataframe."""


def print_args(func, *args):
    """Print a functions key word argument inputs for easy assignment."""
    print("\nARGUMENTS for " + func.__name__ + ":")
    sig = inspect.signature(func)
    keys = sig.parameters.keys()
    kwargs = dict(zip(keys, args))
    for key, arg in kwargs.items():
        if isinstance(arg, str):
            arg = "'" + arg + "'"
        print("  {} = {}".format(key, arg))
    print("\n")


# def value_map(data_path, agg="mean"):
#     """Convert a 2 or 3D NetCDF file to a 2D pandas data frame of points.

#     This will need to select a particular dataset, maybe aggregate by a
#     function, and filter and mask given a set of spatial and/or temporal
#     indices. We'll also need a scale factor and a nodata number.
#     """
#     with xr.open_dataset(data_path) as ds:
#         data = ds["value_" + agg]

#     df = data.to_dataframe()
#     df.reset_index(inplace=True)
#     df = df[~pd.isnull(df["value_" + agg])]

#     return df


# CLASSES
class Data_Path:
    """Data_Path joins a root directory path to data file paths."""

    def __init__(self, data_path):
        """Initialize Data_Path."""
        self.data_path = data_path
        self._expand_check()
        self._exist_check()

    def __repr__(self):
        """Print object representation string."""
        items = ["=".join([str(k), str(v)]) for k, v in self.__dict__.items()]
        arguments = " ".join(items)
        msg = "".join(["<Data_Path " + arguments + ">"])
        return msg

    def join(self, *args):
        """Join a file path to the root directory path."""
        return os.path.join(self.data_path, *args)

    def contents(self, *args):
        """List all content in the data_path or in sub directories."""
        if not any(["*" in a for a in args]):
            items = glob(self.join(*args, "*"))
        else:
            items = glob(self.join(*args))
        return items

    def folders(self, *args):
        """List folders in the data_path or in sub directories."""
        items = self.contents(*args)
        folders = [i for i in items if os.path.isdir(i)]
        return folders

    def files(self, *args):
        """List files in the data_path or in sub directories."""
        items = self.contents(*args)
        folders = [i for i in items if os.path.isfile(i)]
        return folders

    def _expand_check(self):
        # Expand the user path if a tilda is present in the root folder path.
        if "~" in self.data_path:
            self.data_path = os.path.expanduser(self.data_path)

    def _exist_check(self):
        # Make sure path exists
        os.makedirs(self.data_path, exist_ok=True)


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
