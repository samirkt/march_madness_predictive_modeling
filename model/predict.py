from preprocess import create_sample
from utils.globs import *
from utils.brackets import *
import keras
import pandas as pd
import numpy as np
import pickle
import sys, os

pd.options.mode.chained_assignment = None
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def load():
   return pd.read_csv(season_ref)
   
def nn_predict(sample):
    model = keras.models.load_model(nn_model)
    return model.predict(sample)

def rf_predict(sample):
    model = pickle.load(open(rf_model, 'rb'))
    return model.predict_proba(sample)

def lr_predict(sample):
    model = pickle.load(open(lr_model, 'rb'))
    return model.predict_proba(sample)

def predict(sample):
    nn = rf = lr = np.nan

    nn = nn_predict([[sample]])[0][0]
    rf = rf_predict([sample])[0][1]
    lr = lr_predict([sample])[0][1]

    return [np.nanmean([nn,rf,lr]),nn,rf,lr]

def display_pred(preds,school):
    print("{0} {1}:".format(school[1],school[0]))
    print("\t{0:0.2f}".format(preds[0]))
    print("\n\t{0:0.2f}\n\t{1:0.2f}\n\t{2:0.2f}\n".format(
        preds[1],
        preds[2],
        preds[3]
        ))

def pick(bracket):
    season = load()
    year = pred_year

    i = 0
    while len(bracket) > 1:
        # Get school matchup
        school1 = bracket[i]
        school2 = bracket[i+1]

        # Predict for school 1
        prediction1 = predict(create_sample(season,year,school1,school2))
        display_pred(prediction1,school1)

        # Predict for school 2
        prediction2 = predict(create_sample(season,year,school2,school1))
        display_pred(prediction2,school2)

        # Print pick and mark eliminated
        print(bracket[i + (prediction1[0] < prediction2[0])][0])
        bracket[i + (prediction1[0] > prediction2[0])] = None

        # Next matchup
        i += 2

        # Reset for next round
        if i >= len(bracket):
            i = 0
            bracket = [i for i in bracket if i]

        # Wait for input
        ex = input("\n\n")
        if ex: quit()
        

def main():
    pick(brackets[pred_year])

    
if __name__ == "__main__":
    main()
