from datetime import datetime as dt

from mm_modeling.params import defs

# Women's data
women = 0

# Year parameters for data generation
current = dt.now().year

# Year parameters for training
start_year = 1993
#end_year = 2024 #No tourney data after 2024
end_year = dt.now().year-1

# Year parameters for prediction
if women:
    pred_year = "w"+str(dt.now().year)
else:
    pred_year = dt.now().year

# Files for training/predicting
train_data_dir = defs.TRAIN_DATA_DIR
scaler_fp = f"{train_data_dir}/scaler.pkl"
if women:
    season_ref = f"{train_data_dir}/women-season-0.9-2023-{current}.csv"
else:
    season_ref = f"{train_data_dir}/season-0.9-{start_year}-{current}.csv"
tourney_ref = f"{train_data_dir}/tourney-0.9-{start_year}-{end_year}.csv"

# Models for predicting
# OG
#nn_model = 'saved/model9.h5'
#rf_model = 'saved/model21.obj'
#lr_model = 'saved/model22.obj'

nn_model = 'saved/model11.h5'
rf_model = 'saved/model23.obj'
lr_model = 'saved/model24.obj'
