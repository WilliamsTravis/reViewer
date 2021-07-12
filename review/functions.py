# -*- coding: utf-8 -*-
"""Functions for reView.

Created on Sun Mar  8 16:12:01 2020

@author: travis
"""
import datetime as dt
import inspect
import json
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


# CLASSES
class Data_Path:
    """Data_Path joins a root directory path to data file paths."""

    def __init__(self, data_path=".", mkdir=False, warnings=True):
        """Initialize Data_Path."""
        data_path = os.path.abspath(os.path.expanduser(data_path))
        self.data_path = data_path
        self.last_path = os.getcwd()
        self.warnings = warnings
        self._exist_check(data_path, mkdir)
        self._expand_check()

    def __repr__(self):
        """Print the data path."""
        items = ["=".join([str(k), str(v)]) for k, v in self.__dict__.items()]
        arguments = ", ".join(items)
        msg = "".join(["<Data_Path " + arguments + ">"])
        return msg

    def contents(self, *args, recursive=False):
        """List all content in the data_path or in sub directories."""
        if not any(["*" in a for a in args]):
            items = glob(self.join(*args, "*"), recursive=recursive)
        else:
            items = glob(self.join(*args), recursive=recursive)
        return items

    def folders(self, *args, recursive=False):
        """List folders in the data_path or in sub directories."""
        items = self.contents(*args, recursive=recursive)
        folders = [i for i in items if os.path.isdir(i)]
        return folders

    def files(self, *args, recursive=False):
        """List files in the data_path or in sub directories."""
        items = self.contents(*args, recursive=recursive)
        files = [i for i in items if os.path.isfile(i)]
        return files

    def join(self, *args, mkdir=False):
        """Join a file path to the root directory path."""
        path = os.path.join(self.data_path, *args)
        self._exist_check(path, mkdir)
        path = os.path.abspath(path)
        return path

    @property
    def base(self):
        """Return the base name of the home directory."""
        return os.path.basename(self.data_path)

    @property
    def back(self):
        """Change directory back to last working directory if home was used."""
        os.chdir(self.last_path)
        print(self.last_path)

    @property
    def home(self):
        """Change directories to the data path."""
        self.last_path = os.getcwd()
        os.chdir(self.data_path)
        print(self.data_path)

    def extend(self, path, mkdir=False):
        """Return a new Data_Path object with an extended home directory."""
        new = Data_Path(os.path.join(self.data_path, path), mkdir)
        return new

    def _exist_check(self, path, mkdir=False):
        """Check if the directory of a path exists, and make it if not."""
        # If this is a file name, get the directory
        if "." in path:  # Will break if you use "."'s in your directories
            directory = os.path.dirname(path)
        else:
            directory = path

        # Don't try this with glob patterns
        if "*" not in directory:
            if not os.path.exists(directory):
                if mkdir:
                    if self.warnings:
                        print(f"Warning: {directory} did not exist, "
                              "creating directory.")
                    os.makedirs(directory, exist_ok=True)
                else:
                    if self.warnings:
                        print(f"Warning: {directory} does not exist.")

    def _expand_check(self):
        # Expand the user path if a tilda is present in the root folder path.
        if "~" in self.data_path:
            self.data_path = os.path.expanduser(self.data_path)


