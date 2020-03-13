# March Madness Predictive Modeling 2020

## Description
This repo contains code to develop a predictive model for the 2020 NCAA March Madness tournament. Included in the repo are scripts to extract tournament and season statistics for NCAA teams from "www.sports-reference.com".

## Repo Contents
1. Scripts
	* *get_season_data.py* - Gets season statistics for teams that appear in NCAA tournament (i.e. Wins, Losses, etc.)
	* *get_tourney_data.py* - Gets data from NCAA tournament games (i.e. Seed, Round, Score, etc.)
	* *data_processor.py* - Processes and cleans up season data. Outputs file to season folder with suffix "\_clean.csv". More details in Data Processing section
2. Data Directories (created during script execution)
	* *data/season/* - directory where all season data is stored
	* *data/tourney/* - directory where all tournament data is stored

## Data Processing
#### Data Checks
1. Print out teams with no associated tournament data or no associated season statistics
	* Performed separately on each year of data
	* Some teams have season stats but are missing tournament matchup data
	* There shouldn't be any teams with matchup data but no season statistics

#### Data Cleaning
1. Map team names in season data to abbreviated versions used in tourney data
	* Abbreviation mappings stored and editable in "school\_abbrevs.py"

---

## Usage
Pipeline to use this repo. All data scraped from 1993 through 2019 by default.

1. Scrape season stats

	`python3 get_season_data.py`

2. Scrape tournament data

	`python3 get_tourney_data.py`

3. Preprocess season data

	`python3 data_processor.py`

	`When prompted: enter season data file name stored in data/season/ (i.e. 1993_to_2019_season.csv)`

## Other examples
Replace \<script\> with either `get_season_data.py` or `get_tourney_data.py`.
1. Get data in year range (2000 thru 2019 inclusive)

	`python3 <script> 2000 2019`

2. Get data in single year (2019)

	`python3 <script> 2019`
