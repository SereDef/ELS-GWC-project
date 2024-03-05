import os
import pandas as pd
import numpy as np
import warnings

from nilearn import plotting, datasets
import nibabel as nb

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

import definitions.layout_styles as styles

# ===== DATA PROCESSING FUNCTIONS ==============================================================

results_directory = './assets/results/'


def detect_models(resdir=results_directory, out_clean=False):
    all_models = [x[0].split('/')[-1] for x in os.walk(resdir)][1:]  # assume all stored in resdir

    all_model_names = list(set([x.split('.')[1] for x in all_models]))  # assume structure lh.name.measure

    if out_clean:
        clean_dic = {'base model': {'covariate_base': 'Covariates only'},
                     'prenatal models': {'prenatal_stress_conf_adjusted': 'Prenatal ELS - confound. adjusted',
                                         'prenatal_stress_mini_adjusted': 'Prenatal ELS - minimal. adjusted',
                                         'prenatal_stress_cthick_adjusted': 'Prenatal ELS + cort. thickness',
                                         'prenatal_stress_nonlinear': 'Prenatal ELS - non-linear',
                                         'prenatal_stress_by_sex': 'Prenatal ELS by sex',
                                         'prenatal_stress_by_age': 'Prenatal ELS by age',
                                         'prenatal_stress_by_ethnicity': 'Prenatal ELS by ethnicity',
                                         'prenatal_domains': 'Prenatal domains (all)',
                                         'pre_life_events': 'Prenatal life events',
                                         'pre_contextual_risk': 'Prenatal contextual risk',
                                         'pre_parental_risk': 'Prenatal parental risk',
                                         'pre_interpersonal_risk': 'Prenatal interpersonal risk'},
                     'postnatal models': {'postnatal_stress_conf_adjusted': 'Postnatal ELS - confound. adjusted',
                                          'postnatal_stress_mini_adjusted': 'Postnatal ELS - minimal. adjusted',
                                          'postnatal_stress_cthick_adjusted': 'Postnatal ELS + cort. thickness',
                                          'postnatal_stress_nonlinear': 'Postnatal ELS - non-linear',
                                          'postnatal_stress_by_sex': 'Postnatal ELS by sex',
                                          'postnatal_stress_by_age': 'Postnatal ELS by age',
                                          'postnatal_stress_by_ethnicity': 'Postnatal ELS by ethnicity',
                                          'postnatal_domains': 'Postnatal domains (all)',
                                          'post_life_events': 'Postnatal life events',
                                          'post_contextual_risk': 'Postnatal contextual risk',
                                          'post_parental_risk': 'Postnatal parental risk',
                                          'post_interpersonal_risk': 'Postnatal interpersonal risk',
                                          'post_direct_victimization': 'Postnatal direct victimization'}}
        dic_model_names = [ele for ww in clean_dic.keys() for ele in clean_dic[ww]]
        if not set(all_model_names) == set(dic_model_names):
            return all_model_names
        else:
            return clean_dic

    out_terms = {}
    for model in all_model_names:
        # Assume you have left and right hemispheres are always run and with the same model
        mdir = f'{resdir}lh.{model}.w_g.pct'
        stacks = pd.read_table(f'{mdir}/stack_names.txt', delimiter="\t")

        out_terms[model] = dict(zip(list(stacks.stack_name)[1:], list(stacks.stack_number)[1:]))

    # Assume you have left and right hemispheres are always run
    return out_terms


