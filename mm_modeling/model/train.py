from models import rf, lr, nn
from utils.globs import tourney_ref, scaler_fp, season_ref
import pandas as pd
import pickle
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


def main():
    x = pd.read_csv(tourney_ref,index_col=False)

    # Get target
    y = x.pop('target')

    # Split data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

    # Scale data and save scaler object
    scaler = MinMaxScaler()
    scaler.fit(x_train.values) # fit training x

    # Transform data based on scaler. Fit on values so that scaler
    # object does not expect column names in future inference
    x_train = scaler.transform(x_train.values)
    x_test = scaler.transform(x_test.values)

    with open(scaler_fp, 'wb') as f:
        pickle.dump(scaler, f)

    # Call model training methods
    data = (x_train, x_test, y_train, y_test)
    nn(data)
    rf(data)
    lr(data)

if __name__ == "__main__":
    main()

