import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import pandas as pd

import time
import urllib.parse
import re
import random

from mm_modeling.params import defs
from mm_modeling.model.utils.brackets import brackets

# Team map
team_map = {
    "BYU": "Brigham Young",
    "Ole Miss": "Mississippi",
    "Saint Mary's": "Saint Mary's (CA)",
    "UConn": "Connecticut",
    "UNC": "North Carolina",
    "VCU": "Virginia Commonwealth",
}

# Columns for team stats
stat_cols = [
    "Overall_W",
    "Overall_L",
    "Overall_SRS",
    "Overall_SOS",
    "Conf._W",
    "Conf._L",
    "Home_W",
    "Home_L",
    "Away_W",
    "Away_L",
    "Points_Tm.",
    "Points_Opp.",
    "Totals_FG",
    "Totals_FGA",
    "Totals_FG%",
    "Totals_3P",
    "Totals_3PA",
    "Totals_3P%",
    "Totals_FT",
    "Totals_FTA",
    "Totals_FT%",
    "Totals_ORB",
    "Totals_TRB",
    "Totals_AST",
    "Totals_STL",
    "Totals_BLK",
    "Totals_TOV",
    "Totals_PF",
]

# TODO: Get openAI key
# Initialize open AI connection
client = OpenAI(
    api_key=...
)

# Define the directory to store cached content
CACHE_DIR = "scraped_data"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def sanitize_filename(name):
    """Simple function to sanitize team names for filenames."""
    return "".join(c if c.isalnum() else "_" for c in name)

# --- Step 1: Scrape Relevant Team Content with Caching ---
def get_query_content(query, limit=5):
    """
    Helper function that executes a Google News search for the given query and returns
    a list of detailed snippets including headlines, publication dates, and article text.
    """
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://news.google.com/search?q={encoded_query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    print(search_url)
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error retrieving content for query '{query}': {e}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article")
    snippets = []
    for article in articles:
        headline_tag = article.find(['h3', 'h4'])
        headline = headline_tag.get_text(strip=True) if headline_tag else ""
        time_tag = article.find("time")
        pub_date = time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else (time_tag.get_text(strip=True) if time_tag else "")
        snippet = article.get_text(separator=" ", strip=True)
        detailed_snippet = f"Headline: {headline}. Date: {pub_date}. Snippet: {snippet}"
        snippets.append(detailed_snippet)
        if len(snippets) >= limit:
            break
    return snippets

def scrape_team_content(team_name, tournament_year):
    """
    Given a team name and tournament year, this function returns cached content if available.
    Otherwise, it scrapes multiple sources to gather relevant, matchup-agnostic information,
    including general season reviews and team overviews, as well as basic team stats.
    It uses separate queries to capture overall team performance sentiment and caches
    and returns a combined string of high-value content.
    """
    safe_team_name = sanitize_filename(team_name)
    cache_filename = os.path.join(CACHE_DIR, f"{safe_team_name}_{tournament_year}.txt")

    if os.path.exists(cache_filename):
        with open(cache_filename, "r", encoding="utf-8") as f:
            cached_content = f.read()
        print(f"Loaded cached content for {team_name} ({tournament_year}).")
        return cached_content

    # Updated queries to capture matchup-agnostic sentiment.
    review_query = f"{team_name} men's basketball {tournament_year}"
    overview_query = f"{team_name} men's basketball season stats {tournament_year}"
    
    review_snippets = get_query_content(review_query, limit=6)
    overview_snippets = get_query_content(overview_query, limit=6)
    
    combined_snippets = review_snippets + overview_snippets
    combined_content = " ".join(combined_snippets) if combined_snippets else ""
    
    with open(cache_filename, "w", encoding="utf-8") as f:
        f.write(combined_content)
    print(f"Scraped and cached enhanced matchup-agnostic content for {team_name} ({tournament_year}).")

    return combined_content


