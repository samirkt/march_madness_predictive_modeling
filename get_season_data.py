'''
Samir Townsley
March 3, 2020
NCAA Season Data Scraper

Description: 
    Get season stats for all NCAA tournament teams between specified year range (inclusive). Default year range is 1993 through 2019. Output is a .csv file where each row corresponds to the statistics for a team for a given season. File is saved in the 'data/season/' directory.
Usage: 
    Run with default parameters - python3 get_season_data.py
    Run with manual year entry - python3 get_season_data.py <first included year> <last included year>
Source:
    www.sports-reference.com
'''



from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import sys, os

### Set year parameters
if len(sys.argv) == 1:  # Default year range
    start = 1993    # First season with data available
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
sub_dir = data_dir+'/season'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
if not os.path.exists(sub_dir):
    os.mkdir(sub_dir)
filename = sub_dir+'/'+str(start)+'_to_'+str(end)+'_season.csv'


table = []
for year in range(int(start),int(end)+1):
    ### Status report
    print('\tCurrent year: '+str(year), end="\r", flush=True)

    ### Fetch web data from "sports-reference.com"
    page = requests.get('https://www.sports-reference.com/cbb/seasons/'+str(year)+'-school-stats.html')

    ### Process content
    try:
        # Get data table headers and body
        soup = bs(page.content,'html.parser')
        thead = soup.find_all('thead')[0]
        tbody = soup.find_all('tbody')[0]
    except:
        # No season data available for this year
        print('\tNo data found: %s%s' % (str(year)," "*10))
        continue

    ### Extract table column names
    if len(table) == 0:
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
        table = [['Year']+cols[1:]]

    ### Build out table
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


### Save data to .csv file
pd.DataFrame(columns=table[0],data=table[1:]).to_csv(filename)
print('\rData saved to file \'%s\'' % filename)

