# -*- coding: utf-8 -*-
"""
The configuration page layout.

Created on Sun Aug 23 14:59:00 2020

@author: travis
"""

import dash_core_components as dcc
import dash_html_components as html

from review.support import BUTTON_STYLES


NAVBAR = html.Nav(
    className="top-bar fixed",
    children=[

        html.Div([

          html.Div([
              html.H1(
                  "reView | ",
                  style={
                     'float': 'left',
                     'position': 'relative',
                     "color": "white",
                     'font-family': 'Times New Roman',
                     'font-size': '48px',
                     "font-face": "bold",
                     "margin-bottom": 5,
                     "margin-left": 15,
                     "margin-top": 0
                     }
              ),
              html.H2(
                  children=("  Renewable Energy Technical Potential Projects"),
                  style={
                    "float": "left",
                    "position": "relative",
                    "color": "white",
                    "font-family": "Times New Roman",
                    "font-size": "28px",
                    "margin-bottom": 5,
                    "margin-left": 15,
                    "margin-top": 15,
                    "margin-right": 55
                    }
                ),

              ]),

          # Not implemented yet
          html.Button(
                id="reset_chart",
                children="Reset Selections",
                title="Clear Point Selection Filters.",
                # style=BUTTON_STYLES["on"],
                style={"display": "none"}
                ),

          dcc.Link(
              html.Button(
                id="scenario_link_button",
                children="Scenario-based Page",
                type="button",
                title=("Go to the scenario-based project page."),
                style={"display": "none"},
                ),
              id="scenario_link",
              href="/apps/scenario_page",
          ),

          # dcc.Link(
          #      html.Button(
          #        id="variable_link_button",
          #        children="Variable-based Page",
          #        type="button",
          #        title=("Go to the scenario-based project page."),
          #        style={"display": "none"},
          #        ),
          #      id="variable_link",
          #      href="/apps/variable_page",
          #  ),

          dcc.Link(
              html.Button(
                id="config_link_button",
                children="Configuration Page",
                type="button",
                title=("Go to the data configuration page."),
                style={"display": "none"}
              ),
              id="config_link",
              href="/apps/config_page"
          ),

          html.A(
            html.Img(
              src=("/static/nrel_logo.png"),
              className="twelve columns",
              style={
                  "height": 70,
                  "width": 180,
                  "float": "right",
                  "position": "relative",
                  "margin-left": "10",
                  "border-bottom-right-radius": "3px"
                  }
            ),
            href="https://www.nrel.gov/",
            target="_blank"
          )

          ],
            style={
                "background-color": "#1663B5",
                "width": "100%",
                "height": 70,
                "margin-right": "0px",
                "margin-top": "-15px",
                "margin-bottom": "15px",
                "border": "3px solid #FCCD34",
                "border-radius": "5px"
                },
            className="row"),
    ])