@pd.api.extensions.register_dataframe_accessor("rr")
class PandasExtension:
    """Accessing useful pandas functions directly from a data frame object."""

    import warnings

    from json import JSONDecodeError

    import geopandas as gpd
    import pandas as pd
    import numpy as np

    from scipy.spatial import cKDTree
    from shapely.geometry import Point

    def __init__(self, pandas_obj):
        """Initialize PandasExtension object."""
        self.warnings.simplefilter(action='ignore', category=UserWarning)
        if type(pandas_obj) != self.pd.core.frame.DataFrame:
            if type(pandas_obj) != self.gpd.geodataframe.GeoDataFrame:
                raise TypeError("Can only use .rr accessor with a pandas or "
                                "geopandas data frame.")
        self._obj = pandas_obj

    def average(self, value, weight="n_gids", group=None):
        """Return the weighted average of a column.

        Parameters
        ----------
        value : str
            Column name of the variable to calculate.
        weight : str
            Column name of the variable to use as the weights. The default is
            'n_gids'.
        group : str, optional
            Column name of the variable to use to group results. The default is
            None.

        Returns
        -------
        dict | float
            Single value or a dictionary with group, weighted average value
            pairs.
        """
        df = self._obj.copy()
        if not group:
            values = df[value].values
            weights = df[weight].values
            x = self.np.average(values, weights=weights)
        else:
            x = {}
            for g in df[group].unique():
                gdf = df[df[group] == g]
                values = gdf[value].values
                weights = gdf[weight].values
                x[g] = self.np.average(values, weights=weights)
        return x

    def bmap(self):
        """Show a map of the data frame with a basemap if possible."""
        if not isinstance(self._obj, self.gpd.geodataframe.GeoDataFrame):
            print("Data frame is not a GeoDataFrame")

    def decode(self):
        """Decode the columns of a meta data object from a reV output."""
        import ast

        def decode_single(x):
            """Try to decode a single value, pass if fail."""
            try:
                x = x.decode()
            except UnicodeDecodeError:
                x = "indecipherable"
            return x

        for c in self._obj.columns:
            x = self._obj[c].iloc[0]
            if isinstance(x, bytes):
                try:
                    self._obj[c] = self._obj[c].apply(decode_single)
                except Exception:
                    self._obj[c] = None
                    print("Column " + c + " could not be decoded.")
            elif isinstance(x, str):
                try:
                    if isinstance(ast.literal_eval(x), bytes):
                        try:
                            self._obj[c] = self._obj[c].apply(
                                lambda x: ast.literal_eval(x).decode()
                                )
                        except Exception:
                            self._obj[c] = None
                            print("Column " + c + " could not be decoded.")
                except:
                    pass

    def dist_apply(self, linedf):
        """To apply the distance function in parallel (not ready)."""
        from pathos.multiprocessing import ProcessingPool as Pool
        from tqdm import tqdm

        # Get distances
        ncpu = os.cpu_count()
        chunks = self.np.array_split(self._obj.index, ncpu)
        args = [(self._obj.loc[idx], linedf) for idx in chunks]
        distances = []
        with Pool(ncpu) as pool:
            for dists in tqdm(pool.imap(self.point_line, args),
                              total=len(args)):
                distances.append(dists)
        return distances

    def find_coords(self):
        """Check if lat/lon names are in a pre-made list of possible names."""
        # List all column names
        df = self._obj.copy()
        cols = df.columns

        # For direct matches
        ynames = ["y", "lat", "latitude", "Latitude", "ylat"]
        xnames = ["x", "lon", "long", "longitude", "Longitude", "xlon",
                  "xlong"]

        # Direct matches
        possible_ys = [c for c in cols if c in ynames]
        possible_xs = [c for c in cols if c in xnames]

        # If no matches return item and rely on manual entry
        if len(possible_ys) == 0 or len(possible_xs) == 0:
            raise ValueError("No field names found for coordinates, use "
                             "latcol and loncol arguments.")

        # If more than one match raise error
        elif len(possible_ys) > 1:
            raise ValueError("Multiple possible entries found for y/latitude "
                             "coordinates, use latcol argument: " +
                             ", ".join(possible_ys))
        elif len(possible_xs) > 1:
            raise ValueError("Multiple possible entries found for y/latitude "
                             "coordinates, use latcol argument: " +
                             ", ".join(possible_xs))

        # If there's just one column use that
        else:
            return possible_ys[0], possible_xs[0]

    def gid_join(self, df_path, fields, agg="mode", left_on="res_gids",
                 right_on="gid"):
        """Join a resource-scale data frame to a supply curve data frame.

        Parameters
        ----------
        df_path : str
            Path to csv with desired join fields.
        fields : str | list
            The field(s) in the right DataFrame to join to the left.
        agg : str
            The aggregating function to apply to the right DataFrame. Any
            appropriate numpy function.
        left_on : str
            Column name to join on in the left DataFrame.
        right_on : str
            Column name to join on in the right DataFrame.

        Returns
        -------
        pandas.core.frame.DataFrame
            A pandas DataFrame with the specified fields in the right
            DataFrame aggregated and joined.
        """
        from pathos.multiprocessing import ProcessingPool as Pool

        # The function to apply to each item of the left dataframe field
        def single_join(x, vdict, right_on, field, agg):
            """Return the aggregation of a list of values in df."""
            x = self._destring(x)
            rvalues = [vdict[v] for v in x]
            rvalues = [self._destring(v) for v in rvalues]
            rvalues = [self._delist(v) for v in rvalues]
            return agg(rvalues)

        def chunk_join(arg):
            """Apply single to a subset of the main dataframe."""
            chunk, df_path, left_on, right_on, field, agg = arg
            rdf = pd.read_csv(df_path)
            vdict = dict(zip(rdf[right_on], rdf[field]))
            chunk[field] = chunk[left_on].apply(single_join, args=(
                vdict, right_on, field, agg
                )
            )
            return chunk

        # Create a copy of the left data frame
        df1 = self._obj.copy()

        # Set the function
        if agg == "mode":
            def mode(x): max(set(x), key=x.count)
            agg = mode
        else:
            agg = getattr(self.np, agg)

        # If a single string is given for the field, make it a list
        if isinstance(fields, str):
            fields = [fields]

        # Split this up and apply the join functions
        chunks = self.np.array_split(df1, os.cpu_count())
        for field in fields:
            args = [(c, df_path, left_on, right_on, field, agg)
                    for c in chunks]
            df1s = []
            with Pool(os.cpu_count()) as pool:
                for cdf1 in pool.imap(chunk_join, args):
                    df1s.append(cdf1)
            df = pd.concat(df1s)

        return df

    def nearest(self, df, fields=None, lat=None, lon=None, no_repeat=False,
                k=5):
        """Find all of the closest points in a second data frame.

        Parameters
        ----------
        df : pandas.core.frame.DataFrame | geopandas.geodataframe.GeoDataFrame
            The second data frame from which a subset will be extracted to
            match all points in the first data frame.
        fields : str | list
            The field(s) in the second data frame to append to the first.
        lat : str
            The name of the latitude field.
        lon : str
            The name of the longitude field.
        no_repeat : logical
            Return closest points with no duplicates. For two points in the
            left dataframe that would join to the same point in the right, the
            point of the left pair that is closest will be associated with the
            original point in the right, and other will be associated with the
            next closest. (not implemented yet)
        k : int
            The number of next closest points to calculate when no_repeat is
            set to True. If no_repeat is false, this value is 1.

        Returns
        -------
        df : pandas.core.frame.DataFrame | geopandas.geodataframe.GeoDataFrame
            A copy of the first data frame with the specified field and a
            distance column.
        """
        # We need geodataframes
        df1 = self._obj.copy()
        original_type = type(df1)
        if not isinstance(df1, self.gpd.geodataframe.GeoDataFrame):
            df1 = df1.rr.to_geo(lat, lon)  # <--------------------------------- not necessary, could speed this up just finding the lat/lon columns, we'd also need to reproject for this to be most accurate.
        if not isinstance(df, self.gpd.geodataframe.GeoDataFrame):
            df = df.rr.to_geo(lat, lon)
            df = df.reset_index(drop=True)

        # What from the second data frame do we want to return?
        if fields:
            if isinstance(fields, str):
                fields = [fields]
        else:
            fields = [c for c in df if c != "geometry"]

        # Get arrays of point coordinates
        crds1 = self.np.array(
            list(df1["geometry"].apply(lambda x: (x.x, x.y)))
        )
        crds2 = self.np.array(
            list(df["geometry"].apply(lambda x: (x.x, x.y)))
        )

        # Build the connections tree and query points from the first df
        tree = self.cKDTree(crds2)
        if no_repeat:
            dist, idx = tree.query(crds1, k=k)
            dist, idx = self._derepeat(dist, idx)
        else:
            dist, idx = tree.query(crds1, k=1)

        # We might be relacing a column
        for field in fields:
            if field in df1:
                del df1[field]

        # Rebuild the dataset
        dfa = df1.reset_index(drop=True)
        dfb = df.iloc[idx, :]
        del dfb["geometry"]
        dfb = dfb.reset_index(drop=True)
        df = pd.concat([dfa, dfb[fields], pd.Series(dist, name='dist')],
                       axis=1)

        # If this wasn't already a geopandas data frame reformat
        if not isinstance(df, original_type):
            del df["geometry"]
            df = pd.DataFrame(df)

        return df

    def to_bbox(self, bbox):
        """Return points within a bounding box [xmin, ymin, xmax, ymax]."""
        df = self._obj.copy()
        df = df[(df["longitude"] >= bbox[0]) &
                (df["latitude"] >= bbox[1]) &
                (df["longitude"] <= bbox[2]) &
                (df["latitude"] <= bbox[3])]
        return df

    def to_geo(self, lat=None, lon=None):
        """Convert a Pandas data frame to a geopandas geodata frame."""
        # Let's not transform in place
        df = self._obj.copy()
        df.rr.decode()

        # Find coordinate columns
        if "geometry" not in df.columns:
            if "geom" not in df.columns:
                try:
                    lat, lon = self.find_coords()
                except ValueError:
                    pass

                # For a single row
                def to_point(x):
                    return self.Point(tuple(x))
                df["geometry"] = df[[lon, lat]].apply(to_point, axis=1)

        # Create the geodataframe - add in projections
        if "geometry" in df.columns:
            gdf = self.gpd.GeoDataFrame(df, crs='epsg:4326',
                                        geometry="geometry")
        if "geom" in df.columns:
            gdf = self.gpd.GeoDataFrame(df, crs='epsg:4326',
                                        geometry="geom")

        return gdf

    def to_sarray(self):
        """Create a structured array for storing in HDF5 files."""
        # Create a copy
        df = self._obj.copy()

        # For a single column
        def make_col_type(col, types):

            coltype = types[col]
            column = df.loc[:, col]

            try:
                if 'numpy.object_' in str(coltype.type):
                    maxlens = column.dropna().str.len()
                    if maxlens.any():
                        maxlen = maxlens.max().astype(int)
                        coltype = ('S%s' % maxlen)
                    else:
                        coltype = 'f2'
                return column.name, coltype
            except:
                print(column.name, coltype, coltype.type, type(column))
                raise

        # All values and types
        v = df.values
        types = df.dtypes
        struct_types = [make_col_type(col, types) for col in df.columns]
        dtypes = self.np.dtype(struct_types)

        # The target empty array
        array = self.np.zeros(v.shape[0], dtypes)

        # For each type fill in the empty array
        for (i, k) in enumerate(array.dtype.names):
            try:
                if dtypes[i].str.startswith('|S'):
                    array[k] = df[k].str.encode('utf-8').astype('S')
                else:
                    array[k] = v[:, i]
            except:
                raise

        return array, dtypes

    def _delist(self, value):
        """Extract the value of an object if it is a list with one value."""
        if isinstance(value, list):
            if len(value) == 1:
                value = value[0]
        return value

    # def _derepeat(dist, idx):
    #     """Find the next closest index for repeating cKDTree outputs."""  # <-- Rethink this, we could autmomatically set k tot he max repeats
    #     # Get repeated idx and counts
    #     k = idx.shape[1]
    #     uiidx, nrepeats = np.unique(idx, return_counts=True)
    #     max_repeats = nrepeats.max()
    #     if max_repeats > k:
    #         raise ValueError("There are a maximum of " + str(max_repeats) +
    #                          " repeating points, to use the next closest "
    #                          "neighbors to avoid repeats, set k to this "
    #                          "number.")

    #     for i in range(k - 1):
    #         # New arrays for this axis
    #         iidx = idx[:, i]
    #         idist = dist[:, i]

    def _destring(self, string):
        """Destring values into their literal python types if needed."""
        try:
            return json.loads(string)
        except (TypeError, self.JSONDecodeError):
            return string



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
