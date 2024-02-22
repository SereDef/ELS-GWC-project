
library(miceadds)
library(QDECR)
# require(TAM)

# =========================================================
# Setup 
project_dir <- "/home/r057600/ELS_ICM"
setwd(project_dir)

SUBJ_DIR <- "/mnt/data/genr/mrdata/GenR_MRI/bids/derivatives/freesurfer/6.0.0/qdecr"
# FSHOME_DIR <- "/mnt/appl/tools/freesurfer/6.0.0"  # Set up globally 

OUT_DIR <- file.path(project_dir,"QDECR_results_220224")

# sample <- readRDS(file.choose())
sample <- readRDS(file.path(project_dir, "Data/ELS_brain_sample.rds"))

pren_domains <- c("pre_life_events","pre_contextual_risk","pre_parental_risk","pre_interpersonal_risk")
post_domains <- c("post_life_events","post_contextual_risk","post_parental_risk","post_interpersonal_risk","post_direct_victimization")

# Compute sample z-scores 
cat('\nComputing z-scores...\n')
var_list <- c("prenatal_stress", "postnatal_stress", pren_domains, post_domains)
sample <- datlist2mids( scale_datlist( mids2datlist(sample), orig_var = var_list, trafo_var = paste0(var_list, "_z")))


# Main analysis function
run_model <- function(analysis_name, 
                      outcome = "qdecr_w_g.pct", 
                      covariates = "+ age + sex + ethnicity + prenatal_smoking + prenatal_alcohol", 
                      dataset=sample) {
  
  # Define model formula for all analyses
  if (analysis_name=="covariate_base") { 
    exposure <- ""
    covariates <- substr(covariates, 3, nchar(covariates)) # remove leading + 
  # all domains
  } else if (analysis_name=="post_domains") { exposure <- paste0(paste(post_domains, collapse="_z + "),"_z") 
  } else if (analysis_name=="pren_domains") { exposure <- paste0(paste(pren_domains, collapse="_z + "),"_z")
  # stratified analyses
  } else if (grepl( "_by_", analysis_name)) { interaction_list <- stringr::str_split(analysis_name, "_by_")[[1]]
   exposure <- paste(interaction_list, collapse="_z * ")
   covariates <- gsub(paste(" +", interaction_list[2]), "", covariates, fixed=TRUE)
  # Adjusted for cortical thickness
  } else if (grepl( "_ct_adjusted", analysis_name)) { 
    exposure <- gsub("_ct_adjusted","_z",analysis_name)
    covariates <- paste(covariates, "")
  # simpler model
  } else { exposure <- paste0(analysis_name,"_z") }
  
  # Formula
  form <- as.formula(paste0(outcome, " ~ ", exposure, covariates))
  
  # Run both hemispheres
  for (hemisf in c("rh","lh")) {
    
    if (grepl( "_ct_adjusted", analysis_name)) { 
      covariates <- paste0(covariates, " + mean_cortical_thickness_", hemisf) }
    
    a <- qdecr_fastlm(form, 
                      data = dataset, 
                      id = "folders_f09",
                      project = analysis_name, # Suggestion: add M1 to the name if it is a crude model, M2 if it is a minimally adjusted model
                      hemi = hemisf,
                      clobber = TRUE, # override analysis you have already done;
                      n_cores = 4,    # parallelization, by default maximum is 4 but can go up to 32
                      dir_subj = SUBJ_DIR, 
                      # dir_fshome = FSHOME_DIR,
                      dir_tmp = file.path(project_dir,"qdecr_tmp"), # "/dev/shm", = shared memory
                      dir_out = OUT_DIR) # folder for saving in the QdecR structure
    
    # Save model object too
    # saveRDS(a, file.path(OUT_DIR,"all_models", paste0(analysis_name,"_",hemisf,".rds"))) 
  }
}

# -	Nonlinear (cut)  – 2 models (pre and post)
# -	Puberty? --- to support prec development i put age interaction instead 
# Sensitivity: 
#   -	Sample selection 

analyses_list <- c("covariate_base", 
                   
                   "prenatal_stress",
                   "pren_domains", pren_domains,
                   "prenatal_stress_by_sex",
                   "prenatal_stress_by_age",
                   "prenatal_stress_by_ethnicity",
                   "prenatal_stress_ct_adjusted",
                   
                   "postnatal_stress",
                   "post_domains", post_domains,
                   "postnatal_stress_by_sex",
                   "postnatal_stress_by_age",
                   "postnatal_stress_by_ethnicity",
                   "postnatal_stress_ct_adjusted")

for (model in analyses_list) { run_model(model) }