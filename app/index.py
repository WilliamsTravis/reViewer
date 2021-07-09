# -*- coding: utf-8 -*-
"""Transition reView project 5index file.

Created on Sun Aug 23 16:41:32 2020

@author: travis
"""
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

import scenario_page, config_page

from app import app, server
from innovations_presentation import innovation_layouts
from review.support import BUTTON_STYLES
from navbar import NAVBAR

print("FLASK SERVER SETTINGS: \n   " + str(dict(server.config)))


app.layout = html.Div([
    NAVBAR,
    dcc.Location(id="url", refresh=False),
    html.Div(id="page_content")
])


PAGES = {
    "/": scenario_page.layout,
    "/scenario_page": scenario_page.layout,
    "/config_page": config_page.layout
}

PAGES = {**PAGES, **innovation_layouts()}


@app.callback([Output("page_content", "children"),
               Output("scenario_link_button", "style"),
               Output("config_link_button", "style")],
              [Input("url", "pathname")])
def change_page(pathname):
    """Output chosen layout from the navigation bar links."""
    config_style = BUTTON_STYLES["on"]
    scenario_style = BUTTON_STYLES["on"]
    print(f"URL: {pathname}")
    page = PAGES[pathname]
    if pathname == "/config_page":
        config_style = {"display": "none"}
    else:
        scenario_style = {"display": "none"}
    return page, scenario_style, config_style


if __name__ == '__main__':
    # app.run_server(debug=True, port="9876")
    app.run_server(debug=False, port="8000")
