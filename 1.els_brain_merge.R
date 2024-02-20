library(mice)
library(haven)


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
############################################################################

genrpath <- '/mnt/data/genr/mrdata/GenR_MRI/summary_data'

# Core data for selection
core <- readRDS(file.path(genrpath, 'core/genr_mri_core_data_20221220.rds'))
core <- core[, -grep('f05', names(core))] # get rid of F05 wave ( bit quicker :))

# Anatomical data Focus @9
vols <- readRDS(file.path(genrpath, 'F09/anat/freesurfer/6.0.0/f09_freesurfer_v6_09dec2016_tbv_stats_pull20june2017_v2.rds'))

# Imputed ELS set
imps <- readRDS('/home/r095290/datin_ELS/imputation_list_full.rds')

# Select siblings 
sibs_to_include <- select_sibling(complete(imps, action=0), random=T, mother_id='mother', child_id='IDC')

# Merge maternal education file containing more specific levels 
corePhen <- '/mnt/data/genr/users/rmuetzel/forDatin/qdecr/CHILD-ALLGENERALDATA_29012018.sav'

educ_m <- read_sav(corePhen)[, c('IDC','EDUCM')]
names(educ_m) <- tolower(names(educ_m))

brain <- merge(core, vols, by='idc', all.x=T)

brain <- merge(brain, educ_m, by='idc', all.x=T) # keep full cohort

print(summary(as.factor(brain$educ_m)))

# message(paste(names(brain), collapse='\n'))
# Check dimentions
cat('Data dimention:')
cat('\ncore', dim(core))
cat('\nvols', dim(vols))

cat('\nTotal brain', dim(brain))
cat('\nImputed ELS', dim(imps$data),'\n')

# Check IDC overlap 
cat('\nIDC overlap ? ') 
identical(imps$data$IDC, brain$idc)
setdiff(imps$data$IDC, brain$idc)

# Re-order
cat('\nMatching IDC...')
brain <- brain[match(imps$data$IDC, brain$idc), ]

# Check IDC overlap again
cat('\nIDC overlap ? ') 
identical(imps$data$IDC, brain$idc)

###########################################################################

# Simple merge: cbind long format and replicated dataset
els_long <- complete(imps, action='long', include=T)
brainrep <- do.call("rbind", replicate(31, brain, simplify = F)) # 30 imputed sets + 1 original data 

#cat('\nlongi', dim(els_long))
#cat('\nbrain', dim(brainrep))
cat('\nMerging sets...')
els_brain <- cbind(els_long, brainrep)

# Check IDC overlap again
cat('\nIDC overlap ? ') 
identical(els_brain$IDC, els_brain$idc)

# summary(els_brain[els_brain$.imp==2,]) # summary of a random set 

# Transforma back to mids and save
cat('\nSaving mids...')
output <- as.mids(els_brain)
print(output$loggedEvents)

saveRDS(output, '/home/r095290/datin_ELS/scripts/els_brain.rds')

###########################################################################

# Filter participants 
els_brain_sample <- filter(output, mri_consent_f09 == "yes" & t1_has_nii_f09 == "yes" & 
                             t1_asset_has_nii_f09 != "exclude" & has_braces_mri_f09 == "no" & 
                             exclude_incidental_f09 == "include" & freesurfer_qc_f09 == "usable" & 
                             qdec_has_lgi_f09 == "yes" & twin == 0 & 
                             !IDC %in% sibs_to_include & 
                             pre_percent_missing < 50 & post_percent_missing < 50 & 
                             !is.na(age_child_mri_f09 == "TRUE") & !is.na(ethn_cont == "TRUE"))

print(dim(els_brain_sample$data))

## Define variables as factors

# Ethnicity
els_brain_sample$data$ethninf_3gLab <- with(els_brain_sample$data, factor( ifelse(ethn_cont == 'Dutch',  'Dutch', ifelse(ethn_cont %in% c('European'), 'other European', 'non-European' )))) # NOTE: non-European = 'Indonesian','American, western', 'Asian, western', 'Oceanie','Cape Verdian','Moroccan','Dutch Antilles','Surinamese','Turkish','African','American, non western','Asian, non western'

# Education
els_brain_sample$educ_m <- factor(els_brain_sample$data$educ_m, levels = c(0,1,2,3,4,5), labels = c("no_education","primary", "seconday, phase 1","secondary, phase 2", "higher, phase 1", "higher, phase 2")) 

# Sex 
els_brain_sample$sex <- with(els_brain_sample, factor(sex, levels = c(1,2), labels = c("male", "female")))

saveRDS(els_brain_sample, '/home/r095290/datin_ELS/scripts/els_brain_sample.rds')

#mother education 
table(els_brain_sample12$data$educm)

