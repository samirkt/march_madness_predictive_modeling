from preprocess import create_sample
import keras
import pandas as pd
import numpy as np
import pickle
import sys, os

[
    [
        [
            [[[("Duke",1),
            ("North Dakota State",16)],

            [("VCU",8),
            ("UCF",9)]],

            [[("Mississippi State",5),
            ("Liberty",12)],

            [("Virginia Tech",4),
            ("Saint Louis",13)]]],


            [[[("Maryland",6),
            ("Belmont",11)],

            [("LSU",3),
            ("Yale",14)]],

            [[("Louisville",7),
            ("Minnesota",10)],

            [("Michigan State",2),
            ("Bradley",15)]]]
        ],

        [
            [[[("Gonzaga",1),
            ("Fairleigh Dickinson",16)],

            [("Syracuse",8),
            ("Baylor",9)]],

            [[("Marquette",5),
            ("Murray State",12)],

            [("Florida State",4),
            ("Vermont",13)]]],


            [[[("Buffalo",6),
            ("Arizona State",11)],

            [("Texas Tech",3),
            ("Northern Kentucky",14)]],

            [[("Nevada",7),
            ("Florida",10)],

            [("Michigan",2),
            ("Montana",15)]]]
        ]
    ],

    [
        [
            [[[("Virginia",1),
            ("Gardner-Webb",16)],

            [("Ole Miss",8),
            ("Oklahoma",9)]],

            [[("Wisconsin",5),
            ("Oregon",12)],

            [("Kansas State",4),
            ("UC-Irvine",13)]]],


            [[[("Villanova",6),
            ("Saint Mary's",11)],

            [("Purdue",3),
            ("Old Dominion",14)]],

            [[("Cincinnati",7),
            ("Iowa",10)],

            [("Tennessee",2),
            ("Colgate",15)]]]
        ],

        [
            [[[("UNC",1),
            ("Iona",16)],

            [("Utah State",8),
            ("Washington",9)]],

            [[("Auburn",5),
            ("New Mexico State",12)],

            [("Kansas",4),
            ("Northeastern",13)]]],


            [[[("Iowa State",6),
            ("Ohio State",11)],

            [("Houston",3),
            ("Georgia State",14)]],

            [[("Wofford",7),
            ("Seton Hall",10)],

            [("Kentucky",2),
            ("Abilene Christian",15)]]]
        ]
    ]
]

def load():
   return pd.read_csv("train_data/season-0.9-0-1993-2021.csv")
   
def nn_predict(sample):
    model = keras.models.load_model('saved/model3.h5')
    return model.predict(sample)

def rf_predict(sample):
    model = pickle.load(open('saved/model0.obj', 'rb'))
    return model.predict_proba(sample)

def lr_predict(sample):
    model = pickle.load(open('saved/model1.obj', 'rb'))
    return model.predict_proba(sample)

def main():
    season = load()
    #match = create_sample(season,2019,('UNC',1),('Iona',16))
    #match = create_sample(season,2019,('Iona',16),('UNC',1))
    match = create_sample(season,2021,('Baylor',1),('Hartford',16))
    print(len(match))
    
    print(nn_predict([[match]]))
    print(rf_predict([match])[0][1])
    print(lr_predict([match])[0][1])

    match = create_sample(season,2021,('Hartford',16),('Baylor',1))
    print(len(match))
    
    print(nn_predict([[match]]))
    print(rf_predict([match])[0][1])
    print(lr_predict([match])[0][1])


if __name__ == "__main__":
    main()
