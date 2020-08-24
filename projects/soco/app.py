# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 16:39:45 2020

@author: travis
"""

import dash

from apps.support import STYLESHEET

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[STYLESHEET])
server = app.server
