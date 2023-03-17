from datetime import datetime as dt

# Year parameters for data generation
current = dt.now().year

# Year parameters for training
start_year = 1993
end_year = dt.now().year-1

# Year parameters for prediction
pred_year = dt.now().year

# Files for training
train_data_dir = "train_data"
scaler_fp = f"{train_data_dir}/scaler.pkl"
season_ref = f"{train_data_dir}/season-0.9-{start_year}-{current}.csv"
tourney_ref = f"{train_data_dir}/tourney-0.9-{start_year}-{end_year}.csv"

# Models for predicting
nn_model = 'saved/model3.h5'
rf_model = 'saved/model6.obj'
lr_model = 'saved/model7.obj'
