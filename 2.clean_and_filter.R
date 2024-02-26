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
                      if_else(ethn_cont=="European", "other European", "non-European"))),
                      # NOTE: non-European = 'Indonesian','American, western','Asian, western','Oceanie','Cape Verdian','Moroccan','Dutch Antilles','Surinamese','Turkish','African','American, non western','Asian, non western'
          sex = factor(sex, labels=c("Male", "Female")),
          postnatal_stress_cat = relevel(cut(postnatal_stress, quantile(postnatal_stress, na.rm=TRUE)[-3], include.lowest=TRUE, 
                                            labels=c("Low","Medium","High")), ref="Medium"),
          prenatal_stress_cat = relevel(cut(prenatal_stress, quantile(prenatal_stress, na.rm=TRUE)[-3], include.lowest=TRUE, 
                                            labels=c("Low","Medium","High")), ref="Medium")) %>%
                                            
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
   

# Check transformations and missing values 
# table(long.data$ethn_cont, long.data$ethnicity, useNA="ifany")

# check <- long.data %>% group_by(.imp) %>%
#    summarize_at(c("postnatal_stress_cat","prenatal_stress_cat"), summary)
#    summarize_at(c("ethnicity", "age", "maternal_education"), function(x) sum(is.na(x)) )
# print(check, n=31)

# Subset siblings
select_sibling <- function(dt, column_selection = c(), random = TRUE, seed = 31081996, mother_id = 'mother', child_id = 'IDC') {
  # if no selection is specified, missingness in the entire dataframe is used
  if (length(column_selection) > 0) { dt <- dt[, c(child_id, mother_id, column_selection)] } 
  # First randomly shuffle the dataset 
  set.seed(seed)
  dt <- dt[sample(nrow(dt)),]
  # Get rid of empty NA values for mother
  dt <- dt[!is.na(dt[,mother_id]),]
  # Determine a list of children that have a sibling in the set
  if (random) { 
    sibling_ids <- dt[duplicated(dt[, mother_id]), child_id] # i.e.  which mother IDs recur more than once
  } else {
    dt$missing <- rowSums(is.na(dt)) # compute how many missing values in the columns of interest 
    dt_ord <- dt[order(dt$missing, decreasing=FALSE),] # order based on number of missing (less missing first)
    sibling_ids <- dt_ord[duplicated(dt_ord[, mother_id]), child_id] # selection the child with more missings
  }
  message(length(sibling_ids), ' siblings identified.')
  return(sibling_ids)
}

sibs_to_exclude <- long.data %>%
   filter(.imp == 0) %>%  # original dataset 
   select_sibling()

final_sample <- long.data %>% 
   # Remove 1 of each sibling couple
   verbose_filter(!IDC %in% sibs_to_exclude)  %>% 
   # Convert back to mids
   mice::as.mids()

cat('\n\nSaving mids...')
# Save output
saveRDS(final_sample, '../Data/ELS_brain_sample.rds')

cat('\nDone!')
##########################################################
#Descriptives Datin

#Missing ELS scores 
#els_brain_sample12$nmis['post_life_events']
#els_brain_sample12$nmis['post_contextual_risk']
#els_brain_sample12$nmis['post_parental_risk']
#els_brain_sample12$nmis['post_interpersonal_risk']
#els_brain_sample12$nmis['post_direct_victimization']

# Proportion of missing ELS items 
#length(which(between(els_brain_sample12$data$post_percent_missing, 0, 10) == TRUE))
#length(which(between(els_brain_sample12$data$post_percent_missing, 10, 20) == TRUE))
#length(which(between(els_brain_sample12$data$post_percent_missing, 20, 30) == TRUE))
#length(which(between(els_brain_sample12$data$post_percent_missing, 30, 40) == TRUE))
#length(which(between(els_brain_sample12$data$post_percent_missing, 40, 50) == TRUE))
#length(which(between(els_brain_sample12$data$post_percent_missing, 50, 60) == TRUE))

###########################################################





