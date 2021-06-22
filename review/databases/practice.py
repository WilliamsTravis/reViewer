
# -*- coding: utf-8 -*-
"""Practicing postgres-python interactions.

Created on Sun Jun 20 12:21:00 2021

@author: travis
"""
import os

import numpy as np
import pandas as pd
import psycopg2 as pg
import sqlalchemy as sql

from review.databases.postgres import config


TABLE = "/home/travis/nrel/review_datasets/atb/00_na_n_current_sc.csv"
CONFIG = "~/github/reView/review/databases/database.ini"


class ReviewDB:

    @property
    def db(self):
        """Connect to data base and read csv in as a table."""
        # Get our database info
        c = config(os.path.expanduser(CONFIG))
        db = c["database"]
        host = c["host"]
        port = c["port"]
        pw = c["password"]
        user = c["user"]
    
        # Build our connection address
        url = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}"
    
        # And create the engine
        db = sql.create_engine(url)

        return db

    def columns(self, name):
        """Return column names for table."""
        cmd = ("select column_name from information_schema.columns where "
                f"table_name = '{name}';")
        return [c[0] for c in self.query(cmd)]

    def query(self, cmd):
        """Return the results of a table query."""
        r = self.db.execute(cmd)
        return r.fetchall()

    def upload(self, path):
        """Upload a CSV to the database."""
        # Translate these into postgres datatypes
        name = self._name(path)
        df = pd.read_csv(path, low_memory=False)        
        df.to_sql(name, self.db, if_exists="replace", method="multi")

    def fdata(self, name, col, op, value):
        """Just playing around with different ways to filter the dataframe."""
        cmd = f"select * from {name} where {col} {op} {value};"
        df = pd.DataFrame(self.query(cmd))
        cols = self.columns(self._name(path))
        df.columns = cols
        return df
    
    def _name(self, path):
        """Return the db name for a CSV file."""
        name = os.path.basename(path.replace(".csv", ""))
        name = name[2:]  # I don't think tables can start with a number, that sucks
        return "test"


def timing():
    """Curious to see if pg is faster than pandas."""
    path = TABLE

    col = "mean_lcoe"
    value = 40

    q = f"select * from test where {col} < {value};"

    db = ReviewDB()
    
    # %timeit df1 = pd.read_csv(TABLE); df1[df1[col] < value]
    # %timeit db.query(q)


if __name__ == "__main__":
    path = TABLE
    self = ReviewDB()
    