'''
Samir Townsley
March 13, 2021
NCAA Season Data Scraper

Description: 
    Get advanced season stats for all NCAA tournament teams between specified year range (inclusive). Default year range is 1993 through 2021. Output is a .csv file where each row corresponds to the statistics for a team for a given season. File is saved in the 'data/season_adv/' directory.
Usage: 
    Run with default parameters - python3 get_season_adv_data.py
    Run with manual year entry - python3 get_season_adv_data.py <first included year> <last included year>
Source:
    www.sports-reference.com
'''

from mm_modeling.scrapers.ScraperBase import ScraperBase


class AdvSeasonScraper(ScraperBase):
    NAME = "season_adv"

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

        return cols
    
    def build_table(self, tbody, table, year):
        for trow in tbody.find_all('tr'):
            # Check if row is not relevant
            if trow.has_attr('data-row'):
                continue

            # Append each item in row
            row = []
            for col in trow.find_all('td'):
                # Split school name and NCAA appearance
                item = col.text.split('\xa0')
                row.extend(item)

            # Check if team was in NCAA tourney
            if len(row) > 0 and row[1] == 'NCAA':
                table.append([year]+row[:1]+row[2:])

        return table

    def run(self):
        table = []
        for year in range(int(self.START),int(self.END)+1):
            ### Status report
            print('\tCurrent year: '+str(year), end="\r", flush=True)

            ### Fetch web data from "sports-reference.com"
            url = f"https://www.sports-reference.com/cbb/seasons/{year}-advanced-school-stats.html"
            page = self.get(url)

            ### Process content
            try:
                thead, tbody = self.get_head_and_body(page)
            except:
                # No season data available for this year
                print('\tNo data found: %s%s' % (str(year)," "*10))
                continue

            ### Extract table column names
            if len(table) == 0:
                cols = self.extract_columns(thead)
                table = [['Year']+cols[1:]]

            ### Build out table
            self.build_table(tbody, table, year)

            self.save(table)

if __name__ == "__main__":
    s = AdvSeasonScraper()
    s.run()