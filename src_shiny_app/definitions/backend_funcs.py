import os
import pandas as pd
import numpy as np

from nilearn import plotting, datasets
import nibabel as nb

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# ===== DATA PROCESSING FUNCTIONS ==============================================================

resdir = './assets/results/'


def detect_models(resdir=resdir):
    allmods = [x[0].split('/')[-1] for x in os.walk(resdir)][1:]

    am_clean = list(set([x.split('.')[1] for x in allmods]))  # assume structure lh.name.measure

    # Assume you have left and right hemispheres always
    return am_clean


def detect_terms(model, mode='list', resdir=resdir):
    l_mdir, r_mdir = [f'{resdir}{h}h.{model}.w_g.pct' for h in ['l', 'r']]

    l_stacks, r_stacks = [pd.read_table(f'{mdir}/stack_names.txt', delimiter="\t") for mdir in [l_mdir, r_mdir]]

    if not l_stacks.equals(r_stacks):
        print("ATTENTION: different models for left and right hemisphere")  # Happens with mean thickness

    if mode == 'list':
        return list(l_stacks.stack_name)[1:]  # Ignore intercept
    else:
        return l_stacks, l_mdir, r_mdir


def extract_results(model, term, thr='30'):

    stacks, l_mdir, r_mdir = detect_terms(model, mode='df')
    # Read in term names
    stack = stacks.loc[stacks.stack_name == term, 'stack_number'].iloc[0]

    min_beta = []
    max_beta = []
    med_beta = []

    sign_clusters_left_right = {}
    sign_betas_left_right = {}

    for h, mdir in enumerate([l_mdir, r_mdir]):
        # Read significant cluster map
        ocn = nb.load(f'{mdir}/stack{stack}.cache.th{thr}.abs.sig.ocn.mgh')
        sign_clusters = np.array(ocn.dataobj).flatten()

        # Read beta map
        coef = nb.load(f'{mdir}/stack{stack}.coef.mgh')
        betas = np.array(coef.dataobj).flatten()
        # Set non-significant betas to NA
        mask = np.where(sign_clusters == 0)[0]
        betas[mask] = np.nan

        min_beta.append(np.nanmin(betas))
        max_beta.append(np.nanmax(betas))
        med_beta.append(np.nanmean(betas))

        hemi = 'left' if h == 0 else 'right'
        sign_clusters_left_right[hemi] = sign_clusters
        sign_betas_left_right[hemi] = betas

    return np.min(min_beta), np.max(max_beta), np.mean(med_beta), sign_clusters_left_right, sign_betas_left_right


# ===== PLOTTING FUNCTIONS ===================================================================

def fetch_surface(resolution):
    # Size / number of nodes per map
    n_nodes = {'fsaverage': 163842,
               'fsaverage6': 40962,
               'fsaverage5': 10242}

    return datasets.fetch_surf_fsaverage(mesh=resolution), n_nodes[resolution]

# ---------------------------------------------------------------------------------------------

def plot_surfmap(model,
                 term,
                 surf='pial',  # 'pial', 'infl', 'flat', 'sphere'
                 resol='fsaverage6',
                 output='betas'):

    min_beta, max_beta, mean_beta, sign_clusters, sign_betas = extract_results(model, term)

    fs_avg, n_nodes = fetch_surface(resol)

    brain3D = {}

    for hemi in ['left', 'right']:

        if output == 'clusters':
            stats_map = sign_clusters[hemi]

            max_val = int(np.nanmax(stats_map))
            min_val = thresh = 1

            cmap = plt.get_cmap('Paired', max_val)

        else:
            stats_map = sign_betas[hemi]

            max_val = max_beta
            min_val = min_beta
            thresh = np.nanmin(abs(stats_map))

            cmap = 'viridis'

        brain3D[hemi] = plotting.plot_surf(
                surf_mesh=fs_avg[f'{surf}_{hemi}'],  # Surface mesh geometry
                surf_map=stats_map[:n_nodes],  # Statistical map
                bg_map=fs_avg[f'sulc_{hemi}'],  # alpha=.2, only in matplotlib
                darkness=0.7,
                hemi=hemi,
                view='lateral',
                engine='plotly',  # axes=axs[0] # only for matplotlib
                cmap=cmap,
                symmetric_cmap=False,
                colorbar=True,
                vmin=min_val, vmax=max_val,
                cbar_vmin=min_val, cbar_vmax=max_val,
                avg_method='median',
                # title=f'{hemi} hemisphere',
                # title_font_size=20,
                threshold=thresh
            ).figure

    return brain3D

# ---------------------------------------------------------------------------------------------

def plot_overlap(model1, term1, model2, term2, surf='pial', resol='fsaverage6'):

    sign_clusters1 = extract_results(model1, term1)[3]
    sign_clusters2 = extract_results(model2, term2)[3]

    fs_avg, n_nodes = fetch_surface(resol)

    cmap = ListedColormap(['r', 'g', 'b'])

    brain3D = {}

    for hemi in ['left', 'right']:

        sign1, sign2 = sign_clusters1[hemi], sign_clusters2[hemi]

        sign1[sign1 > 0] = 1
        sign2[sign2 > 0] = 2

        ovlp_map = np.sum([sign1, sign2], axis=0)

        brain3D[hemi] = plotting.plot_surf(
            surf_mesh=fs_avg[f'{surf}_{hemi}'],  # Surface mesh geometry
            surf_map=ovlp_map[:n_nodes],  # Statistical map
            bg_map=fs_avg[f'sulc_{hemi}'],  # alpha=.2, only in matplotlib
            darkness=0.7,
            hemi=hemi,
            view='lateral',
            engine='plotly',  # or matplolib # axes=axs[0] # only for matplotlib
            cmap=cmap,
            symmetric_cmap=False,
            colorbar=True,
            vmin=1, vmax=3,
            cbar_vmin=1, cbar_vmax=3,
            # title=f'{hemi} hemisphere',
            # title_font_size=20,
            threshold=1
        ).figure

    return brain3D
