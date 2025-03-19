import ast
from collections import defaultdict
import os
import pandas as pd
import numpy as np

from mm_modeling.params import defs
from utils.globs import *
from utils.globs import women
from utils import globs


# Data parameters
missing = 0.9

class_map = defaultdict(lambda: np.nan)
class_map["FR"] = 1
class_map["SO"] = 2
class_map["JR"] = 3
class_map["SR"] = 4

if women:
    sfilename = os.path.join(defs.DATA_DIR,"women_season_clean.csv")
    tfilename = os.path.join(defs.DATA_DIR,"women_tourney_clean.csv")
else:
    sfilename = os.path.join(defs.DATA_DIR,"season_clean.csv")
    tfilename = os.path.join(defs.DATA_DIR,"tourney_clean.csv")

def load():
    season, tourney = None, None
    try:
        print('Loading season data from file %s' % (sfilename))
        season = pd.read_csv(sfilename)
    except:
        print('Error: Could not read file %s' % (sfilename))

    try:
        print('Loading tourney data from file %s' % (tfilename))
        tourney = pd.read_csv(tfilename)
    except:
        print('Error: Could not read file %s' % (tfilename))
    
    return season, tourney

def create_season_train_data(season):
    # Feature processing
    season = build_is_ass(season)
    season = unpack_player_stats(season)
    season = drop_meta_cols(season)

    # Column filtering and preprocessing
    season = season.loc[:, season.isnull().sum() < missing*len(season)]
    season = missing_vals(season)

    # Export season training data
    if not os.path.exists(defs.TRAIN_DATA_DIR):
        os.makedirs(defs.TRAIN_DATA_DIR)

    print(f"Outputting season map to {os.path.join(defs.TRAIN_DATA_DIR,globs.season_ref)}")
    season.to_csv(os.path.join(defs.TRAIN_DATA_DIR,globs.season_ref), index=False)


def create_tourney_train_data(tourney):
    # NOTE: Add code to select season lookup table

    try:
        season = pd.read_csv(globs.season_ref)
    except:
        print("Error: could not load file " + globs.season_ref + ". Make sure file is created using 'create_season_train_data' function")
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
    if not os.path.exists(defs.TRAIN_DATA_DIR):
        os.makedirs(defs.TRAIN_DATA_DIR)

    print(f"Outputting train data to {os.path.join(defs.TRAIN_DATA_DIR,globs.tourney_ref)}")
    table.to_csv(os.path.join(defs.TRAIN_DATA_DIR,globs.tourney_ref), index=False)

def create_sample(season,year,school,opponent):
    sch = season[(season['Year']==year) 
        & (season['_School']==school[0])].copy()
    sch.drop(columns=['Year','_School'],axis=1,inplace=True)

    opp = season[(season['Year']==year) 
        & (season['_School']==opponent[0])].copy()
    opp.drop(columns=['Year','_School'],axis=1,inplace=True)

    match = [school[1],opponent[1]]
    #match = [1,1]

    return np.concatenate((sch, opp, match), axis=None)

def missing_vals(data):
    #print_missing_percentages(data)
    data.fillna(data.mean(),inplace=True)
    print("Dataset has nans: ",data.isna().values.any())

    return data

def print_missing_percentages(table):
    missing = table.isnull().sum()/len(table)*100
    for col,val in missing.items():
        print(col,val)

def drop_meta_cols(df):
    cols_to_drop = df.filter(regex='_\xa0|Unnamed|player_stats').columns
    df = df.drop(cols_to_drop, axis=1)
    return df

def unpack_player_stats(df):
    df[["avg_height", "avg_class"]] = df.player_stats.apply(lambda x: pd.Series(parse_roster_table(x)))
    return df

def build_is_ass(df):
    df["is_ass"] = df._School.apply(lambda x: True if x in ["Virginia", "Purdue"] else False)
    return df

def parse_roster_table(x):
    roster_table = ast.literal_eval(x)[0].get("Roster Table", {})

    heights = roster_table.get("Height", [])
    if len(heights) >= 6:
        avg_height = get_avg_height(heights)
    else:
        avg_height = np.nan
    
    classes = roster_table.get("Class", [])
    if len(classes) >= 7:
        avg_class = get_avg_class(classes)
    else:
        avg_class = np.nan
    
    return avg_height, avg_class

def get_avg_height(heights):
    h, cnt = 0, 0
    for i in heights[:5]: # Starting lineup + 6th man only
        split_h = i.split("-")
        if len(split_h) == 2:
            ft = split_h[0]
            inch = split_h[1]
            h += int(ft)*12+int(inch) 
            cnt += 1
    return h/cnt

def get_avg_class(classes):
    c, cnt = 0, 0
    for i in classes[:7]: # 7 players with highest minutes avg
        if len(i) > 0:
            c += class_map[i]
            cnt += 1
    return c/cnt

def main():
    season, tourney = load()
    if not season is None:
        create_season_train_data(season)
    if not tourney is None:
        create_tourney_train_data(tourney)

if __name__ == "__main__":
    main()
