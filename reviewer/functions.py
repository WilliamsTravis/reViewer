#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions for reViewer.

Created on Sun Mar  8 16:12:01 2020

@author: travis
"""

import math
import numpy as np
import os
import rasterio
import shutil
import tiledb
import xarray as xr


# CLASSES
class Data_Path:
    """Data_Path joins a root directory path to data file paths."""

    def __init__(self, folder_path):
        """Initialize Data_Path."""

        self.folder_path = folder_path
        self._check_all()

    def join(self, *args):
        """Join a file path to the root directory path"""

        return os.path.join(self.folder_path, *args)

    def _check_all(self):

        # Expand the user path if a tilda is present in the folder path.
        if "~" in self.folder_path:
            self.folder_path = os.path.expanduser(self.folder_path)

        # Make sure the this path exists
        os.makedirs(self.folder_path, exist_ok=True)


class To_Tiledb:
    """Convert a spatially referenced dataset to a tiledb array data base."""

    def __init__(self, name, db_dir="./"):
        """Inititalize a TileDB file converter.
        
        Parameters
        ----------
        name : str
            The name of the data base to create/add to.
        db_dir : str, optional
            The directory containing the data base files. The default is
            "./database".
        """
        self.name = name
        self.db_dir = db_dir

    def __repr__(self):

        attrs = ["{}='{}'".format(k, v) for k, v in self.__dict__.items()]
        attrs_str = " ".join(attrs)
        msg = "<To_Tiledb {}> ".format(attrs_str)
        return msg

    def hdf(self, file):
        """Import an HDF file to the tildb database.

        Parameters
        ----------
        file : str
            Path to an HDF file.

        Returns
        -------
        None.
        """

    def netcdf(self, file, overwrite=False):
        """Import an NetCDF file to the tildb database.

        Parameters
        ----------
        file : str
            Path to an NetCDF file.

        Returns
        -------
        str
            Path to data frame files.

        Sample Arguments
        ----------------
        file = '/home/travis/github/reviewer/data/samples/spei6.nc'
        """
    
        # Target path
        output = Data_Path(self.db_dir).join(self.name)

        if overwrite:
            if os.path.exists(output):
                shutil.rmtree(output)
        else:
            if os.path.exists(output):
                print(output + " exists, use overwrite=True.")
                return output

        # Get meta data
        profile = self._raster_profile(file)
 
        # Open dask/xarray 
        chunks = {"band": profile["count"], "x": profile["width"], # Automate this
                  "y": profile["height"]}
        array = xr.open_rasterio(file, chunks=chunks)

        # Get the partition sizes for each dimension
        count = profile["count"]
        height = profile["height"]
        width = profile["width"]
        zdomain = (0, profile["count"] - 1)
        ydomain = (0, profile["height"] - 1)
        xdomain = (0, profile["width"] - 1)

        # Create the domain
        zdim = tiledb.Dim(name='BANDS', domain=zdomain, tile=count, dtype=np.uint32)
        ydim = tiledb.Dim(name='Y', domain=ydomain, tile=height, dtype=np.uint32)
        xdim = tiledb.Dim(name='X', domain=xdomain, tile=width, dtype=np.uint32)
        domain = tiledb.Domain(zdim,  ydim, xdim)

        # Create the schema
        attrs = [tiledb.Attr(name='values', dtype=profile["dtype"])]
        schema = tiledb.ArraySchema(domain=domain, sparse=False, attrs=attrs)
       
        # Initialize the database
        tiledb.DenseArray.create(output, schema)

        # Write the data array to the database  <------------------------------ Why does this create such an enormous file?
        with tiledb.DenseArray(output, 'w') as arr_output:
            array.data.to_tiledb(arr_output)

        # return output
        return output
    
    
    def _raster_profile(self, file):
        """Generate meta data for a rasterio accessible file."""

        # Open file
        with rasterio.open(file) as nc:
            profile = nc.profile
            dtype = np.dtype(nc.dtypes[0])
            
        # Reset the driver to tiledb
        profile["driver"] = "TileDB"

        # Get the numpy version of this dtype
        profile["dtype"] = dtype

        # Our target chunk size
        tile_size = 1024.0

        # Get chunk number of chunks
        w = profile["width"]
        h = profile["height"]
        z = profile["count"]
        profile["blocks"] = {}
        profile["blocks"]["band"] = math.ceil(z / tile_size)        
        profile["blocks"]["x"] = math.ceil(w / tile_size)
        profile["blocks"]["y"] = math.ceil(h / tile_size)

        return profile
    


