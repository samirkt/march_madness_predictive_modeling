'''
Samir Townsley
March 3, 2020
NCAA Tournament Data Scraper

Description: 
    Scrape March Madness tournament matchups between desired year range (inclusive). Default year range is 1993 through 2019. Output is a .csv file with each row representing one tournament matchup. File is saved in a directory titled 'data/tourney/'.
Usage: 
    Run with default parameters - python3 get_tourney_data.py
    Run with manual year entry - python3 get_tourney_data.py <first included year> <last included year>
Source:
    www.sports-reference.com
'''



from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import sys, os

### Set year parameters
if len(sys.argv) == 1:  # Default year range
    start = 1993    # 1993: Earliest available season data
                    # 1987: Introduction of 3-pt line and shot clock
    end = 2019
elif len(sys.argv) == 2:    # Manual year entry (single year)
    start = sys.argv[1]
    end = sys.argv[1]
elif len(sys.argv) == 3: # Manual year entry
    start = sys.argv[1]
    end = sys.argv[2]
else:   
    print('Error: Invalid number of arguments (%s)' % len(sys.argv))
    quit()
print('Getting data from year %s through %s' % (start,end))


### Create data directory and file name
data_dir = 'data'
sub_dir = data_dir+'/tourney'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
if not os.path.exists(sub_dir):
    os.mkdir(sub_dir)

filename = sub_dir+'/'+str(start)+'_to_'+str(end)+'_tourney.csv'


offset = 0
table = []
while 1:
    ### Fetch web data from "sports-reference.com"
    page = requests.get('https://www.sports-reference.com/cbb/play-index/tourney.cgi?request=1&match=single&year_min='+str(start)+'&year_max='+str(end)+'&seed_cmp=eq&opp_seed_cmp=eq&game_result=W&pts_diff_cmp=eq&order_by_single=date_game&order_by_combined=g&offset='+str(offset))

    ### Process content, get data table header and body
    soup = bs(page.content,'html.parser')
    th_soup = soup.find_all('thead')
    tb_soup = soup.find_all('tbody')
    if len(tb_soup) == 0:   # No more data to process
        break
    else:
        thead = th_soup[0]
        tbody = tb_soup[0]

    ### Extract table column names
    if len(table) == 0:
        cols = [col.text for col in thead.find_all('th')]
        cols = cols[1:]
        cols.insert(6,'opponent_seed')
        cols.insert(4,'school_seed')
        table = [cols]

    ### Build out table
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

# Save data to .csv file
pd.DataFrame(columns=table[0],data=table[1:]).to_csv(filename)
print('\rData saved to file \'%s\'' % filename)