# --- Step 2: Evaluate the Matchup Using an LLM ---
def evaluate_matchup(team1, team2, content_team1, content_team2, tournament_year):
    """
    Given two team names, their season statistics, and their corresponding unstructured content (from news, social media, etc.),
    use an LLM (via the OpenAI API) to evaluate which team is most likely to win the matchup.
    """
    prompt = f"""
            You are a sports analytics expert evaluating college basketball teams for the March Madness {tournament_year} tournament.
            Based solely on the following structured statistics and unstructured content scraped from news and social media, please evaluate which team is most likely to win their matchup. Provide your answer using the format below:

            Predicted Winner: <Team Name>
            Explanation: <Detailed reasoning based on the provided information>

            Team 1: {team1[0]}
            Stats: {{{team1[2]}}}
            Information: {content_team1}

            Team 2: {team2[0]}
            Stats: {{{team2[2]}}}
            Information: {content_team2}

            Please base your analysis only on the provided content and your domain expertise about college basketball. Ignore any news or media that are not directly applicable to the quality or sentiment around the team in question. Ignore headlines that are about a matchup other than the one in question.
            """
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",  # or another model as needed
        messages=[
            {"role": "system", "content": "You are a sports analytics expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7)
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error during evaluation: {e}"
    return answer

def extract_winner(prediction):
    """
    Extracts the predicted winner's team name from the LLM's output.
    Expects a line in the format: "Predicted Winner: <Team Name>"
    """
    match = re.search(r"Predicted Winner:\s*(.+)", prediction)
    if match:
        # Return the full team name as predicted (may be multiple words)
        return match.group(1).strip()
    return None

# --- Step 3: Grab relevant team season stats ---
def get_team_stats(team, df):
    if team in team_map:
        team = team_map[team]
    row = df[df._School == team][stat_cols].iloc[0]
    stats = ", ".join(f"{col}: {val}" for col, val in row.items())
    return stats

# --- Helper Function: Process the Full Tournament List ---
def process_tournament(bracket, tournament_year, stats_df):
    """
    Processes a tournament bracket provided as a list of tuples (team_name, seed). Every two consecutive
    entries are treated as a matchup. For each matchup, the function scrapes content for both teams (with caching) and
    then evaluates the predicted outcome using the LLM.
    
    Returns a list of dictionaries with matchup details and predictions.
    """
    predictions = []
    i = 0
    while len(bracket) > 1:
        _team1 = bracket[i]
        _team2 = bracket[i+1]
        print(f"Processing matchup: {_team1[0]} (Seed {_team1[1]}) vs {_team2[0]} (Seed {_team2[1]})")

        # Scrape or load cached content for each team.
        content_team1 = scrape_team_content(_team1[0], tournament_year)
        content_team2 = scrape_team_content(_team2[0], tournament_year)

        # Grab team stats
        team1 = (*_team1, get_team_stats(_team1[0], stats_df))
        team2 = (*_team2, get_team_stats(_team2[0], stats_df))

        # Evaluate the matchup using the LLM.
        prediction = evaluate_matchup(team1, team2, content_team1, content_team2, tournament_year)
        winner = extract_winner(prediction)
        #prediction = random.choice([team1[0], team2[0]])
        #winner = prediction
        predictions.append({
            "matchup": f"{team1} vs {team2}",
            "prediction": prediction,
        })

        # Sleep briefly to mitigate rate limits.
        #time.sleep(2)
        print("=" * 50)
        print("\n" * 2)
        print(f"{team1}:\n\n{content_team1}")
        print("\n" * 2)
        print("=" * 50)
        print("\n" * 2)
        print(f"{team2}:\n\n{content_team2}")
        print("\n" * 2)
        print("=" * 50)
        print("\n" * 2)
        print(predictions[-1]["prediction"])
        print("\n" * 2)
        print(winner)
        print("\n" * 2)

        if winner == team1[0]:
            loser = 1
        elif winner == team2[0]:
            loser = 0
        else:
            raise ValueError(f"Prediction {winner} does not match a team {team1[0]}, {team2[0]}")

        # Mark loser for removal
        bracket[i + loser] = None

        # Next matchup
        i += 2

        # Reset for next round
        if i >= len(bracket):
            i = 0
            bracket = [_i for _i in bracket if _i]
        ex = input()
        if ex: quit(0)


    return predictions

# --- Main Execution Example ---
if __name__ == "__main__":
    tournament_year = 2025
    tournament_list = brackets[tournament_year]

    stats_fp = os.path.join(defs.DATA_DIR, str(tournament_year), "season.csv")
    stats_df = pd.read_csv(stats_fp)

    # Process the tournament bracket and print predictions.
    predictions = process_tournament(tournament_list, tournament_year, stats_df)
    for match in predictions:
        print(match["matchup"])
        print(match["prediction"])
        print("=" * 50)

