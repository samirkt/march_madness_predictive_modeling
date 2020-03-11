# March Madness Predictive Modeling 2020

## Description
This repo contains code to develop a predictive model for the 2020 NCAA March Madness tournament. Included in the repo are scripts to extract tournament and season statistics for NCAA teams from "www.sports-reference.com".

## Repo Contents
1. Scripts
	* *get_season_data.py* - Gets season statistics for NCAA teams that appear in NCAA tournament (i.e. Wins, Losses, etc.)
	* *get_tourney_data.py* - Gets data from NCAA tournament games (i.e. Seed, Round, Score, etc.)
2. Data Directories (created during script execution)
	* *data/season/* - directory where all season data is stored
	* *data/tourney/* - directory where all tournament data is stored

## Examples
1. Get default season data (1993 thru 2019)
	* **python3 get_season_data.py**
2. Get default tourney data (1987 thru 2019)
	* **python3 get_tourney_data.py**
3. Get season data from (2000 thru 2019)
	* **python3 get_season_data.py 2000 2019**
4. Get default tourney data (2019 only)
	* **python3 get_tourney_data.py 2019 2019**
