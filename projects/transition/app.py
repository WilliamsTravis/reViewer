# -*- coding: utf-8 -*-
"""Create dash application objects, server, and data caches.
s
Created on Sun Aug 23 16:39:45 2020

@author: travis
"""

import dash

from review.support import STYLESHEET
from flask_caching import Cache

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[STYLESHEET])
server = app.server

# Create simple cache for storing updated supply curve tables
cache = Cache(config={'CACHE_TYPE': 'filesystem',
                      'CACHE_DIR': 'data/cache',
                      'CACHE_THRESHOLD': 10})

# Create another cache for storing filtered supply curve tables
cache2 = Cache(config={'CACHE_TYPE': 'filesystem',
                       'CACHE_DIR': 'data/cache2',
                       'CACHE_THRESHOLD': 10})

# Create another cache for storing filtered supply curve tables
cache3= Cache(config={'CACHE_TYPE': 'filesystem',
                       'CACHE_DIR': 'data/cache3',
                       'CACHE_THRESHOLD': 10})

cache.init_app(server)
cache2.init_app(server)
cache3.init_app(server)
