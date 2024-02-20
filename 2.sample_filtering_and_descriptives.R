library(haven)
library(mice)
library(dplyr)               
  
els_brain <- readRDS(file.choose())
# els_brain <- readRDS('/home/r095290/datin_ELS/scripts/els_brain.rds')

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

imps <- readRDS('/home/r095290/datin_ELS/imputation_list_full.rds')


sibs_to_include <- select_sibling(complete(imps, action=0), random=T, mother_id='mother', child_id='IDC')

els_brain <- readRDS('./els_brain.rds')
els_brain_sample <- filter(els_brain,mri_consent_f09 == "yes")
length(els_brain_sample$data$mri_consent_f09)

els_brain_sample1 <- filter(els_brain_sample, t1_has_nii_f09 == "yes")
length(els_brain_sample1$data$t1_has_nii_f09)

els_brain_sample2 <- filter(els_brain_sample1, t1_asset_has_nii_f09 != "exclude")
length(els_brain_sample2$data$t1_asset_has_nii_f09)

els_brain_sample3 <- filter(els_brain_sample2, has_braces_mri_f09 == "no")
length(els_brain_sample3$data$has_braces_mri_f09)

els_brain_sample4 <- filter(els_brain_sample3, exclude_incidental_f09 == "include")
length(els_brain_sample4$data$exclude_incidental_f09)

els_brain_sample5 <- filter(els_brain_sample4, freesurfer_qc_f09 == "usable")
length(els_brain_sample5$data$freesurfer_qc_f09)

els_brain_sample6 <- filter(els_brain_sample5, qdec_has_lgi_f09 == "yes")
length(els_brain_sample6$data$qdec_has_lgi_f09)

els_brain_sample7 <- filter(els_brain_sample6, twin == 0)
length(els_brain_sample7$data$twin)

els_brain_sample8 <- filter(els_brain_sample7, !IDC %in% sibs_to_include)
length(els_brain_sample8$data$IDC)

els_brain_sample9 <- filter(els_brain_sample8, pre_percent_missing < 50)
length(els_brain_sample9$data$IDC)

els_brain_sample10 <- filter(els_brain_sample9, post_percent_missing < 50)
length(els_brain_sample10$data$IDC)

els_brain_sample11 <- filter(els_brain_sample10, !is.na(age_child_mri_f09 == "TRUE"))
length(els_brain_sample11$data$IDC)

els_brain_sample12 <- filter(els_brain_sample11, !is.na(ethn_cont == "TRUE"))
length(els_brain_sample12$data$ethn_cont)

##########################################################
#Descriptives

#Ethnicity
els_brain_sample12$data$ethninf_3gLab <- with(els_brain_sample12$data, factor( ifelse(ethn_cont == 'Dutch',  'Dutch', ifelse(ethn_cont %in% c('European'), 'other European', 'non-European' )))) # NOTE: non-European = 'Indonesian','American, western', 'Asian, western', 'Oceanie','Cape Verdian','Moroccan','Dutch Antilles','Surinamese','Turkish','African','American, non western','Asian, non western'
table(els_brain_sample12$data$ethninf_3gLab)
length(els_brain_sample12$data$ethn_cont)
table(els_brain_sample12$data$ethn_cont)

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





