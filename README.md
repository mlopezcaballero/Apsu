apsu
==============================

Aguathon: Modelizar el comportamiento del río Ebro para predecir posibles riadas e inundaciones.

Create environment
------------
1. Create environmen:

    `make environment`

2. Activate environment:

    `source activate apsu`
    
3. Intstall required packages:

    `make requirements`
    
4. Create data set:

5. Train the model:

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- External data
    │   ├── interim        <- 
    │   ├── AEMET          <- Data from AEMET.
    │   └── SAIHEBRO.      <- Data from SAIHEBRO.
    │
    ├── ENTRADA            <- Original data, from Aragon government.
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-mlc-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │   ├── biblio         <- Bibliography 
    │   └── info           <- Information about the challenge
    │
    ├── SALIDA             <- Data output with the results.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    └── src                <- Source code for use in this project.
        ├── __init__.py    <- Makes src a Python module
        │
        ├── data           <- Scripts to download or generate data
        │   └── make_dataset.py
        │
        ├── features       <- Scripts to turn raw data into features for modeling
        │   └── build_features.py
        │
        ├── models         <- Scripts to train models and then use trained models to make
        │   │                 predictions
        │   ├── predict_model.py
        │   └── train_model.py
        │
        └── visualization  <- Scripts to create exploratory and results oriented visualizations
            └── visualize.py


