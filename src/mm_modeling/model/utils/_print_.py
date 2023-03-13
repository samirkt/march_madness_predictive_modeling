import pandas as pd
from globs import *

# Print 
def print_tourney_teams():
    year = input("Enter a year:\n")
    if not year:
        return

    season = pd.read_csv("../../data/season/1993_to_{0}_season_clean.csv".format(current))
    season = season[season['Year']==int(year)]

    print(list(season['_School'].unique()))

def main():
    print_tourney_teams()

if __name__ == "__main__":
    main()