def extract_results(model, term, thr='30'):

    stack = detect_models()[model][term]

    min_beta = []
    max_beta = []
    med_beta = []
    n_clusters = []

    sign_clusters_left_right = {}
    sign_betas_left_right = {}

    for hemi in ['left', 'right']:
        mdir = f'{results_directory}{hemi[0]}h.{model}.w_g.pct'
        # Read significant cluster map
        ocn = nb.load(f'{mdir}/stack{stack}.cache.th{thr}.abs.sig.ocn.mgh')
        sign_clusters = np.array(ocn.dataobj).flatten()

        if not np.any(sign_clusters):  # all zeros = no significant clusters
            betas = np.empty(sign_clusters.shape)
            betas.fill(np.nan)
            n_clusters.append(0)
        else:
            # Read beta map
            coef = nb.load(f'{mdir}/stack{stack}.coef.mgh')
            betas = np.array(coef.dataobj).flatten()

            # Set non-significant betas to NA
            mask = np.where(sign_clusters == 0)[0]
            betas[mask] = np.nan

            n_clusters.append(np.max(sign_clusters))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            min_beta.append(np.nanmin(betas))
            max_beta.append(np.nanmax(betas))
            med_beta.append(np.nanmean(betas))

        sign_clusters_left_right[hemi] = sign_clusters
        sign_betas_left_right[hemi] = betas

    return np.nanmin(min_beta), np.nanmax(max_beta), np.nanmean(med_beta), n_clusters, sign_clusters_left_right, sign_betas_left_right


def compute_overlap(model1, term1, model2, term2):

    sign_clusters1 = extract_results(model1, term1)[4]
    sign_clusters2 = extract_results(model2, term2)[4]

    ovlp_maps = {}
    ovlp_info = {}

    for hemi in ['left', 'right']:
        sign1, sign2 = sign_clusters1[hemi], sign_clusters2[hemi]

        sign1[sign1 > 0] = 1
        sign2[sign2 > 0] = 2

        # Create maps
        ovlp_maps[hemi] = np.sum([sign1, sign2], axis=0)

        # Extract info
        uniques, counts = np.unique(ovlp_maps[hemi], return_counts=True)
        ovlp_info[hemi] = dict(zip(uniques, counts))
        ovlp_info[hemi].pop(0)  # only significant clusters

    # Merge left and right info
    info = {k: [ovlp_info['left'].get(k, 0) + ovlp_info['right'].get(k, 0)] for k in
            set(ovlp_info['left']) | set(ovlp_info['right'])}
    percent = [round(i[0] / sum(sum(info.values(), [])) * 100, 1) for i in info.values()]

    for i, k in enumerate(info.keys()):
        info[k].append(percent[i])

    return info, ovlp_maps


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

    min_beta, max_beta, mean_beta, n_clusters, sign_clusters, sign_betas = extract_results(model, term)

    fs_avg, n_nodes = fetch_surface(resol)

    brain3D = {}

    for hemi in ['left', 'right']:

        if output == 'clusters':
            stats_map = sign_clusters[hemi]

            max_val = int(np.nanmax(n_clusters))
            min_val = thresh = 1

            cmap = plt.get_cmap(styles.CLUSTER_COLORMAP, max_val)

        else:
            stats_map = sign_betas[hemi]

            max_val = max_beta
            min_val = min_beta

            if max_val < 0 and min_val < 0:  # all negative associations
                thresh = max_val
            elif max_val > 0 and min_val > 0:  # all positive associations
                thresh = min_val
            else:
                thresh = np.nanmin(abs(stats_map))

            cmap = styles.BETA_COLORMAP

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

    ovlp_maps = compute_overlap(model1, term1, model2, term2)[1]

    fs_avg, n_nodes = fetch_surface(resol)

    cmap = ListedColormap([styles.OVLP_COLOR1, styles.OVLP_COLOR2, styles.OVLP_COLOR3])

    brain3D = {}

    for hemi in ['left', 'right']:

        brain3D[hemi] = plotting.plot_surf(
            surf_mesh=fs_avg[f'{surf}_{hemi}'],  # Surface mesh geometry
            surf_map=ovlp_maps[hemi][:n_nodes],  # Statistical map
            bg_map=fs_avg[f'sulc_{hemi}'],  # alpha=.2, only in matplotlib
            darkness=0.7,
            hemi=hemi,
            view='lateral',
            engine='plotly',  # or matplolib # axes=axs[0] # only for matplotlib
            cmap=cmap,
            colorbar=False,
            vmin=1, vmax=3,
            threshold=1
        ).figure

    return brain3D
