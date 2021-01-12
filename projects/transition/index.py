# -*- coding: utf-8 -*-
"""Transition reView project index file.

Created on Sun Aug 23 16:41:32 2020

@author: travis
"""
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

from app import app, server
from apps import main_page, config_page
from review.support import BUTTON_STYLES
from navbar import NAVBAR


app.layout = html.Div([
    NAVBAR,
    dcc.Location(id="url", pathname="/apps/main_page", refresh=False),
    html.Div(id="page_content")
])


@app.callback([Output("page_content", "children"),
               Output("app_link_button", "style"),
               Output("config_link_button", "style")],
              [Input("url", "pathname")])
def change_page(pathname):
    """Output chosen layout from the navigation bar links."""
    config_style = BUTTON_STYLES["on"]
    app_style = BUTTON_STYLES["on"]
    if pathname == "/apps/config_page":
        page = config_page.layout
        config_style = {"display": "none"}
    else:
        page = main_page.layout
        app_style = {"display": "none"}

    return page, app_style, config_style


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(port="9876")
