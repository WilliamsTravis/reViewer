#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dash HTML elements

Include high-level options here as well (separate dropdowns or consolidated?)

Created on Sat May 23 12:42:46 2020

@author: travis
"""

import dash_html_components as html

# Navigation bar
NAVBAR = html.Nav(
          className="top-bar fixed",
          children=[

            # Sponser Logos
            html.Div([
              html.A(
                html.Img(
                  src=("/static/earthlab.png"),
                  className='one columns',
                  style={'height': '40',
                         'width': '130',
                         'float': 'right',
                         'position': 'static'}),
                  href="https://www.colorado.edu/earthlab/",
                  target="_blank"),
              html.A(
                html.Img(
                  src=('/static/wwa_logo2015.png'),
                  className='one columns',
                  style={'height': '40',
                         'width': '130',
                         'float': 'right',
                         'position': 'static'}),
                  href="http://wwa.colorado.edu/",
                  target="_blank"),
              html.A(
                html.Img(
                  src=("/static/nccasc_logo.png"),
                  className='one columns',
                  style={'height': '40',
                         'width': '170',
                         'float': 'right',
                         'position': 'relative'}),
                  href="https://www.drought.gov/drought/",
                  target="_blank"),
              html.A(
                html.Img(
                  src=("/static/cires.png"),
                  className='one columns',
                  style={'height': '40',
                         'width': '80',
                         'float': 'right',
                         'position': 'relative',
                         'margin-right': '20'}),
                  href="https://cires.colorado.edu/",
                  target="_blank"),
              html.A(
                html.Img(
                   src=("/static/culogo.png"),
                  className='one columns',
                  style={'height': '40',
                         'width': '50',
                         'float': 'right',
                         'position': 'relative',
                         'margin-right': '20',
                         'border-bottom-left-radius': '3px'}),
                  href="https://www.colorado.edu/",
                  target="_blank")],
              style={'background-color': 'white',
                     'width': '600px',
                     'position': 'center',
                     'float': 'right',
                     'margin-right': '-3px',
                     'margin-top': '-5px',
                     'border': '3px solid #cfb87c',
                     'border-radius': '5px'},
              className='row'),
             # End Sponser Logos

        # Acronym Button
        html.Button(
          children="ACRONYMS (HOVER)",
          type='button',
          title="Acronyms",
          style={'height': '45px',
                 'padding': '9px',
                 'background-color': '#cfb87c',
                 'border-radius': '4px',
                 'font-family': 'Times New Roman',
                 'font-size': '12px',
                 'margin-top': '-5px',
                 'float': 'left',
                 'margin-left': '-5px'}),
                 # End Acronym Button


          # Toggle Buttons
          html.Div([
            html.Button(id='toggle_options',
                        children='Toggle Options: Off',
                        n_clicks=1,
                        type='button',
                        title=('Display/hide options that ' +
                               'apply to each map below.'),
                        style={'display': 'none'}),
            html.Button(id="desc_button",
                        children='Project Description: Off',
                        title=('Display/hide a description of ' +
                               'the application with instructions.'),
                        style={'display': 'none'}),
            html.Button(id="click_sync",
                        children='Location Syncing: On',
                        title=('Sync/unsync the location ' +
                               'of the time series between each map.'),
                        style={'display': 'none'}),
            html.Button(id="year_sync",
                        children='Year Syncing: On',
                        title=('Sync/unsync the years ' +
                               'of the time series between each map.'),
                        style={'display': 'none'})
                        ],
            style={'float': 'left',
                   'margin-left': '15px'})],
          style={'position': 'fixed','top': '0px', 'left': '0px',
                 'background-color': 'black', 'height': '50px',
                 'width': '100%', 'zIndex': '9999',
                 'border-bottom': '10px solid #cfb87c'})
                 # End Toggle Buttons
