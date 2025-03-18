"""Combine all years in range into single dataframe."""

import glob
import os
import pandas as pd
import sys

from mm_modeling.params import defs
from mm_modeling.scrapers.SeasonScraper import SeasonScraper
from mm_modeling.scrapers.AdvSeasonScraper import AdvSeasonScraper
from mm_modeling.scrapers.TourneyScraper import TourneyScraper

def safe_read_csv(fp):
    try:
        _df = pd.read_csv(fp)
    except:
        print(f"Could not read {fp}")
        _df = pd.DataFrame()
    
    return _df

def safe_write_csv(table, fp):
    if len(table) > 0:
        table.to_csv(fp)

def main():
    start = sys.argv[1]
    end = sys.argv[2]
    data_dir = defs.DATA_DIR

    s_scraper = SeasonScraper()
    as_scraper = AdvSeasonScraper()
    t_scraper = TourneyScraper()

    season = pd.DataFrame()
    adv_season = pd.DataFrame()
    tourney = pd.DataFrame()

    for year in range(int(start), int(end)+1):
        _season = safe_read_csv(s_scraper.get_fp(year))
        _adv_season = safe_read_csv(as_scraper.get_fp(year))
        _tourney = safe_read_csv(t_scraper.get_fp(year))


        season = pd.concat([season, _season], axis=0).reset_index(drop=True)
        adv_season = pd.concat([adv_season, _adv_season], axis=0).reset_index(drop=True)
        tourney = pd.concat([tourney, _tourney], axis=0).reset_index(drop=True)

    safe_write_csv(season, os.path.join(data_dir, s_scraper.get_name()))
    safe_write_csv(adv_season, os.path.join(data_dir, as_scraper.get_name()))
    safe_write_csv(tourney, os.path.join(data_dir, t_scraper.get_name()))


if __name__ == "__main__":
    main()
