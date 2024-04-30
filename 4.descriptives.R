
sample <- readRDS(file.choose())

library(mice)
library(dplyr)

ld <- complete(sample, action = 'long', include = FALSE)

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

cate_summ <- function(cate_var) {
  summ <- ld %>% 
    select(.imp, !!as.name(cate_var)) %>%
    group_by(.imp) %>%
    count(!!as.name(cate_var)) %>% 
    group_by(!!as.name(cate_var)) %>% 
    summarise_at(vars(-.imp), mean) %>% 
    transmute(levels = paste(cate_var, !!as.name(cate_var)), 
              summary = paste0(n, ' (', round((n / (nrow(ld)/30))*100, 1), '%)'))
}


summ1 <- cont_summ(c('prenatal_stress', 
                     'pre_life_events','pre_contextual_risk','pre_parental_risk','pre_interpersonal_risk',
                     'postnatal_stress', 
                     'post_life_events','post_contextual_risk','post_parental_risk','post_interpersonal_risk','post_direct_victimization'))

summ2 <- cate_summ('sex')

total_summ <- rbind(summ1,summ2)
