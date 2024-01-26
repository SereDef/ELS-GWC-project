from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

import os
from threading import Timer
import webbrowser

import definitions.layout_styles as styles

from definitions.frontend_funcs import model_group, overlap_group
from callbacks import callbacks


FONT_AWESOME = "https://use.fontawesome.com/releases/v5.13.0/css/all.css"
external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]

app = Dash(__name__,
           external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    # TITLE
    html.Br(),
    html.H1(id='title',
            style=styles.TITLE,
            children='BrainMApp: early-life stress and intracortical myelin'),
    html.Br(),

    # CONTENT
    dbc.Row(
        dbc.Col(width={'size': 10, 'offset': 1},
                children=[
                    # Map 1
                    model_group(1, 'els_global.w_g.pct', 'postnatal_stress'),
                    # Map 2
                    model_group(2, 'pre_els_global.w_g.pct', 'prenatal_stress'),
                    # Overlap map
                    overlap_group('els_global.w_g.pct', 'postnatal_stress',
                                  'pre_els_global.w_g.pct', 'prenatal_stress')
                ])
    ),
    html.Br()
])


def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:8050/')
        # webbrowser.get(using='google-chrome').open(url='http://127.0.0.1:8050/', new=2)


if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, port=8050)
