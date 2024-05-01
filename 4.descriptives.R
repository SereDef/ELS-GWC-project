# DESCRIPTIVES FOR TABLE 1 ==============================================================================

# Setup 
library(mice)
library(dplyr)

project_dir <- "/home/r057600/ELS_ICM"
setwd(project_dir)

# sample <- readRDS(file.choose())
sample <- readRDS(file.path(project_dir, "Data/ELS_brain_sample.rds"))


ld <- complete(sample, action = 'long', include = FALSE)

# Summary of continuous variables = median (min, max)
cont_summ <- function(cont_vars) {
  summ <- ld %>% 
    select(.imp, all_of(cont_vars)) %>%
    group_by(.imp) %>%
    summarise_all(list('med'=median, 'min'=min, 'max'=max)) %>%
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

summ2 <- do.call('rbind', lapply(c('sex', 'ethnicity', 'prenatal_smoking', 'prenatal_alcohol'), cate_summ))

total_summ <- rbind(summ1,summ2)

write.csv(total_summ, paste0(project_dir,'/Table1.csv'))


