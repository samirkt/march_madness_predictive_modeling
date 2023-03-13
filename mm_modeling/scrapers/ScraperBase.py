'''
Samir Townsley
March 3, 2020
NCAA Season Data Scraper Base

Description: 
    Base functionality for data scraping classes.
Source:
    www.sports-reference.com
'''



from abc import abstractmethod
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
import pandas as pd
import random
import requests
import sys, os
import time

import mm_modeling as mm
from mm_modeling.params import defs


class ScraperBase:
    START = defs.FIRST_YEAR
    END = dt.now().year
    DATA_DIR = defs.DATA_DIR

    RPM = 15 # requests per minute

    def __init__(self):
        ### Create data directory and file name
        sub_dir = f"{self.DATA_DIR}/{self._get_name()}"
        if not os.path.exists(self.DATA_DIR):
            os.mkdir(self.DATA_DIR)
        if not os.path.exists(sub_dir):
            os.mkdir(sub_dir)
        f = f"{self.START}_to_{self.END}_{self._get_name()}.csv"
        self.filename = os.path.join(sub_dir, f)
    
    def get_head_and_body(self, page):
        # Get data table headers and body
        soup = bs(page.content,'html.parser')
        thead = soup.find_all('thead')[0]
        tbody = soup.find_all('tbody')[0]
        return thead, tbody
    
    def get(self, url):
        page = requests.get(url)
        if page.status_code != 200:
            print(f"Warning: status code {page.status_code}")
        self._rate_limit()

        return page
    
    def save(self, table):
        pd.DataFrame(columns=table[0],data=table[1:]).to_csv(self.filename)
        print(f"\rData saved to file \'{self.filename}\'")

    def _rate_limit(self):
        rand_wait = random.random() * 3
        time.sleep((60/self.RPM)+rand_wait)

    @abstractmethod
    def _get_name(self):
        pass

    @abstractmethod
    def extract_columns(self, thead):
        pass

    @abstractmethod
    def build_table(self, tbody):
        pass

    @abstractmethod
    def run(self):
        pass
