library(QDECR)
dataFrame <- readRDS('/home/r095290/datin_ELS/scripts/els_brain_sample.rds')

hemis <- c('lh','rh')

for (hemi in hemis){
  
  # Model 1: Postnatal Life Events  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ pre_life_events + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "pre_els_1",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm") 
  
  # Model 2: Postnatal Contextual Risk  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ pre_contextual_risk + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "pre_els_2",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm") 
  
  # Model 3: Postnatal Parental Risk  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ pre_parental_risk + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "pre_els_3",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm") 
  
  # Model 4: Postnatal Interpersonal Risk  
  out <- qdecr_fastlm(qdecr_w_g.pct ~ pre_interpersonal_risk + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "pre_els_4",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")

  
  # Model 6: All ELS domains
  out <- qdecr_fastlm(qdecr_w_g.pct ~ pre_life_events + pre_contextual_risk + pre_parental_risk + pre_interpersonal_risk + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "pre_els_6",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")
  
  # Model 7: Global ELS 
  out <- qdecr_fastlm(qdecr_w_g.pct ~ prenatal_stress + age_child_mri_f09 + sex,
                      data = dataFrame,
                      id = "folders_f09",
                      hemi = hemi,
                      project = "pre_els_global",
                      clobber = TRUE,
                      n_cores = 2,
                      dir_tmp = "/dev/shm")
  
}