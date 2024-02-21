library(mice)
library(dplyr)               
  
# els_brain <- readRDS(file.choose())
els_brain <- readRDS('../Data/ELS_brain.rds')

# ============================================

verbose_filter <- function(dataframe, ...) {
  df <- dataframe
  vars = as.list(substitute(list(...)))[-1L]
  
  m = 31 # for stacked (multiple imputation) datasets (else m=1)
  
  for(arg in vars) {
    dataframe <- df
    dataframe_new <- dataframe %>% filter(!!arg)
    rows_filtered <- (nrow(df) - nrow(dataframe_new))/m
    new_df_size <- nrow(dataframe_new)/m
    cat(sprintf('Filtered out %s rows using: %s. New data size = %s\n', rows_filtered, deparse(arg), new_df_size))
    df = dataframe_new
  }
  return(dataframe_new)
}


long.data <- mice::complete(els_brain, "long", include = TRUE) %>%

   # Recode ethnicity 
   mutate(ethnicity = if_else(is.na(ethn_cont), NA_character_,
                      if_else(ethn_cont=="Dutch", "Dutch", 
                      if_else(ethn_cont=="European", "other European", "non-European")))) %>%
                      # NOTE: non-European = 'Indonesian','American, western','Asian, western','Oceanie','Cape Verdian','Moroccan','Dutch Antilles','Surinamese','Turkish','African','American, non western','Asian, non western'
                      
   # Filter data 
   verbose_filter(mri_consent_f09 == "yes", t1_has_nii_f09 == "yes", t1_asset_has_nii_f09 != "exclude", 
                  has_braces_mri_f09 == "no", exclude_incidental_f09 == "include", freesurfer_qc_f09 == "usable", qdec_has_lgi_f09 == "yes", 
                  twin == 0, pre_percent_missing < 50, post_percent_missing < 50)  %>%
   
   # Rename some variables for easier reading
   rename(., any_of(c(age = "age_child_mri_f09", 
                      prenatal_smoking = "m_smoking", 
                      prenatal_alcohol = "m_drinking", 
                      mean_cortical_thickness_lh = "lh_MeanThickness_f09", 
                      mean_cortical_thickness_rh = "rh_MeanThickness_f09")))
   

els_brain_sample$educ_m <- factor(els_brain_sample$data$educ_m, levels = c(0,1,2,3,4,5), labels = c("no_education","primary", "seconday, phase 1","secondary, phase 2", "higher, phase 1", "higher, phase 2")) 

# Sex 
els_brain_sample$sex <- with(els_brain_sample, factor(sex, levels = c(1,2), labels = c("male", "female")))

# Checking output
# table(long.data$ethn_cont, long.data$ethnicity, useNA="ifany")

# check <- long.data %>%
#    group_by(.imp) %>%
#    summarize_at(c("ethnicity", "age"), function(x) sum(is.na(x)) )

# Convert back to mids
sample <- as.mids(long.data)

select_sibling <- function(dt, column_selection = c(), random = T, seed = 31081996, mother_id = 'mother', child_id = 'IDC') {
  # if no selection is specified, missingness in the entire dataframe is used
  if (length(column_selection) > 0) { dt <- dt[, c(child_id, mother_id, column_selection)] } 
  # First randomly shuffle the dataset 
  set.seed(seed)
  dt <- dt[sample(nrow(dt)),]
  # Get rid of empty NA values for mother
  dt <- dt[!is.na(dt[,mother_id]),]
  # Determine a list of children that have a sibling in the set
  if (random==T) { 
    sibling_ids <- dt[duplicated(dt[, mother_id]), child_id] # i.e.  which mother IDs recur more than once
  } else {
    dt$missing <- rowSums(is.na(dt)) # compute how many missing values in the columns of interest 
    dt_ord <- dt[order(dt$missing),] # order based on number of missing 
    sibling_ids <- dt_ord[duplicated(dt_ord[, mother_id]), child_id] # selection
  }
  # message(length(sibling_ids), ' siblings identified.')
  return(sibling_ids)
}

sibs_to_include <- select_sibling(complete(els_brain, action=0))


els_brain_sample8 <- filter(els_brain_sample7, !IDC %in% sibs_to_include)
length(els_brain_sample8$data$IDC)

##########################################################
#Descriptives

#Missing ELS scores 
els_brain_sample12$nmis['post_life_events']
els_brain_sample12$nmis['post_contextual_risk']
els_brain_sample12$nmis['post_parental_risk']
els_brain_sample12$nmis['post_interpersonal_risk']
els_brain_sample12$nmis['post_direct_victimization']

# Proportion of missing ELS items 
length(which(between(els_brain_sample12$data$post_percent_missing, 0, 10) == TRUE))
length(which(between(els_brain_sample12$data$post_percent_missing, 10, 20) == TRUE))
length(which(between(els_brain_sample12$data$post_percent_missing, 20, 30) == TRUE))
length(which(between(els_brain_sample12$data$post_percent_missing, 30, 40) == TRUE))
length(which(between(els_brain_sample12$data$post_percent_missing, 40, 50) == TRUE))
length(which(between(els_brain_sample12$data$post_percent_missing, 50, 60) == TRUE))



###########################################################################


# Education

saveRDS(els_brain_sample, '/home/r095290/datin_ELS/scripts/els_brain_sample.rds')

#mother education 
table(els_brain_sample12$data$educm)




