# -*- coding: utf-8 -*-
"""
The config function seems useful for automating the set up process. However,
with conda, at least, there does not appear to be a default database.ini file.
It might be true that there never is such a thing, so, regardless, it might be
necessary to create one. Therefore, I am creating a function to build an ini
file and initialize a database connection, using it to configure the database
connection with the tutorial script, and then connect to the database.

Created on Sun Aug  4 18:51:29 2019

@author: travis williams
"""
import os
import subprocess as sp
import time

from configparser import ConfigParser

import psycopg2 as pq
import site


# This is the python environment/ virtual environment
SQLENV = site.getsitepackages()[0]

# This is the database data folder
PGDATA = os.path.join(SQLENV, "pgdata")

# These are our environment variable paths
ENV = os.environ.copy()
USER = ENV["USERNAME"]
ENV["PGDATA"] = PGDATA


def initdb(database="review", password="testing"):
    """Initialize Postgres database."""
    # This ensures we have a database data folder
    if not os.path.exists(PGDATA):
        print("Creating postgres data folder")
        os.mkdir(PGDATA)

        # This initializes postgres and populates the pgdata folder
        r = sp.Popen(["pg_ctl", "initdb"], stderr=sp.STDOUT, stdout=sp.PIPE,
                     env=ENV)
        statement = str(r.stdout.read(), "utf-8").replace("\r", "")
        statement = statement.split("\n")
        for s in statement:    
            print(s)

        # This is the path to our postgres server configuration
        init_path = "database.ini"
    
        # And this ensures we have such a thing
        init = ConfigParser()
        init["postgresql"] = {"host": "localhost", "database": database,
                             "user": USER, "password": password}
        with open(init_path, "w") as file:
            init.write(file)

    r = sp.Popen(["pg_ctl", "start"], stderr=sp.STDOUT, stdout=sp.PIPE,
                 env=ENV)  
    statement = str(r.stdout.read(), "utf-8").replace("\r", "")
    statement = statement.split("\n")
    for s in statement:    
        print(s)


def config(filename="database.ini", section="postgresql"):
    """Return configurations from the ini file as a dictionary."""

    # create a parser
    parser = ConfigParser()

    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
                "Section {0} not found in the {1} file".format(section,
                                                               filename))
    return db


def connect():
    """Connect to postgres using database.ini configuration."""
    sp.Popen(["pg_ctl", "start"], stderr=sp.STDOUT, stdout=sp.PIPE, env=ENV)  
    conn = None
    try:
        # read connection parameters
        params = config()
        conn = pq.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        db_version = cur.fetchone()
        print(db_version)
        cur.close()
        return conn

    except (Exception, pq.DatabaseError) as error:
        print(error)


def disconnect():
    """There doesn't appear to be a psycopg2 method for connecting and
    disconnecting from the postgresql service, perhaps I'm doing this wrong...
    or just don't fully understand how this whole business works.
    """
    r = sp.Popen(["pg_ctl", "stop"], stderr=sp.STDOUT, stdout=sp.PIPE, env=ENV)
    statement = str(r.stdout.read(), "utf-8").replace("\r", "")
    statement = statement.split("\n")
    for s in statement:    
        print(s)


class runcmd:
    def __init__(self, curs):
        self.curs = curs

    def run(self, command):
        start = time.time()
        self.curs.execute(command)
        end = time.time()
        seconds = end - start
        minutes = round(seconds/60, 2)
        try:
            return self.curs.fetchmany(15)
            print("Finished in {} ".format(minutes))
        except:
            print("Command Run")
            print("Finished in {} ".format(minutes))
