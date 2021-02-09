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


# CLASSES
class Data_Path:
    """Data_Path joins a root directory path to data file paths."""

    def __init__(self, data_path, mkdir=False):
        """Initialize Data_Path."""
        data_path = os.path.abspath(os.path.expanduser(data_path))
        self.data_path = data_path
        self.last_path = os.getcwd()
        self._exist_check(data_path, mkdir)
        self._expand_check()

    def __repr__(self):
        """Print the data path."""
        items = ["=".join([str(k), str(v)]) for k, v in self.__dict__.items()]
        arguments = " ".join(items)
        msg = "".join(["<Data_Path " + arguments + ">"])
        return msg

    def join(self, *args, mkdir=False):
        """Join a file path to the root directory path."""
        path = os.path.join(self.data_path, *args)
        self._exist_check(path, mkdir)
        return path

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

    def files(self, pattern=None, *args):
        """List files in the data_path or in sub directories."""
        items = self.contents(*args)
        files = [i for i in items if os.path.isfile(i)]
        if pattern:
            files = [f for f in files if pattern in f]
            if len(files) == 1:
                files = files[0]
        return files

    @property
    def home(self):
        """Change directories to the data path."""
        self.last_path = os.getcwd()
        os.chdir(self.data_path)
        print(self.data_path)

    @property
    def back(self):
        """Change directory back to last working directory if home was used."""
        os.chdir(self.last_path)
        print(self.last_path)

    def _exist_check(self, path, mkdir=False):
        """Check if the directory of a path exists, and make it if not."""
        # If this is a file name, get the directory
        if "." in os.path.basename(path):
            directory = os.path.dirname(path)
        else:
            directory = path

        # Don't try this with glob patterns
        if "*" not in directory:
            if not os.path.exists(directory):
                if mkdir:
                    print("Warning: " + directory + " did not exist, creating "
                          "directory.")
                    os.makedirs(directory, exist_ok=True)
                else:
                    print("Warning: " + directory + " does not exist.")

    def _expand_check(self):
        # Expand the user path if a tilda is present in the root folder path.
        if "~" in self.data_path:
            self.data_path = os.path.expanduser(self.data_path)




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
