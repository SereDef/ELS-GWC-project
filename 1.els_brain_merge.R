library(mice)
library(foreign)

# =========================================================
# Setup 
project_dir <- "/home/r057600/ELS_ICM"

braind_path <- "/mnt/data/genr/mrdata/GenR_MRI/summary_data"

# Core data for selection
core <- readRDS(file.path(braind_path, 'core/genr_mri_core_data_20231204.rds'))
core <- core[, -grep('f05', names(core))] # get rid of F05 wave ( bit quicker :))

# Anatomical data Focus @9
vols <- readRDS(file.path(braind_path, 'F09/anat/freesurfer/6.0.0/f09_freesurfer_v6_09dec2016_tbv_stats_pull20june2017_v2.rds'))

# Check dimentions
cat('Data dimention:')
cat('\ncore', dim(core))
cat('\nvols', dim(vols))

brain <- merge(core, vols, by='idc', all.x=TRUE) # keep full cohort

# Merge maternal education file containing more specific levels 
educ_m <- foreign::read.spss('/mnt/data/genr/users/rmuetzel/forDatin/qdecr/CHILD-ALLGENERALDATA_29012018.sav', 
                             use.value.labels = TRUE, to.data.frame = TRUE)[, c('IDC','EDUCM')]
names(educ_m) <- c("idc", "maternal_education")

brain <- merge(brain, educ_m, by='idc', all.x=TRUE) # keep full cohort

cat('\nMaternal education:\n')
print(summary(brain$maternal_education))

# Imputed ELS set
imps <- readRDS(file.path(project_dir, 'Data/imputation_list_full.rds'))

# message(paste(names(brain), collapse='\n'))
cat('\nTotal brain', dim(brain))
cat('\nImputed ELS', dim(imps$data),'\n')

# Check IDC overlap 
cat('\nIDC overlap ? ') 
identical(imps$data$IDC, brain$idc)
setdiff(imps$data$IDC, brain$idc) # Are they just in different order?

# Re-order
cat('\nMatching IDC...')
brain <- brain[match(imps$data$IDC, brain$idc), ]

# Check IDC overlap again
cat('\nIDC overlap ? ') 
identical(imps$data$IDC, brain$idc)

# Simple merge: cbind long format and replicated dataset
els_long <- mice::complete(imps, action='long', include=TRUE)
brainrep <- do.call("rbind", replicate(31, brain, simplify = FALSE)) # 30 imputed sets + 1 original data 

#cat('\nlongi', dim(els_long))
#cat('\nbrain', dim(brainrep))
cat('\nMerging sets...')
els_brain <- cbind(els_long, brainrep)

# Check IDC overlap again
cat('\nIDC overlap ? ') 
identical(els_brain$IDC, els_brain$idc)

cat('\nIncluded variables:\n') 
message(paste(names(els_brain), collapse='\n'))

# summary(els_brain[els_brain$.imp==2,]) # summary of a random set 

# Transforma back to mids and save
cat('\nSaving mids...')
output <- as.mids(els_brain)
print(output$loggedEvents)

saveRDS(output, file=file.path(project_dir, 'Data/ELS_brain.rds'))

cat('\nDone!')

