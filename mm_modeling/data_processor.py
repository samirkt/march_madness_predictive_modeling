from helper.school_abbrevs import load as abb_load
from datetime import datetime as dt
import pandas as pd

def abbrev_schools(table):
    # Load abbreviation map
    abbrevs = abb_load()

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
    # Pick season and tourney data files (tourney file is fixed)
    yr = dt.now().year
    usr_in = (input("Processing and cleaning season data...\nEnter season filename or hit 'enter' to use default: ") or "1993_to_{0}_season.csv".format(yr))
    print("Using file {0}".format(usr_in))
    usr_in = usr_in[12:] if usr_in[:12] == 'data/season/' else usr_in
    sfilename = 'data/season/' + usr_in
    safilename = 'data/season_adv/'+usr_in[:-4]+'_adv'+usr_in[-4:]
    tfilename = 'data/tourney/1993_to_{0}_tourney.csv'.format(yr)
    print()

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
    tourney = pd.read_csv(tfilename)

    # Merge advanced stats
    if check_adv_stats:
        season = merge_adv_stats(season,season_adv)

    # Data Preprocessing
    season = abbrev_schools(season)

    # Data Checks
    test_abbrev_mapping(season,tourney)

    # Data Cleaning Output
    filename = sfilename[:-4]+'_clean.csv'
    season.to_csv(filename)
    print('\rData saved to file \'%s\'' % filename)

