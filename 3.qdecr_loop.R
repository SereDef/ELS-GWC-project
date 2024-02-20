library(QDECR)

project_dir <- "/home/r057600/datin_ELS"
setwd(project_dir)

sample <- readRDS("els_brain_sample.rds")

# TODO: compute z scores
# Rename age variable and mean thickness variable?
# lh_MeanThickness_f09

post_domains <- c("post_life_events","post_contextual_risk","post_parental_risk","post_interpersonal_risk","post_direct_victimization")
pren_domains <- c("pre_life_events","pre_contextual_risk","pre_parental_risk","pre_interpersonal_risk")


run_models <- function(analysis_name, 
                       outcome = "qdecr_w_g.pct", 
                       covariates = "+ age_child_mri_f09 + sex", 
                       dataset=sample)
  {
  
  # Define exposure variables
  if (analysis_name=="covariate_base") { exposure <- ""; covariates <- substr(covariates, 3, nchar(covariates)) # remove leading + 
  } else if (analysis_name=="post_domains") { exposure <- paste0(paste(post_domains, collapse="_z + "),"_z") 
  } else if (analysis_name=="pren_domains") { exposure <- paste0(paste(pren_domains, collapse="_z + "),"_z")
  
  } else { exposure <- paste0(analysis_name,"_z") }
  
  # Define model formula
  form <- as.formula(paste0(outcome, " ~ ", exposure, covariares))
  
  # Run both hemispheres
  for (hemisf in c("rh","lh")) {
    
    a <- qdecr_fastlm(form, 
                      data = dataset, 
                      id = "folders_f09",
                      project = analysis_name, # Suggestion: add M1 to the name if it is a crude model, M2 if it is a minimally adjusted model
                      hemi = hemisf,
                      clobber = TRUE, # override analysis you have already done;
                      n_cores = 4,    # parallelization, by default maximum is 4 but can go up to 32
                      dir_subj = "/mnt/data/genr/mrdata/GenR_MRI/bids/derivatives/freesurfer/6.0.0/", 
                      dir_fshome = "/mnt/appl/tools/freesurfer/6.0.0",
                      dir_tmp = paste0(project_dir,"/qdec_tmp"), # "/dev/shm", = shared memory
                      dir_out = paste0(project_dir,"/qdec_results")) # folder for saving in the QdecR structure
    
    # Save model objet too
    saveRDS(a, paste0(project_dir,"/qdec_results/",analysis_name,"_",hemisf,".rds"))
  }
}


analyses_list <- c("covariate_base", 
                   "postnatal_stress","post_domains", post_domains,
                   "prenatal_stress","pren_domains", pren_domains)

