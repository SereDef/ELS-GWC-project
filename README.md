# ELS-GWC-project
Vertex-wise associations between early-life stress (ELS) exposure and gray-white matter boundary contrast (GWC) in early adolescence

## Analytical pipeline 
 - `1.els_brain_merge.R`: reads the imputed ELS data from Defina et al. (2023) and merges it with additional brain data
 - `2.sample_filter_and describe.R`: cleaning, sample selection and descriptives
 - `3.qdecr_loop.R`: main analyses (vertex-wise associations with each exposure of interest)
 - `4.qdecr_cortical_thickness.R`: additional analyses (ertex-wise associations with mean thickness)

## 3D brain surface maps
Interactive 3D brain surface maps representing the associations from this project can be visualized using this online application. 

### Running the application locally 
```
git clone https://github.com/SereDef/ELS-GWC-project
cd src_shiny_app
pip install -r requirements.txt

shiny run app.py
```
