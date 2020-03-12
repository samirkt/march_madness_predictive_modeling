from school_abbrevs import load as abb_load
import pandas as pd

def abbrev_schools(table):
    abbrevs = abb_load()
    for pair in abbrevs:
        table.replace(pair[0],pair[1],inplace=True)
    return table

def test_abbrev_mapping(season, tourney):
    sTeams = season.groupby('year')
    tTeams = tourney.groupby('Year')

    for year,group in sTeams:
        matches = tTeams.get_group(year)
        matchSet = (set(matches.School) | set(matches.Opponent))
        seasSet = set(group._School)
        
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
    sfilename = 'data/season/1993_to_2019_season.csv'
    tfilename = 'data/tourney/1987_to_2019_tourney.csv'
    season = pd.read_csv(sfilename)
    tourney = pd.read_csv(tfilename)

    filename = sfilename[:-4]+'_clean.csv'
    season = abbrev_schools(season)
    season.to_csv(filename)
    print('\rData saved to file \'%s\'' % filename)

    test_abbrev_mapping(season,tourney)
