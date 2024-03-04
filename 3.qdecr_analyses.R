
library(miceadds)
library(QDECR)
# require(TAM)

# =========================================================
# Setup 
project_dir <- "/home/r057600/ELS_ICM"
setwd(project_dir)

SUBJ_DIR <- "/mnt/data/genr/mrdata/GenR_MRI/bids/derivatives/freesurfer/6.0.0/qdecr"
FSHOME_DIR <- "/mnt/appl/tools/freesurfer/6.0.0"  # or set up globally 

cat("\nEnviroment checks:\n", Sys.getenv("FREESURFER_HOME"))
                      # "\n", Sys.getenv("SUBJECTS_DIR"))

OUT_DIR <- file.path(project_dir,"QDECR_results_040324")

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
                      covariates = "+ age + sex", # + ethnicity + prenatal_smoking + prenatal_alcohol", 
                      dataset=sample) {
  
  # Define model formula for all analyses
  # if (analysis_name=="intercept_only") { 
  #  exposure <- "1"
  #  covariates <- ""
  # } else 
  if (analysis_name=="covariate_base") { 
    exposure <- ""
    covariates <- "age + sex + ethnicity + prenatal_smoking + prenatal_alcohol" # substr(covariates, 3, nchar(covariates)) # remove leading "+"
  # Minimally adjusted models
  } else if (grepl( "_mini_adjusted", analysis_name)) { 
    exposure <- gsub("_mini_adjusted","_z", analysis_name)
  # Confounder adjusted models
  } else if (grepl( "_conf_adjusted", analysis_name)) { 
    exposure <- gsub("_conf_adjusted","_z", analysis_name)
    covariates <- "+ age + sex + ethnicity + prenatal_smoking + prenatal_alcohol"
  # all domains
  } else if (analysis_name=="postnatal_domains") { exposure <- paste0(paste(post_domains, collapse="_z + "),"_z") 
  } else if (analysis_name=="prenatal_domains") { exposure <- paste0(paste(pren_domains, collapse="_z + "),"_z")
  # interaction analyses
  } else if (grepl( "_by_", analysis_name)) { interaction_list <- stringr::str_split(analysis_name, "_by_")[[1]]
   exposure <- paste(interaction_list, collapse="_z * ")
   covariates <- gsub(paste(" +", interaction_list[2]), "", covariates, fixed=TRUE)
  # non-linear models
  } else if (grepl("_nonlinear", analysis_name)) {
    exposure <- gsub("_nonlinear","_cat", analysis_name)
  # Adjusted for cortical thickness
   } else if (grepl( "_cthick_adjusted", analysis_name)) { 
    exposure <- gsub("_cthick_adjusted","_z", analysis_name)
    covariates <- "+ age + sex + ethnicity + prenatal_smoking + prenatal_alcohol + mean_cortical_thickness_lh + mean_cortical_thickness_rh"
  # individual domain models
  } else { exposure <- paste0(analysis_name,"_z") }
  
  # Formula
  form <- as.formula(paste0(outcome, " ~ ", exposure, covariates))
  
  # Run both hemispheres
  for (hemisf in c("rh","lh")) {
    
    a <- qdecr_fastlm(form, 
                      data = dataset, 
                      id = "folders_f09",
                      project = analysis_name, # Suggestion: add M1 to the name if it is a crude model, M2 if it is a minimally adjusted model
                      hemi = hemisf,
                      clobber = TRUE, # override analysis you have already done;
                      n_cores = 4,    # parallelization, by default maximum is 4 but can go up to 32
                      dir_subj = SUBJ_DIR, 
                      dir_fshome = FSHOME_DIR,
                      dir_tmp = file.path(project_dir,"qdecr_tmp"), # "/dev/shm", = shared memory
                      dir_out = OUT_DIR) # folder for saving in the QdecR structure
  }
}

# -	Puberty? --- to support prec development i put age interaction instead 
# Sensitivity: 
#   -	Sample selection 

analyses_list <- c(# "intercept_only", 
                   "covariate_base",

                   "prenatal_stress_mini_adjusted",
                   "prenatal_stress_conf_adjusted",
                   "prenatal_domains", post_domains,
                   "prenatal_stress_nonlinear",
                   "prenatal_stress_by_sex",
                   "prenatal_stress_by_age",
                   "prenatal_stress_by_ethnicity",
                   "prenatal_stress_cthick_adjusted",
                   
                   "postnatal_stress_mini_adjusted",
                   "postnatal_stress_conf_adjusted",
                   "postnatal_domains", pren_domains,
                   "postnatal_stress_nonlinear",
                   "postnatal_stress_by_sex",
                   "postnatal_stress_by_age",
                   "postnatal_stress_by_ethnicity",
                   "postnatal_stress_cthick_adjusted")

for (model in analyses_list) { run_model(model) }

warnings()