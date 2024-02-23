#!/bin/bash
#SBATCH --mem=10GB
#SBATCH --job-name="ELSICM"
#SBATCH --output=ELS_ICM_QDECR.log
#SBATCH -t 4-00:00

# SET-UP
module load R

# If not yet done, configure Freesurfer
export FREESURFER_HOME=/mnt/appl/tools/freesurfer/6.0.0
source $FREESURFER_HOME/SetUpFreeSurfer.sh

# echo 'export FREESURFER_HOME=/mnt/appl/tools/freesurfer/6.0.0' >> ~/.bashrc 
# echo 'source $FREESURFER_HOME/SetUpFreeSurfer.sh' >> ~/.bashrc


# Run entire pipeline (or part of it)

# Rscript 1.els_brain_merge.R
# Rscript 2.clean_and_filter.R
Rscript 3.qdecr_analyses.R