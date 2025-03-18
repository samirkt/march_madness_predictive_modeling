from helper import school_abbrevs
from datetime import datetime as dt
import os
import pandas as pd

from mm_modeling.params import defs
from mm_modeling.scrapers import SeasonScraper, AdvSeasonScraper, TourneyScraper

def abbrev_schools(table):
    # Load abbreviation map
    abbrevs = school_abbrevs.load()

    # Replace school names based on map
    for pair in abbrevs:
        table.replace(pair[0],pair[1],inplace=True)
    return table

def merge_adv_stats(season,season_adv):
    basic_stats=set(season.Year.astype(str)+season._School)
    advanced_stats=set(season_adv.Year.astype(str)+season_adv._School)

    diff = list(basic_stats-advanced_stats)

    print("Seasons/teams missing advanced stats:", end=" ")
    print(diff)
    _ = input("Hit enter to continue.")
    print()

    merged=season.merge(season_adv, on=['Year','_School'], suffixes=[None,'_adv'])

    return merged


def test_abbrev_mapping(season, tourney):
    # Group season and tourney data by year
    sTeams = season.groupby('Year')
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
    sfilename = os.path.join(defs.DATA_DIR, SeasonScraper.SeasonScraper().get_name())
    safilename = os.path.join(defs.DATA_DIR, AdvSeasonScraper.AdvSeasonScraper().get_name())
    tfilename = os.path.join(defs.DATA_DIR, TourneyScraper.TourneyScraper().get_name())

    check_adv_stats = 1
    try:
        season = pd.read_csv(sfilename)
    except:
        print("Searching for file %s. File does not exist." % sfilename)
        quit()
    try:
        season_adv = pd.read_csv(safilename)
    except:
        print("Searching for file %s. File does not exist." % safilename)
        _ = input("Ignoring advanced stats. Hit enter to continue.")
        print()
        check_adv_stats = 0

    # Merge advanced stats
    if check_adv_stats:
        season = merge_adv_stats(season,season_adv)

    # Data Preprocessing
    season = abbrev_schools(season)

    # Data Checks
    try:
        tourney = pd.read_csv(tfilename)
        tourney = abbrev_schools(tourney)
        test_abbrev_mapping(season,tourney)
        tourney.to_csv(tfilename[:-4]+"_clean.csv")
    except:
        print(f"Could not load or clean tourney data for {tfilename}")


    # Data Cleaning Output
    season.to_csv(sfilename[:-4]+"_clean.csv")
    print("Saved cleaned season and tourney data.")

