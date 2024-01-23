from nilearn import plotting, datasets
import nibabel as nb

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import os

from threading import Timer
import webbrowser
from dash import Dash, html, dcc, callback, Output, Input
# import dash_bootstrap_components as dbc


fsaverage = datasets.fetch_surf_fsaverage(mesh='fsaverage')

resdir = './assets/'  # '/home/r095290/datin_ELS/scripts/postnatal_els_results/'

def detect_models(folder):
    allmods = [x[0].split('/')[-1] for x in os.walk(folder)][1:]
    
    am_clean = list(set([x.split('h.')[-1] for x in allmods]))
    
    # Assume you have left and right always 
    return am_clean 

def detect_terms(model, mode='list'):
    
    l_mdir = resdir + 'lh.' + model
    r_mdir = resdir + 'rh.' + model
    
    l_stacks = pd.read_table(l_mdir + '/stack_names.txt', delimiter="\t")
    r_stacks = pd.read_table(r_mdir + '/stack_names.txt', delimiter="\t")
    
    if not l_stacks.equals(r_stacks): 
        print("ATTENTION: different models for left and right hemisphere")
    
    if mode=='list':
        return list(l_stacks.stack_name)
    else:
        return l_stacks
    

def plot_surfmap(model, term, surf='pial',  # flat, infl, pial, sphere
                 view='lateral', cmap='viridis',
                 show_clusters=False):
    out = {}
    
    stacks = detect_terms(model, mode='df')
    # Read in term names 
    stack = stacks.loc[stacks.stack_name == term, 'stack_number'].iloc[0]

    for hemi in ['left', 'right']:
        
        # Directory
        hm = hemi[0]+'h.'
        mdir = resdir + hm + model
    
        ocn = nb.load(mdir + f'/stack{stack}.cache.th30.abs.sig.ocn.mgh')  # significant
        sign_clusters = np.array(ocn.dataobj).flatten()
    
        if show_clusters:
            max_val = int(np.nanmax(sign_clusters))
    
            count = np.unique(sign_clusters, return_counts=True)
            info = f'\nResults: {np.sum(count[1][1:])} significant vertices across {max_val} clusters.'
    
            cmap = plt.get_cmap('Paired', max_val)
            surfmap = sign_clusters
            thresh = min_val = 1
    
        else:
            coef = nb.load(mdir + f'/stack{stack}.coef.mgh')  # betas
            betas = np.array(coef.dataobj).flatten()
            # print('Loading', betas.shape[0], 'vertex coefficients:\n', betas)
    
            mask = np.where(sign_clusters == 0)[0]
            betas[mask] = np.nan
    
            min_val = np.nanmin(betas)
            max_val = np.nanmax(betas)
    
            info = f'Mean beta value [range] = {np.nanmean(betas):.2f} [{min_val:.2f}; {max_val:.2f}]'
    
            surfmap = betas
            thresh = np.nanmin(abs(betas))

    
        out[hemi] = plotting.plot_surf(
            surf_mesh=fsaverage[f'{surf}_{hemi}'],  # Surface mesh geometry
            surf_map=surfmap,  # Statistical map
            bg_map=fsaverage[f'sulc_{hemi}'], # alpha=.2, only in matplotlib
            darkness=0.7,
            hemi=hemi,
            view=view,
            engine='plotly',  # or matplolib # axes=axs[0] # only for matplotlib
            cmap=cmap,
            symmetric_cmap=False,
            colorbar=True,
            vmin=min_val, vmax=max_val,
            cbar_vmin=min_val, cbar_vmax=max_val,
            avg_method='median',
            title=f'{hemi} hemisphere',
            title_font_size=20,
            threshold=thresh
        )

    return out, info

