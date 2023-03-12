"""Grid search of all possible team matchups."""

from datetime import datetime as dt
import pandas as pd

from preprocess import create_sample
from utils.brackets import brackets as br
from predict import Models


m = Models()
mat = []
schools = []
year = dt.now().year
season = m.season_data

for school1 in br[year]:
    schools.append(str(school1[0]))
    row = []
    for school2 in br[year]:
        if school1 == school2:
            row.append(-1)
        else:
            pred = m.predict(create_sample(season,year,school1,school2))
            row.append(pred[0])
    mat.append(row)  

pd.DataFrame(mat,columns = schools).to_csv("matchup_mat.csv")


### Check if both teams higher than .5 or both less than .5



