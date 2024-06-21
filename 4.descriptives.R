# DESCRIPTIVES FOR TABLE 1 ==============================================================================

# Setup 
library(mice)
library(dplyr)

project_dir <- "/home/r057600/ELS_ICM"
setwd(project_dir)

# sample <- readRDS(file.choose())
sample <- readRDS(file.path(project_dir, "Data/ELS_brain_sample.rds"))

print(cor(complete(sample,0)[c('prenatal_stress', 'postnatal_stress')], use='pairwise.complete.obs'))

preposcor <- miceadds::micombine.cor(sample, variables=c('prenatal_stress', 'postnatal_stress'))
print(preposcor)

ld <- mice::complete(sample, action = 'long', include = FALSE)

# Summary of continuous variables = median (min, max)
cont_summ <- function(cont_vars) {
  summ <- ld %>% 
    select(.imp, all_of(cont_vars)) %>%
    group_by(.imp) %>%
    summarise_all(list('med'=median, 'min'=min, 'max'=max), na.rm=TRUE) %>%
    summarise_at(vars(-.imp), mean) %>% 
    round(., 2) %>% 
    matrix(nrow=length(cont_vars), ncol=3, dimnames = list(cont_vars, c('med','min','max'))) %>% 
    as.data.frame() %>% transmute(levels = cont_vars, summary = paste0(med, ' (', min, ', ', max, ')'))
}

# Summary of categorical variables = n (%)
cate_summ <- function(cate_var) {
  summ <- ld %>% 
    select(.imp, !!as.name(cate_var)) %>%
    group_by(.imp) %>%
    count(!!as.name(cate_var)) %>% 
    group_by(!!as.name(cate_var)) %>% 
    summarise_at(vars(-.imp), mean) %>% 
    transmute(levels = paste(cate_var, !!as.name(cate_var)), 
              summary = paste0(round(n, 1), ' (', round((n / (nrow(ld)/30))*100, 1), '%)'))
}


summ1 <- cont_summ(c('prenatal_stress', 
                     'pre_life_events','pre_contextual_risk','pre_parental_risk','pre_interpersonal_risk',
                     'postnatal_stress', 
                     'post_life_events','post_contextual_risk','post_parental_risk','post_interpersonal_risk','post_direct_victimization', 
                     'age', 'mean_cortical_thickness_lh', 'mean_cortical_thickness_rh'))

summ2 <- do.call('rbind', lapply(c('sex', 'ethnicity', 'prenatal_smoking', 'prenatal_alcohol', 'm_education'), cate_summ))

total_summ <- rbind(summ1,summ2)

write.csv(total_summ, paste0(project_dir,'/Table1.csv'))


# Add complete dateset descriptives for supplement =======================================================================================
full_data <- readRDS(file.path(project_dir, "Data/ELS_brain.rds"))

cat(nrow(complete(full_data,0)))

ld <- mice::complete(full_data, action = 'long', include = FALSE) %>% 
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

   # Rename some variables for easier reading
   rename(., any_of(c(age = "age_child_mri_f09", 
                      prenatal_smoking = "m_smoking", 
                      prenatal_alcohol = "m_drinking", 
                      mean_cortical_thickness_lh = "lh_MeanThickness_f09", 
                      mean_cortical_thickness_rh = "rh_MeanThickness_f09")))

summ1_full <- cont_summ(c('prenatal_stress', 
                     'pre_life_events','pre_contextual_risk','pre_parental_risk','pre_interpersonal_risk',
                     'postnatal_stress', 
                     'post_life_events','post_contextual_risk','post_parental_risk','post_interpersonal_risk','post_direct_victimization', 
                     'age', 'mean_cortical_thickness_lh', 'mean_cortical_thickness_rh'))

summ2_full <- do.call('rbind', lapply(c('sex', 'ethnicity', 'prenatal_smoking', 'prenatal_alcohol', 'm_education'), cate_summ))

total_summ_full <- cbind(total_summ, rbind(summ1_full, summ2_full))

write.csv(total_summ_full, paste0(project_dir,'/SuppTable1.csv'))

