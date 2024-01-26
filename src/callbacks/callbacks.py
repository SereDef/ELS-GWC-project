from dash import Dash, html, dcc, callback, Output, Input, no_update, ctx

import definitions.layout_styles as styles

from definitions.results_nav_funcs import detect_models, detect_terms
from definitions.plotting_funcs import plot_surfmap, plot_overlap
from definitions.frontend_funcs import badge_it

# Update terms when the selected model1 changes
@callback(
    Output('term-selection1', 'options'),
    Output('term-selection1', 'value'),
    Input('model-selection1', 'value'),
)
def update_terms1(model):

    if ctx.triggered_id == 'model-selection1':
        terms = detect_terms(model, mode='list')
        place_holder = "Select term"

        return terms, place_holder

    return no_update, no_update


# Update terms when the selected model2 changes
@callback(
    Output('term-selection2', 'options'),
    Output('term-selection2', 'value'),
    Input('model-selection2', 'value'),
)
def update_terms2(model):

    if ctx.triggered_id == 'model-selection2':
        terms = detect_terms(model, mode='list')
        place_holder = "Select term"

        return terms, place_holder

    return no_update, no_update

@callback(
    Output('graph-left1', 'figure'),
    Output('graph-right1', 'figure'),
    Input('model-selection1', 'value'),
    Input('term-selection1', 'value'),
    Input('surf-selection1', 'value'),
    Input('display-selection1', 'value'),
)
def update_graph1(model, term, surf, display):

    if term == "Select term":
        return no_update, no_update

    clust = False if display == 'betas' else True

    new_surf = plot_surfmap(model=model, term=term, surf=surf, show_clusters=clust)[0]

    return new_surf['left'].figure, new_surf['right'].figure


@callback(
    Output('graph-left2', 'figure'),
    Output('graph-right2', 'figure'),
    Input('model-selection2', 'value'),
    Input('term-selection2', 'value'),
    Input('surf-selection2', 'value'),
    Input('display-selection2', 'value'),
)
def update_graph2(model, term, surf, display):

    if term == "Select term":
        return no_update, no_update

    clust = False if display == 'betas' else True

    new_surf = plot_surfmap(model=model, term=term, surf=surf, show_clusters=clust)[0]

    return new_surf['left'].figure, new_surf['right'].figure


@callback(
    Output('ovlp-graph-left', 'figure'),
    Output('ovlp-graph-right', 'figure'),
    Output('ovlp-info', 'children'),
    Input('model-selection1', 'value'),
    Input('term-selection1', 'value'),
    Input('model-selection2', 'value'),
    Input('term-selection2', 'value'),
    Input('ovlp-surf-selection', 'value')

)
def update_graph3(model1, term1, model2, term2, surf):

    if term1 == "Select term" or term2 == "Select term":
        return no_update, no_update

    new_surf = plot_overlap(model1, term1, model2, term2, surf=surf)

    info = ['Visualize overlap ',
            badge_it(' ', color=styles.OVLP_COLOR1), ' between ', term1,
            badge_it(' ', color=styles.OVLP_COLOR2), ' (from the ', model1, ' model) and ', term2,
            badge_it(' ', color=styles.OVLP_COLOR3), ' (from the ', model2, ' model).']

    return new_surf['left'].figure, new_surf['right'].figure, info

# ---------------------- Callbacks ---------------------------------
# Callbacks are all client-side (https://dash.plot.ly/performance)
# in order to transform the app into static html pages
# javascript functions are defined in assets/callbacks.js

# app.clientside_callback(
#     ClientsideFunction(
#         namespace='clientside3',
#         function_name='update_table'
#     ),
#     output=Output('table', 'selected_rows'),
#     inputs=[
#         Input('map', 'clickData'),
#         Input('map', 'selectedData'),
#         Input('table', 'data')
#         ],
#     state=[State('table', 'selected_rows'),
#            State('store', 'data')],
#     )