def plot_overlap(model1, term1, 
                 model2, term2,
                 surf='pial',  # flat, infl, pial, sphere
                 view='lateral'):
    out = {}
    for hemi in ['left', 'right']:
        # Directory
        hm = hemi[0]+'h.'
        
        if model1 == model2: 
            mdir1 = mdir2 = resdir + hm + model1
            # Read in term names 
            stacks1 = stacks2 = pd.read_table(mdir1 + '/stack_names.txt', delimiter="\t")
        else:
            mdir1 = resdir + hm + model1
            mdir2 = resdir + hm + model2
            # Read in term names 
            stacks1 = pd.read_table(mdir1 + '/stack_names.txt', delimiter="\t")
            stacks2 = pd.read_table(mdir2 + '/stack_names.txt', delimiter="\t")
        
        stack1 = stacks1.loc[stacks1.stack_name == term1, 'stack_number'].iloc[0]
        stack2 = stacks2.loc[stacks2.stack_name == term2, 'stack_number'].iloc[0]
        
        ocn1 = nb.load(mdir1 + f'/stack{stack1}.cache.th30.abs.sig.ocn.mgh')
        ocn2 = nb.load(mdir2 + f'/stack{stack2}.cache.th30.abs.sig.ocn.mgh')

        sign1 = np.array(ocn1.dataobj).flatten()
        sign2 = np.array(ocn2.dataobj).flatten()

        sign1[sign1 > 0] = 1
        sign2[sign2 > 0] = 2
        ovlp = np.sum([sign1, sign2], axis=0)

        cmap = plt.get_cmap('Paired', 3)

        out[hemi] = plotting.plot_surf(
            surf_mesh=fsaverage[f'{surf}_{hemi}'],  # Surface mesh geometry
            surf_map=ovlp,  # Statistical map
            bg_map=fsaverage[f'sulc_{hemi}'], # alpha=.2, only in matplotlib
            darkness=0.7,
            hemi=hemi,
            view=view,
            engine='plotly',  # or matplolib # axes=axs[0] # only for matplotlib
            cmap=cmap,
            symmetric_cmap=False,
            colorbar=True,
            vmin=1, vmax=3,
            cbar_vmin=1, cbar_vmax=3,
            title=f'{hemi} hemisphere',
            title_font_size=20,
            threshold=1
        )

    return out


# FRONT-END -----------------------------
def model_group(n, model, term):
    return html.Div([
        html.Div([
            html.Label(['Choose model:', html.Br(),
                        dcc.Dropdown(detect_models(resdir), model, id=f'model-selection{n}',
                                     style={'width': '200px', 'display': 'inline-block'}),
                        ]),
            html.Label(['Choose term:', html.Br(),
                        dcc.Dropdown(detect_terms(model), term, id=f'term-selection{n}',
                                     style={'width': '200px', 'display': 'inline-block'}),
                        ]),
            html.Label(['Surface type:', html.Br(),
                        dcc.Dropdown(['pial', 'infl', 'flat'], 'pial', id=f'surf-selection{n}',
                                     style={'width': '200px', 'display': 'inline-block'}),
                        ]),
            html.Label(['Display:', html.Br(),
                        dcc.Dropdown(['Betas', 'Clusters'], 'Betas', id=f'display-selection{n}',
                                     style={'width': '200px', 'display': 'inline-block'}),
                        ])
        ], style={'display': 'flex', 'flexWrap': 'wrap'}
        ),
        # Info
        html.Div([html.H5(id=f'info{n}', children=plot_surfmap(model, term)[1])]),
        # Maps
        html.Div(style={'display': 'inline-block', 'width': '40%'},
                 children=[dcc.Graph(id=f'graph-left{n}',
                                     figure=plot_surfmap(model, term, surf='pial', show_clusters=False)[0]['left'].figure)]),
        html.Div(style={'display': 'inline-block', 'width': '40%'},
                 children=[dcc.Graph(id=f'graph-right{n}',
                                     figure=plot_surfmap(model, term, surf='pial', show_clusters=False)[0]['right'].figure)])
    ])


app = Dash(__name__)


app.layout = html.Div([
    html.H1(children='Brain map', style={'textAlign': 'center'}),
    model_group(1, 'els_global.w_g.pct', 'postnatal_stress'),
    model_group(2, 'els_global.w_g.pct', 'postnatal_stress'),
    html.Label(['Surface type:', html.Br(),
                        dcc.Dropdown(['pial', 'infl', 'flat'], 'pial', id=f'ovlp-surf-selection',
                                     style={'width': '200px', 'display': 'inline-block'}),
                        ]),
    # Overlap maps
    html.Div(style={'display': 'inline-block', 'width': '40%'},
                 children=[dcc.Graph(id=f'ovlp-graph-left',
                                     figure=plot_overlap('els_global.w_g.pct','postnatal_stress','els_global.w_g.pct','postnatal_stress')['left'].figure)]),
    html.Div(style={'display': 'inline-block', 'width': '40%'},
                 children=[dcc.Graph(id=f'ovlp-graph-right',
                                     figure=plot_overlap('els_global.w_g.pct','postnatal_stress','els_global.w_g.pct','postnatal_stress')['right'].figure)])
])

@callback(
    Output('graph-left1', 'figure'),
    Output('graph-right1', 'figure'),
    Input('model-selection1', 'value'),
    Input('term-selection1', 'value'),
    Input('surf-selection1', 'value'),
    Input('display-selection1', 'value'),
)
def update_graph1(model, term, surf, display):

    clust = False if display == 'Betas' else True

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

    clust = False if display == 'Betas' else True

    new_surf = plot_surfmap(model=model, term=term, surf=surf, show_clusters=clust)[0]

    return new_surf['left'].figure, new_surf['right'].figure


def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:8050/')
        # webbrowser.get(using='google-chrome').open(url='http://127.0.0.1:8050/', new=2)


if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, port=8050)
