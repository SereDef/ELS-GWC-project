library(QDECR)
dataFrame <- readRDS('/home/r095290/datin_ELS/scripts/els_brain_sample.rds')

# Model 8: Thickness
out <- qdecr_fastlm(qdecr_w_g.pct ~ lh_MeanThickness_f09 + age_child_mri_f09 + sex,
                    data = dataFrame,
                    id = "folders_f09",
                    hemi = "lh",
                    project = "thickness",
                    clobber = TRUE,
                    n_cores = 2,
                    dir_tmp = "/dev/shm")

out <- qdecr_fastlm(qdecr_w_g.pct ~ rh_MeanThickness_f09 + age_child_mri_f09 + sex,
                    data = dataFrame,
                    id = "folders_f09",
                    hemi = "rh",
                    project = "thickness",
                    clobber = TRUE,
                    n_cores = 2,
                    dir_tmp = "/dev/shm")