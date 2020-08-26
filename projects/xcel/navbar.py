# -*- coding: utf-8 -*-
"""
The configuration page layout.

Created on Sun Aug 23 14:59:00 2020

@author: travis
"""

import dash_core_components as dcc
import dash_html_components as html

from apps.support import BUTTON_STYLES


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
                    'float': 'left',
                    'position': 'relative',
                    "color": "white",
                    'font-family': 'Times New Roman',
                    'font-size': '28px',
                    "margin-bottom": 5,
                    "margin-left": 15,
                    "margin-top": 15,
                    "margin-right": 55
                    }
                ),

              ]),

          html.Button(
                id='sync_variables',
                children='Sync Variables: On',
                n_clicks=1,
                type='button',
                title=('Click to sync the chosen variable between the map '
                       'and y-axis of the chart.'),
                style=BUTTON_STYLES["on"]
                ),

          html.Button(
                id='rev_color',
                children='Reverse Map Color: Off',
                n_clicks=1,
                type='button',
                title=('Click to render the map with the inverse of '
                       'the chosen color ramp.'),
                style=BUTTON_STYLES["on"]
                ),

          html.Button(
                id="reset_chart",
                children="Reset Selections",
                title="Clear Point Selection Filters.",
                # style=BUTTON_STYLES["on"],
                style={"display": "none"}
                ),
          html.A(
            html.Img(
              src=("/static/nrel_logo.png"),
              className='twelve columns',
              style={
                  'height': 70,
                  'width': 180,
                  "float": "right",
                  'position': 'relative',
                  "margin-left": "10",
                  'border-bottom-right-radius': '3px'
                  }
            ),
            href="https://www.nrel.gov/",
            target="_blank"
          )

          ],
            style={
                'background-color': '#1663B5',
                'width': '100%',
                "height": 70,
                'margin-right': '0px',
                'margin-top': '-15px',
                'margin-bottom': '35px',
                'border': '3px solid #FCCD34',
                'border-radius': '5px'
                },
            className='row'),
    ])
