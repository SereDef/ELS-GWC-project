library(QDECR)
dataFrame <- readRDS('/home/r095290/datin_ELS/scripts/els_brain_sample.rds')

hemis <- c('lh','rh')

for (hemi in hemis){

# Model 1: Postnatal Life Events  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ post_life_events + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "els_1",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm") 
                      
# Model 2: Postnatal Contextual Risk  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ post_contextual_risk + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "els_2",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm") 

# Model 3: Postnatal Parental Risk  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ post_parental_risk + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "els_3",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm") 
                      
# Model 4: Postnatal Interpersonal Risk  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ post_interpersonal_risk + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "els_4",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")

# Model 5: Postnatal Direct Victimization  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ post_direct_victimization + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "els_5",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")
                      
# Model 6: All ELS domains
out <- qdecr_fastlm(qdecr_w_g.pct ~ post_life_events + post_contextual_risk + post_parental_risk + post_interpersonal_risk + post_direct_victimization + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "els_6",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")
                      
# Model 7: Global ELS 
out <- qdecr_fastlm(qdecr_w_g.pct ~ postnatal_stress + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "els_global",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")
                      
# Model 8: Age Associations
out <- qdecr_fastlm(qdecr_w_g.pct ~ age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "age_associations",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")
                      
}