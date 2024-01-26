import os
import pandas as pd

resdir = './assets/results/'   # '/home/r095290/datin_ELS/scripts/postnatal_els_results/'

def detect_models(resdir=resdir):
    allmods = [x[0].split('/')[-1] for x in os.walk(resdir)][1:]

    am_clean = list(set([x.split('h.')[-1] for x in allmods]))

    # Assume you have left and right always
    return am_clean


def detect_terms(model, mode='list',
                 resdir=resdir):
    l_mdir = resdir + 'lh.' + model
    r_mdir = resdir + 'rh.' + model

    l_stacks = pd.read_table(l_mdir + '/stack_names.txt', delimiter="\t")
    r_stacks = pd.read_table(r_mdir + '/stack_names.txt', delimiter="\t")

    if not l_stacks.equals(r_stacks):
        print("ATTENTION: different models for left and right hemisphere")

    if mode == 'list':
        return list(l_stacks.stack_name)
    else:
        return l_stacks
