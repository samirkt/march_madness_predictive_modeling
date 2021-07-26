import pandas as pd
import numpy as np
from utils.globs import *
import os


# Data parameters
missing = 0.9
fill = 0


def load():
    try:
        sfilename = "../data/season/1993_to_"+str(current)+"_season_clean.csv"
        print('Loading season data from file %s' % (sfilename))
        season = pd.read_csv(sfilename)
    except:
        print('Error: Could not read file %s' % (sfilename))

    try:
        tfilename = "../data/tourney/1993_to_"+str(current)+"_tourney.csv"
        print('Loading tourney data from file %s' % (tfilename))
        tourney = pd.read_csv(tfilename)
    except:
        print('Error: Could not read file %s' % (tfilename))
    
    return season, tourney

def create_season_train_data(season):
    # Column filtering and preprocessing
    season = season.loc[:, season.isnull().sum() < missing*len(season)]
    season = missing_vals(season,fill)

    # Export season training data
    data_dir = 'train_data/'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    name = 'season-' + str(missing) + '-' + str(fill) + '-1993-'+str(current)+'.csv'

    season.to_csv(data_dir + name, index=False)


def create_tourney_train_data(tourney):
    # NOTE: Add code to select season lookup table

    season_file = 'train_data/season-' + str(missing) + '-' + str(fill) + '-1993-'+str(current)+'.csv'
    try:
        season = pd.read_csv(season_file)
    except:
        print("Error: could not load file " + season_file + ". Make sure file is created using 'create_season_train_data' function")
        quit()

    tourney = tourney[['Year','Round','school_seed','School','opponent_seed','Opponent','PTS','PTS.1']]

    # NOTE: IF CATEGORIZING ROUNDS, the round names are not consistent in the data. Dropping for now..
    #tourney['Round'] = pd.Categorical(tourney['Round'],ordered=True,categories=['First Four','First Round','Second Round','Regional Semifinal','Regional Final','National Semifinal','National Final'])
    #tourney['Round'] = tourney['Round'].cat.codes

    data = []
    for index, match in tourney.iterrows():
        # Check year range
        if not start_year <= match['Year'] <= end_year:
            continue

        # Set target variables
        if match['PTS'] > match['PTS.1']:
            targ1 = 1
            targ2 = 0
        else:
            targ1 = 0
            targ2 = 1

        # Create samples
        row1 = create_sample(season,
                match['Year'],
                (match['School'],match['school_seed']),
                (match['Opponent'],match['opponent_seed'])
                )
                
        row2 = create_sample(season,
                match['Year'],
                (match['Opponent'],match['opponent_seed']),
                (match['School'],match['school_seed'])
                )

        data_row1 = np.concatenate((row1,targ1), axis=None)
        data_row2 = np.concatenate((row2,targ2), axis=None)

        data.append(data_row1)
        data.append(data_row2)

    cols = np.concatenate((range(len(data[0])-1),['target']), axis=None)
    table = pd.DataFrame(columns=cols,data=data)

    # Export tourney training data
    data_dir = 'train_data/'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    name = 'tourney-' + str(missing) + '-' + str(fill) + '-' + str(start_year) + '-' + str(end_year) + '.csv'

    table.to_csv(data_dir + name, index=False)
    #table.to_csv('train_data/test.csv')

def create_sample(season,year,school,opponent):
    sch = season[(season['Year']==year) 
        & (season['_School']==school[0])]
    sch.drop(['_School'],axis=1,inplace=True)

    opp = season[(season['Year']==year) 
        & (season['_School']==opponent[0])]
    opp.drop(['_School'],axis=1,inplace=True)

    match = [school[1],opponent[1]]

    return np.concatenate((sch, opp, match), axis=None)


def missing_vals(data,fill):
    #print_missing_percentages(data)
    data.fillna(fill,inplace=True)
    print("Dataset has nans: ",data.isna().values.any())

    return data

def print_missing_percentages(table):
    missing = table.isnull().sum()/len(table)*100
    for col,val in missing.items():
        print(col,val)
    
def main():
    season, tourney = load()
    create_season_train_data(season)
    create_tourney_train_data(tourney)

if __name__ == "__main__":
    main()
