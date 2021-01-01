# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 16:41:32 2020

@author: travis
"""
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

from app import app, server
from apps import main_page, config_page
from apps.support import BUTTON_STYLES
from navbar import NAVBAR


app.layout = html.Div([
    NAVBAR,
    dcc.Location(id="url", pathname="/apps/main_page", refresh=False),
    html.Div(id="page-content",
             children=main_page.layout)
])


if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server()
