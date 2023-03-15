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
from mm_modeling.scrapers.UtilScrapers import PlayerScraper


class SeasonScraper(ScraperBase):
    NAME = "season"

    def __init__(self):
        ScraperBase.__init__(self)
    
    def _get_name(self):
        return self.NAME
    
    def extract_columns(self, thead):
        cols = []
        headers = thead.find_all('tr')

        # Get high-level columns
        for over in headers[0].find_all('th'): 
            val = over.get('colspan')
            cnt = 1 if val is None else int(val)
            cols.extend([over.text]*cnt)

        # Combine with sub-columns
        for i,under in enumerate(headers[1].find_all('th')): 
            cols[i] = cols[i]+'_'+under.text
        
        # Add util scraper cols
        cols.append(PlayerScraper.NAME)
        
        return cols
    
    def build_table(self, tbody, table, players, games, year):
        count = 0
        for trow in tbody.find_all('tr'):
            # Check if row is not relevant
            if trow.has_attr('data-row'):
                continue

            # Append each item in row
            row = []
            for i, col in enumerate(trow.find_all('td')):
                # Get school link
                if i == 0:
                    school_stats = self.BASE_URL + col.find("a")["href"] 

                # Split school name and NCAA appearance
                item = col.text.split('\xa0')
                row.extend(item)

            # Check if team was in NCAA tourney
            if len(row) > 0 and row[1] == 'NCAA':
                count += 1
                players = self.util_scrapes(school_stats)
                print(f"\t\tSchools added: {count}", end="\r", flush=True)
                table.append([year]+row[:1]+row[2:]+[players])
        
        return table
    
    def util_scrapes(self, url):
        util_scrapers = [
            (url, PlayerScraper),
        ]

        # lists should be getting passed by reference
        ret = []
        for link, scrape_cls in util_scrapers:
            scraper = scrape_cls(link)
            scraper.run()
            ret.append(scraper.row)

        return ret

    def run(self):
        table, players, games = [], [], []
        for year in range(int(self.START),int(self.END)+1):
            ### Status report
            print('\tCurrent year: '+str(year))

            ### Fetch web data from "sports-reference.com"
            url = f"{self.BASE_URL}/cbb/seasons/{year}-school-stats.html"
            page = self.get(url)

            ### Process content
            try:
                thead, tbody = self.get_head_and_body(page)
            except Exception as exc:
                print(exc)
                # No season data available for this year
                print('\tNo data found: %s%s' % (str(year)," "*10))
                continue

            ### Extract table column names
            if len(table) == 0:
                cols = self.extract_columns(thead)
                table = [['Year']+cols[1:]]

            ### Build out table
            table = self.build_table(tbody, table, players, games, year)

            self.save(table)

if __name__ == "__main__":
    s = SeasonScraper()
    s.run()
