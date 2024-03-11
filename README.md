# ELS-GWC-project
Vertex-wise associations between early-life stress (ELS) exposure during gestation and during childhood, and gray-white matter boundary contrast (GWC) in early adolescence.

## Analytical pipeline 
 - **`1.els_brain_merge.R`**: reads the imputed ELS data mids object [ imputation procedure described in Defina et al. (2023)] and merges it with the necessary neuroimaging metadata
 - **`2.clean_and_filter.R`**: recode or rename variables, and perform sample selection
 - **`3.qdecr_analyses.R`**: main analyses = vertex-wise associations between each ELS exposure of interest and GWC.
These steps were run in sequence using `run_pipeline.sh`.
 - **`4.figures.ipynb`**: jupyter notebook used to generate the figures included in the manuscript. 

## 3D brain surface maps
Interactive 3D brain surface maps representing the associations examined in this project can be visualized using this [web application](https://seredef.shinyapps.io/brainmapp2/). 

### Running the application locally 
The 3D brain surface reconstructions (especially the high-resolution ones) may be faster to compute on your local machine. 
To run the application locally (assuming a UNIX system with Python installed):
```
git clone https://github.com/SereDef/ELS-GWC-project
cd src_shiny_app
pip install -r requirements.txt

shiny run --launch-browser app.py
```
