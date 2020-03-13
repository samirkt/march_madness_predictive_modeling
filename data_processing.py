from school_abbrevs import load as abb_load
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd

def abbrev_schools(table):
    # Load abbreviation map
    abbrevs = abb_load()

    # Replace school names based on map
    for pair in abbrevs:
        table.replace(pair[0],pair[1],inplace=True)
    return table

def test_abbrev_mapping(season, tourney):
    # Group season and tourney data by year
    sTeams = season.groupby('year')
    tTeams = tourney.groupby('Year')

    # Check school name overlap between season and tourney data
    for year,group in sTeams:
        try:
            matches = tTeams.get_group(year)
        except:
            print("%d: " % year)
            print("No tournament data for this year.\n")
            continue

        # Get set of season and tourney team names
        matchSet = (set(matches.School) | set(matches.Opponent))
        seasSet = set(group._School)
        
        # Compute set differences and display results
        diff1 = list(matchSet - seasSet)
        diff2 = list(seasSet - matchSet)
        diff1.sort()
        diff2.sort()

        print("%d: " % year)
        print("Missing season stats:", end=" ")
        print(diff1)
        print("Missing tourney stats:", end=" ")
        print(diff2)
        print()

if __name__ == "__main__":
    # Pick season and tourney data files
    usr_in = (input('Processing and cleaning season data...\nEnter season filename or hit "enter" to use default: ') or '1993_to_2019_season.csv')
    usr_in = usr_in[12:] if usr_in[:12] == 'data/season/' else usr_in
    sfilename = 'data/season/' + usr_in
    tfilename = 'data/tourney/1987_to_2019_tourney.csv'
    print()

    try:
        season = pd.read_csv(sfilename)
    except:
        print("Searching for file %s. File does not exist." % sfilename)
        quit()
    tourney = pd.read_csv(tfilename)

    # Data Preprocessing
    season = abbrev_schools(season)

    # Data Checks
    test_abbrev_mapping(season,tourney)

    # Data Cleaning Output
    filename = sfilename[:-4]+'_clean.csv'
    season.to_csv(filename)
    print('\rData saved to file \'%s\'' % filename)

