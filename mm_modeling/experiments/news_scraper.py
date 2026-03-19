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
    "TCU": "Texas Christian",
    "Cal Baptist": "California Baptist",
    "Long Island": "Long Island University",
    "Queens (N.C.)": "Queens (NC)",
    "Penn": "Pennsylvania",
    "Miami (Ohio)": "Miami (OH)",
    "St. John's": "St. John's (NY)",
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

# Initialize open AI connection
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

# Define the directory to store cached content
CACHE_DIR = "scraped_data"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def sanitize_filename(name):
    """Simple function to sanitize team names for filenames."""
    return "".join(c if c.isalnum() else "_" for c in name)

def normalize_team_name(name):
    """Normalize school names for tolerant matching."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())

# --- Step 1: Scrape Relevant Team Content with Caching ---
def get_query_content(query, limit=5):
    """
    Helper function that executes a Google News search for the given query and returns
    a list of detailed snippets including headlines, publication dates, and article text.
    """
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://news.google.com/search?q={encoded_query}"
    headers = {"User-Agent": "Mozilla/5.0"}
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


def scrape_matchup_content(team1_name, team2_name, tournament_year):
    """
    Scrapes matchup-specific content (expert previews, head-to-head analysis) for a given pair of teams.
    Caches result to avoid redundant requests.
    """
    safe_t1 = sanitize_filename(team1_name)
    safe_t2 = sanitize_filename(team2_name)
    cache_filename = os.path.join(CACHE_DIR, f"{safe_t1}_{safe_t2}_{tournament_year}.txt")

    if os.path.exists(cache_filename):
        with open(cache_filename, "r", encoding="utf-8") as f:
            cached_content = f.read()
        print(f"Loaded cached matchup content for {team1_name} vs {team2_name} ({tournament_year}).")
        return cached_content

    preview_query = f"{team1_name} vs {team2_name} NCAA tournament {tournament_year} preview"
    matchup_query = f"{team1_name} {team2_name} March Madness {tournament_year}"

    preview_snippets = get_query_content(preview_query, limit=5)
    matchup_snippets = get_query_content(matchup_query, limit=5)

    combined_snippets = preview_snippets + matchup_snippets
    combined_content = " ".join(combined_snippets) if combined_snippets else ""

    with open(cache_filename, "w", encoding="utf-8") as f:
        f.write(combined_content)
    print(f"Scraped and cached matchup content for {team1_name} vs {team2_name} ({tournament_year}).")

    return combined_content


# --- Step 2: Evaluate the Matchup Using an LLM ---
def evaluate_matchup(team1, team2, content_team1, content_team2, matchup_content, tournament_year):
    """
    Given two team names, their season statistics, and their corresponding unstructured content (from news, social media, etc.),
    use an LLM (via the OpenAI API) to evaluate which team is most likely to win the matchup.
    """
    prompt = f"""
            You are a sports analytics expert evaluating college basketball teams for the March Madness {tournament_year} tournament.
            Based solely on the following structured statistics and unstructured content scraped from news and social media, please evaluate which team is most likely to win their matchup. Provide your answer using the format below:

            Predicted Winner: <Team Name>
            Key Factors:
            - Offensive edge: <which team and why>
            - Defensive matchup: <which team and why>
            - Recent form & momentum: <which team and why>
            - Tournament experience & coaching: <which team and why>
            Confidence: <High / Medium / Low>
            Summary: <1-2 sentence overall reasoning>

            Team 1: {team1[0]}
            Stats: {{{team1[2]}}}
            Information: {content_team1}

            Team 2: {team2[0]}
            Stats: {{{team2[2]}}}
            Information: {content_team2}

            Matchup-Specific Analysis (previews, expert picks, head-to-head context):
            {matchup_content}

            Please base your analysis only on the provided content and your domain expertise about college basketball. Ignore any news or media that are not directly applicable to the quality or sentiment around the team in question. Ignore headlines that are about a matchup other than the one in question.
            """
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",  # or another model as needed
        messages=[
            {"role": "system", "content": "You are a sports analytics expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
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
    mapped_team = team_map.get(team, team)

    # 1) Direct exact match.
    exact = df[df._School == mapped_team]
    if not exact.empty:
        row = exact[stat_cols].iloc[0]
        return ", ".join(f"{col}: {val}" for col, val in row.items())

    # 2) Normalized exact match (handles punctuation / spacing differences).
    normalized_target = normalize_team_name(mapped_team)
    normalized_school = df["_School"].astype(str).apply(normalize_team_name)
    norm_matches = df[normalized_school == normalized_target]
    if not norm_matches.empty:
        row = norm_matches[stat_cols].iloc[0]
        return ", ".join(f"{col}: {val}" for col, val in row.items())

    # 3) Unique partial normalized match as a final fallback.
    partial_mask = normalized_school.apply(
        lambda s: normalized_target in s or s in normalized_target
    )
    partial_matches = df[partial_mask]
    if len(partial_matches) == 1:
        row = partial_matches[stat_cols].iloc[0]
        return ", ".join(f"{col}: {val}" for col, val in row.items())

    raise ValueError(
        f"Unable to locate stats row for team '{team}' (mapped as '{mapped_team}')."
    )

def get_round_name(teams_remaining):
    """Return human-readable round names based on teams remaining."""
    round_names = {
        64: "Round of 64",
        32: "Round of 32",
        16: "Sweet 16",
        8: "Elite 8",
        4: "Final Four",
        2: "Championship",
    }
    return round_names.get(teams_remaining, f"Round with {teams_remaining} teams")

def print_bracket_summary(rounds, champion):
    """Print bracket outcomes in an easy-to-scan format."""
    print("\n" + "=" * 90)
    print("FINAL BRACKET")
    print("=" * 90)

    for round_data in rounds:
        print(f"\n{round_data['name']} (Round {round_data['round']})")
        print("-" * 90)
        for idx, matchup in enumerate(round_data["matchups"], start=1):
            team1 = f"({matchup['team1_seed']}) {matchup['team1']}"
            team2 = f"({matchup['team2_seed']}) {matchup['team2']}"
            winner = f"({matchup['winner_seed']}) {matchup['winner']}"
            print(f"{idx:>2}. {team1:<34} vs {team2:<34} -> {winner}")

    print("\n" + "=" * 90)
    print(f"CHAMPION: ({champion[1]}) {champion[0]}")
    print("=" * 90)

# --- Helper Function: Process the Full Tournament List ---
def process_tournament(bracket, tournament_year, stats_df):
    """
    Processes a tournament bracket provided as a list of tuples (team_name, seed). Every two consecutive
    entries are treated as a matchup. For each matchup, the function scrapes content for both teams (with caching) and
    then evaluates the predicted outcome using the LLM.
    
    Returns a list of dictionaries with matchup details and predictions.
    """
    predictions = []
    rounds = []
    current_bracket = bracket[:]
    round_num = 1

    while len(current_bracket) > 1:
        round_name = get_round_name(len(current_bracket))
        print(f"\n{'#' * 20} {round_name} {'#' * 20}\n")
        next_round = []
        round_matchups = []

        for i in range(0, len(current_bracket), 2):
            _team1 = current_bracket[i]
            _team2 = current_bracket[i + 1]
            print(f"Processing matchup: {_team1[0]} (Seed {_team1[1]}) vs {_team2[0]} (Seed {_team2[1]})")

            # Scrape or load cached content for each team.
            content_team1 = scrape_team_content(_team1[0], tournament_year)
            content_team2 = scrape_team_content(_team2[0], tournament_year)
            matchup_content = scrape_matchup_content(_team1[0], _team2[0], tournament_year)

            # Grab team stats
            team1 = (*_team1, get_team_stats(_team1[0], stats_df))
            team2 = (*_team2, get_team_stats(_team2[0], stats_df))

            # Evaluate the matchup using the LLM.
            prediction = evaluate_matchup(team1, team2, content_team1, content_team2, matchup_content, tournament_year)
            winner = extract_winner(prediction)
            # prediction = random.choice([team1[0], team2[0]])
            # winner = prediction

            if winner == team1[0]:
                winner_team = _team1
            elif winner == team2[0]:
                winner_team = _team2
            else:
                raise ValueError(f"Prediction {winner} does not match a team {team1[0]}, {team2[0]}")

            predictions.append({
                "round": round_num,
                "round_name": round_name,
                "matchup": f"{team1[0]} vs {team2[0]}",
                "winner": winner_team[0],
                "prediction": prediction,
            })

            round_matchups.append({
                "team1": _team1[0],
                "team1_seed": _team1[1],
                "team2": _team2[0],
                "team2_seed": _team2[1],
                "winner": winner_team[0],
                "winner_seed": winner_team[1],
            })

            next_round.append(winner_team)

            # Sleep briefly to mitigate rate limits.
            time.sleep(2)
            print("=" * 50)
            print("\n" * 2)
            print(prediction)
            print("\n" * 2)
            print(f"Winner: {winner_team[0]}")
            print("\n" * 2)

        rounds.append({
            "round": round_num,
            "name": round_name,
            "matchups": round_matchups,
        })
        current_bracket = next_round
        round_num += 1

    champion = current_bracket[0]
    return predictions, rounds, champion

# --- Main Execution Example ---
if __name__ == "__main__":
    tournament_year = 2026
    tournament_list = brackets[tournament_year]

    stats_fp = os.path.join(defs.DATA_DIR, str(tournament_year), "season.csv")
    stats_df = pd.read_csv(stats_fp)

    # Process the tournament bracket and print predictions.
    predictions, rounds, champion = process_tournament(tournament_list, tournament_year, stats_df)
    print_bracket_summary(rounds, champion)
