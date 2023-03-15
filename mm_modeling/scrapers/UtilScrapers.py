'''
Samir Townsley
March 3, 2020
NCAA Season Data Scraper

Description: 
    Get season stats for all NCAA tournament teams between specified year range (inclusive). Default year range is 1993 through 2021. Output is a .csv file where each row corresponds to the statistics for a team for a given season. File is saved in the 'data/season/' directory.
Usage: 
    Run with default parameters - python3 get_season_data.py
    Run with manual year entry - python3 get_season_data.py <first included year> <last included year>
Source:
    www.sports-reference.com
'''

from mm_modeling.scrapers.ScraperBase import ScraperBase


class PlayerScraper(ScraperBase):
    NAME = "player_stats"

    def __init__(self, url):
        # Since this is being used as a util in a broader
        # scraper, we don't need file saving attributes
        # so don't init parent class
        self.url = url
        self.row = {}
    
    def _get_name(self):
        return self.NAME
    
    def extract_columns(self, thead):
        # Get high-level columns
        cols = [col.text for col in thead.find_all('th')][1:]
        
        return cols
    
    def build_table(self, tbody, cols):
        # Make dictionary where each entry is a list of stats for every
        # player. As of python 3.6 dicts are ordered
        players = {col:[] for col in cols}
        for trow in tbody.find_all('tr'):
            for col, item in zip(players.keys(), trow.find_all('td')):
                players[col].append(item.text)
        
        return players

    def run(self):
        table = []
        ### Fetch web data from "sports-reference.com"
        page = self.get(self.url)

        ### Process content
        try:
            titles, theads, tbodies = self.get_tables(page)
        except Exception as exc:
            print(exc)

        for title, thead, tbody in zip(titles, theads, tbodies):
            ### Extract table column names
            cols = self.extract_columns(thead)
            ### Build out table
            entry = self.build_table(tbody, cols)
            self.row[title] = entry.copy()
    