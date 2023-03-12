# March Madness Predictive Modeling 2021

## Description
This repo contains code to build, train, and test an ensemble classifier for the 2021 NCAA March Madness tournament. The default ensemble method trains a basic neural network, a random forest classifier, and a logistic regression model and makes predictions based on an average of the resulting prediction probabilities. Included in the repo are scripts to extract tournament and season statistics for NCAA teams from "www.sports-reference.com".

## Model Training and Predicting
The model training and predicting code is set up to automatically format scraped data for model training. The model code builds three different machine learning models (fully connected neural net, random forest, logistic regression) with access to several tunable parameters. Model performances are written to an output file and models are saved and usable for performing predictions on unseen tournament data.

### Contents
1. Scripts
	* *preprocess.py* - Formats season and tournament data into feature and target columns that can be fed into a classifier
	* *models.py* - ML operationalization for 3 different models: a basic fully-connected NN, a random forest classifier, and a logistic regression. Model parameter settings and model performance are appended to outputs.txt for each trained model. Uses 25% of the data as a validation set.
	* *train.py* - Uses the *models.py* library to train and save 3 different models
	* *predict.py* - Uses a voting process between 3 trained and saved models to pick winners in a bracket of teams (bracket stored in utils/brackets.py)

### Usage
1. Scrape data up until current year (Refer to "Data Scraping" section below)
2. Set current year, start and end years (for training), and prediction year in *utils/globs.py*. 
	* NOTE: Current year should match the final year of scraped data. Training and predicting may not actually use this year (or all years prior) but it is assumed to be present and is used to identify which scraped data file to use.
3. Format data: `python preprocess.py`
4. Specify model training parameters by setting the parameters for each model-specific method in *models.py*
5. Train up to 3 models: `python train.py`
	* Comment out any models in *train.py* that do not need to be trained (i.e. when retraining a single model with new parameters)
6. If predicting for tournaments after 2021... Add an entry in the brackets dictionary in *utils/brackets.py* containing matchups and seeds. See existing entries for an example.
7. Run model predictions: `python predict.py`
	* Current behavior: predictions are output one matchup at a time with probabilities for each of the three models as well as the average probability across models. Default predictions are made based on this average probability.

---

## Data Scraping
### Contents
1. Scripts
	* *get_season_data.py* - Gets season statistics for teams that appear in NCAA tournament (i.e. Wins, Losses, etc.)
	* *get_season_adv_data.py* - Gets advanced season statistics for teams that appear in NCAA tournament
	* *get_tourney_data.py* - Gets data from NCAA tournament games (i.e. Seed, Round, Score, etc.)
	* *data_processor.py* - Processes and cleans up season data. Combines season data with advanced season statistics if available. Outputs file to season folder with suffix "\_clean.csv". More details in Data Processing section
2. Data Directories (created during script executions)
	* *data/season/* - directory where all basic and cleaned season data is stored
	* *data/season_adv/* - directory where extra advanced season data is stored
	* *data/tourney/* - directory where all tournament data is stored

### Data Processing
##### Data Checks
1. Print out teams with no associated tournament data or no associated season statistics
	* *Performed separately on each year of data*
	* *Some teams have season stats but are missing tournament matchup data*
	* *There should not be any teams with tourney matchup data but no season statistics*

##### Data Cleaning
1. Map team names in season data to the abbreviated versions used in tourney data
	* *Abbreviation mappings stored and editable in "helper/school\_abbrevs.py"*


### Data Scraping Usage
Pipeline to use this repo. All data scraped from 1993 through current year (inclusive) by default.

1. Scrape season stats

	`python get_season_data.py`

2. Scrape advanced season stats

	`python get_season_adv_data.py`

3. Scrape tournament data

	`python get_tourney_data.py`

4. Clean season data

	`python data_processor.py`

	When prompted, enter season data file name or hit "enter" for default.

	Example: `2000_to_2021_season.csv`

### Other examples
#### (Deprecated - if using model training code, pull all data up until current year even if it won't be used for training/predicting)
Replace \<script\> with either `get_season_data.py` or `get_tourney_data.py`.
1. Get data in year range (2000 thru 2019 inclusive)

	`python <script> 2000 2019`

2. Get data in single year (2019)

	`python <script> 2019`
