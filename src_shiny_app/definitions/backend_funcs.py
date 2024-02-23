import os
import pandas as pd
import numpy as np

from nilearn import plotting, datasets
import nibabel as nb

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


resdir = './assets/results/'


def detect_models(resdir=resdir):
    allmods = [x[0].split('/')[-1] for x in os.walk(resdir)][1:]

    am_clean = list(set([x.split('.')[1] for x in allmods]))  # assume structure lh.name.measure

    # Assume you have left and right hemispheres always
    return am_clean


def detect_terms(model, mode='list', resdir=resdir):
    l_mdir = f'{resdir}lh.{model}.w_g.pct'
    r_mdir = f'{resdir}rh.{model}.w_g.pct'

    l_stacks = pd.read_table(l_mdir + '/stack_names.txt', delimiter="\t")
    r_stacks = pd.read_table(r_mdir + '/stack_names.txt', delimiter="\t")

    if not l_stacks.equals(r_stacks):
        print("ATTENTION: different models for left and right hemisphere")

    if mode == 'list':
        return list(l_stacks.stack_name)[1:]
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
        ocn = nb.load(mdir + f'/stack{stack}.cache.th{thr}.abs.sig.ocn.mgh')
        sign_clusters = np.array(ocn.dataobj).flatten()

        # Read beta map
        coef = nb.load(mdir + f'/stack{stack}.coef.mgh')
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


# ===== PLOTTING FUNCTIONS ================================

fsaverage = datasets.fetch_surf_fsaverage(mesh='fsaverage')


def plot_surfmap(model,
                 term,
                 surf,  # 'pial', 'infl', 'flat', 'sphere'
                 output='betas'):

    min_beta, max_beta, mean_beta, sign_clusters, sign_betas = extract_results(model, term)

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
                surf_mesh=fsaverage[f'{surf}_{hemi}'],  # Surface mesh geometry
                surf_map=stats_map,  # Statistical map
                bg_map=fsaverage[f'sulc_{hemi}'],  # alpha=.2, only in matplotlib
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

# -------------------------------------------------

def plot_overlap(model1, term1,
                 model2, term2,
                 surf='pial',  # flat, infl, pial, sphere
                 view='lateral'):
    out = {}
    for hemi in ['left', 'right']:
        # Directory
        hm = hemi[0] + 'h.'

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

        # cmap = plt.get_cmap('Paired', 3)
        cmap = ListedColormap(['r', 'g', 'b'])

        out[hemi] = plotting.plot_surf(
            surf_mesh=fsaverage[f'{surf}_{hemi}'],  # Surface mesh geometry
            surf_map=ovlp,  # Statistical map
            bg_map=fsaverage[f'sulc_{hemi}'],  # alpha=.2, only in matplotlib
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
