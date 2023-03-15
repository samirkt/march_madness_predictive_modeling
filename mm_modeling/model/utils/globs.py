from datetime import datetime as dt

# Year parameters for data generation
current = dt.now().year

# Year parameters for training
start_year = 1993
end_year = 2021

# Year parameters for prediction
pred_year = dt.now().year

# Files for training
season_ref = "train_data/season-0.9-0-1993-2023.csv"
tourney_ref = "train_data/tourney-0.9-0-1993-2021.csv"

# Models for predicting
nn_model = 'saved/model0.h5'
rf_model = 'saved/model0.obj'
lr_model = 'saved/model1.obj'
