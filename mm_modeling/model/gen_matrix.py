"""Grid search of all possible team matchups."""

from datetime import datetime as dt
import os
import pandas as pd

from preprocess import create_sample
#from utils.brackets import brackets as br
#from predict import Models


#m = Models()

def gen_mat(m, bracket, year, save_fp):
    schools = [str(school[0]) for school in bracket]

    if not os.path.exists(save_fp):
        mat = []
        schools = []
        season = m.season_data

        for school1 in bracket:
            print(f"Matchups for {school1}")
            schools.append(str(school1[0]))
            row = []
            for school2 in bracket:
                if school1 == school2:
                    row.append(-1)
                else:
                    print(school1, school2)
                    pred = m.predict(create_sample(season,year,school1,school2))
                    row.append(pred[0])
            mat.append(row)  

        #fn = "outputs/matchup_mat.csv"
        #print(f"Outputting matrix to {fn}")
        df = pd.DataFrame(mat, columns=schools)#.to_csv(fn)
        df.to_csv(save_fp)
    else:
        # TODO: Saving the file seems to pre-pend a column. Probably just an index
        # that should not be saved in the first place
        df = pd.read_csv(save_fp, index_col=0)

    return df

    ### Check if both teams higher than .5 or both less than .5



