"""Model inference and prediction voting."""

from preprocess import create_sample
from utils.globs import *
from utils.globs import scaler_fp
from utils.brackets import *
import keras
import pandas as pd
import numpy as np
import pickle
import sys, os

from mm_modeling.model.gen_matrix import gen_mat
from mm_modeling.model.conditional_projections import project

pd.options.mode.chained_assignment = None
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



class Models(object):
    def __init__(self):
        self.nn_model = keras.models.load_model(nn_model)
        self.rf_model = pickle.load(open(rf_model, 'rb'))
        self.lr_model = pickle.load(open(lr_model, 'rb'))

        with open(scaler_fp, 'rb') as f:
            self.scaler = pickle.load(f)
        
        self.season_data = pd.read_csv(season_ref)

    def nn_predict(self,sample):
        return self.nn_model.predict(sample, verbose=0)

    def rf_predict(self,sample):
        return self.rf_model.predict_proba(sample)

    def lr_predict(self,sample):
        return self.lr_model.predict_proba(sample)

    def predict(self,sample):
        nn = rf = lr = np.nan

        # Fit sample values, don't need to convert to values
        # because sample is already np.array
        sample = self.scaler.transform([sample])

        nn = self.nn_predict(sample)[0][0]
        rf = self.rf_predict(sample)[0][1]
        lr = self.lr_predict(sample)[0][1]

        return [np.nanmean([nn,rf,lr]),nn,rf,lr]

    def display_pred(self,preds,school):
        print("{0} {1}:".format(school[1],school[0]))
        print("\t{0:0.2f}".format(preds[0]))
        print("\n\t{0:0.2f}\n\t{1:0.2f}\n\t{2:0.2f}\n".format(
            preds[1],
            preds[2],
            preds[3]
            ))

    def pick(self, bracket, year):
        season = self.season_data

        i = 0
        while len(bracket) > 1:
            # Get school matchup
            school1 = bracket[i]
            school2 = bracket[i+1]

            # Predict for school 1
            prediction1 = self.predict(create_sample(season,year,school1,school2))
            self.display_pred(prediction1,school1)

            # Predict for school 2
            prediction2 = self.predict(create_sample(season,year,school2,school1))
            self.display_pred(prediction2,school2)

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
            

def main(conditional=True):
    m = Models()
    bracket = brackets[pred_year]
    year = int(str(pred_year)[-4:]) # ignore w if running womens

    if not conditional:
        m.pick(bracket, year)
    else:
        mat = gen_mat(m, bracket, year, save_fp=os.path.join(defs.DATA_DIR,f"{str(pred_year)}_mat.csv"))
        project(mat, bracket)


    
if __name__ == "__main__":
    main()
