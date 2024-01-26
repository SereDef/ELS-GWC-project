from dash import html, dcc
import dash_bootstrap_components as dbc

import definitions.layout_styles as styles

from definitions.results_nav_funcs import detect_models, detect_terms
from definitions.plotting_funcs import plot_surfmap, plot_overlap


def badge_it(text, color, fs=10, pad='7px 7px'):
    return html.Span([' ', dbc.Badge(text, color=color, style={'padding': pad, 'font-size': fs}), ' '])


def model_group(n, model, term):
    return html.Div([
        dbc.Row(style={'background-color': styles.SELECTION_PANE_COLOR, 'border-radius': styles.SELECTION_PANE_CORNER},
                children=[dbc.Col(width={'size': 2},
                                  children=[html.Div(style={'margin-left': styles.SELECTION_PANE_MARGIN},
                                                     children=[html.Label(['Choose model:', html.Br(),
                                                                           dcc.Dropdown(id=f'model-selection{n}',
                                                                                        options=detect_models(),
                                                                                        value=model,
                                                                                        style=styles.DROPDOWN_STYLE)
                                                       ])])]),
                          dbc.Col(width={'size': 2},
                                  children=[html.Div(style={'margin-left': styles.SELECTION_PANE_MINIMARGIN},
                                                     children=[html.Label(['Choose term:', html.Br(),
                                                                           dcc.Dropdown(id=f'term-selection{n}',
                                                                                        options=detect_terms(model),
                                                                                        value=term,
                                                                                        style=styles.DROPDOWN_STYLE)
                                                        ])])]),
                          dbc.Col(width={'size': 2},
                                  children=[html.Div(style={'margin-left': styles.SELECTION_PANE_MINIMARGIN},
                                                     children=[html.Label(['Surface type:', html.Br(),
                                                                           dcc.Dropdown(id=f'surf-selection{n}',
                                                                                        options=[
                                                                                            {'value': 'pial', 'label': 'pial'},
                                                                                            {'value': 'infl', 'label': 'inflated'},
                                                                                            {'value': 'flat', 'label': 'flat'}],
                                                                                        value='pial',
                                                                                        style=styles.DROPDOWN_STYLE)
                                                        ])])]),
                          dbc.Col(width={'size': 2},
                                  children=[html.Div(style={'margin-left': styles.SELECTION_PANE_MINIMARGIN},
                                                     children=[html.Label(['Display:', html.Br(),
                                                                           dcc.Dropdown(id=f'display-selection{n}',
                                                                                        options=['betas', 'clusters'],
                                                                                        value='betas',
                                                                                        style=styles.DROPDOWN_STYLE)
                                                        ])])]),
                          ],
                ),
        # Info
        html.Div(id=f'info{n}',
                 children=[html.Br(), plot_surfmap(model, term)[1], html.Br()],
                 style={'font-size': styles.INFO_FONTSIZE}),
        # Maps
        html.Div(style={'display': 'inline-block', 'width': styles.PLOT_WIDTH},
                 children=[
                     dcc.Graph(id=f'graph-left{n}',
                               figure=plot_surfmap(model, term, surf='pial', show_clusters=False)[0]['left'].figure)
                           ]),
        html.Div(style={'display': 'inline-block', 'width': styles.PLOT_WIDTH},
                 children=[
                     dcc.Graph(id=f'graph-right{n}',
                               figure=plot_surfmap(model, term, surf='pial', show_clusters=False)[0]['right'].figure)
                           ])
    ])


def overlap_group(model1, term1, model2, term2):
    return html.Div([
        html.Div([html.Label(['Surface type:', html.Br(),
                              dcc.Dropdown(['pial', 'infl', 'flat'], 'pial', id=f'ovlp-surf-selection',
                                           style={'width': '200px', 'display': 'inline-block'})])
                  ],
                 style={'background-color': styles.SELECTION_PANE_COLOR,
                        'border-radius': styles.SELECTION_PANE_CORNER}
                 ),
        html.Div(id='ovlp-info',
                 children=['Visualize overlap ',
                           badge_it(' ', color=styles.OVLP_COLOR1), ' between ', term1,
                           badge_it(' ', color=styles.OVLP_COLOR2), ' (from the ', model1, ' model) and ', term2,
                           badge_it(' ', color=styles.OVLP_COLOR3), ' (from the ', model2, ' model).'],
                 style={'font-size': styles.INFO_FONTSIZE}),

        # Overlap maps
        html.Div(style={'display': 'inline-block', 'width': styles.PLOT_WIDTH},
                 children=[dcc.Graph(id='ovlp-graph-left',
                                     figure=plot_overlap(model1, term1, model2, term2)['left'].figure)]),
        html.Div(style={'display': 'inline-block', 'width': styles.PLOT_WIDTH},
                 children=[dcc.Graph(id='ovlp-graph-right',
                                     figure=plot_overlap(model1, term1, model2, term2)['right'].figure)])
    ])
