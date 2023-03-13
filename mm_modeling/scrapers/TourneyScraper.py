'''
Samir Townsley
March 3, 2020
NCAA Tournament Data Scraper

Description: 
    Scrape March Madness tournament matchups between desired year range (inclusive). Default year range is 1993 through 2021. Output is a .csv file with each row representing one tournament matchup. File is saved in a directory titled 'data/tourney/'.
Usage: 
    Run with default parameters - python3 get_tourney_data.py
    Run with manual year entry - python3 get_tourney_data.py <first included year> <last included year>
Source:
    www.sports-reference.com
'''


from mm_modeling.scrapers.ScraperBase import ScraperBase


class TourneyScraper(ScraperBase):
    NAME = "tourney"

    def __init__(self):
        ScraperBase.__init__(self)
    
    def _get_name(self):
        return self.NAME
    
    def extract_columns(self, thead):
        cols = [col.text for col in thead.find_all('th')]
        cols = cols[1:]
        cols.insert(6,'opponent_seed')
        cols.insert(4,'school_seed')

        return cols
    
    def build_table(self, tbody, table, offset):
        for trow in tbody.find_all('tr'):
            # Check if row is invalid
            if trow.has_attr('class'):
                continue

            # Append each item in row
            row = []
            for col in trow.find_all('td'):
                # Split seed and school name
                item = col.text.split('\xa0')

                row.extend(item)

            if len(row) != 13:
                print('ERROR. Incorrect number of columns:')
                print(row)

            print('\tCurrent year: '+str(row[0]), end="\r", flush=True)
            table.append(row)

        # Increase offset to retrieve next page
        offset += 100

        return table, offset

    def run(self):
        
        offset = 0
        table = []
        while 1:
            ### Fetch web data from "sports-reference.com"
            url = f"https://www.sports-reference.com/cbb/play-index/tourney.cgi?request=1&match=single&year_min={self.START}&year_max={self.END}&seed_cmp=eq&opp_seed_cmp=eq&game_result=W&pts_diff_cmp=eq&order_by_single=date_game&order_by_combined=g&offset={offset}"
            page = self.get(url)

            ### Process content, get data table header and body
            try:
                th_soup, tb_soup = self.get_head_and_body(page)
            except Exception as e:
                raise Exception(e)

            if len(tb_soup) == 0:   # No more data to process
                break
            else:
                thead = th_soup[0]
                tbody = tb_soup[0]

            ### Extract table column names
            if len(table) == 0:
                cols = self.extract_columns(thead)
                table = [cols]
                

            ### Build out table
            table, offset = self.build_table(tbody, table, offset)

        self.save(table)

if __name__ == "__main__":
    s = TourneyScraper()
    s.run()
