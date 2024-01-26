from nilearn import plotting, datasets
import nibabel as nb

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np

from definitions.results_nav_funcs import detect_models, detect_terms, resdir


fsaverage = datasets.fetch_surf_fsaverage(mesh='fsaverage')


def plot_surfmap(model,
                 term,
                 surf='pial',  # flat, infl, pial, sphere
                 view='lateral',
                 cmap='viridis',
                 show_clusters=False):
    out = {}

    stacks = detect_terms(model, mode='df')
    # Read in term names
    stack = stacks.loc[stacks.stack_name == term, 'stack_number'].iloc[0]

    for hemi in ['left', 'right']:

        # Directory
        hm = hemi[0] + 'h.'
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
            bg_map=fsaverage[f'sulc_{hemi}'],  # alpha=.2, only in matplotlib
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
