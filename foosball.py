from contextlib import closing
from os import path, remove
from texttable import Texttable
import sqlite3



current_dir = path.dirname((path.abspath(__file__)))
schema_sql = """CREATE TABLE players (
  player_id INTEGER PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  matches_played INT,
  goals_scored INT,
  goals_conceded INT,
  matches_won INT,
  points INT
 );
CREATE TABLE match (
  match_id INTEGER  PRIMARY KEY,
  home_player TEXT,
  away_player TEXT,
  home_goals INT,
  away_goals INT,
  winner TEXT
);
"""

db_file = "foosball.db"


def create_database(*, force=False):
    """Creating a database file
    :param force: used to overwrite database if previous version exist
    :type force: bool
    """
    if force:
        try:
            remove(db_file)
        except OSError:
            pass
    with closing(sqlite3.connect(db_file)) as db:
        db.executescript(schema_sql)


def add_player(*, first_name, last_name):
    """adding a player to a league
    :param first_name: first name of player to be added
    :type first_name: str
    :param last_name: last name of participant
    :type last_name: str
    """
    matches_played = goals_scored = goals_conceded = matches_won = points = 0
    with closing(sqlite3.connect(db_file)) as db, db:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO players (first_name, last_name, matches_played, goals_scored, goals_conceded, matches_won, points) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (first_name, last_name, matches_played, goals_scored, goals_conceded, matches_won, points)
        )


def _search(*, first_name=None, last_name=None, table="players", column="*", match_id=None, sort=False):
    """
    used to query database tables
    :param first_name: participant first name (defaults to None)
    :type first_name: str
    :param last_name: participant last name (defaults to None)
    :type last_name: str
    :param table: table to query (defaults to players table)
    :type table: str
    :param column: table column to query (defaults to *)
    :type column: str
    :param match_id: particular match id to query (defaults to None)
    :type match_id: int
    :param sort: sort points value in table
    :type sort: bool
    :return result: query result
    :rtype result: list
    """
    if first_name:
        query = f"""
        SELECT {column} FROM {table}
        WHERE (first_name LIKE "{first_name}") 
        or (last_name LIKE "{last_name}");
        """
    elif match_id:
        query = f"""
        SELECT {column} FROM {table}
        WHERE (match_id = {match_id});
        """
    elif sort:
        query = f"""
        SELECT {column} FROM {table}
        ORDER BY points DESC;
        """
    else:
        query = f"""
        SELECT {column} FROM {table}
        """
    with closing(sqlite3.connect(db_file)) as db:
        cur = db.cursor()
        cur.execute(query)
        result = [details for details in cur]
        if not result:
            result = f"no data found"
        return result


def delete_player(*, first_name, last_name):
    """deleting a player to a league
    :param first_name: first name of player to be added
    :type first_name: str
    :param last_name: last name of participant
    :type last_name: str
    """
    query = f"""
    DELETE * FROM players
    WHERE (first_name LIKE "{first_name}") 
    and (last_name LIKE "{last_name}");
    """
    with closing(sqlite3.connect(db_file)) as db:
        cur = db.cursor()
        cur.execute(query)


def _fixtures():
    """Make league fixtures in match table"""
    away_goals = home_goals = 0
    players = _search()
    for match, player_1 in enumerate(players):
        for match_2, player_2 in enumerate(players):
            if player_1 != player_2:
                with closing(sqlite3.connect(db_file)) as db, db:
                    cur = db.cursor()
                    cur.execute("INSERT INTO match (home_player, away_player, home_goals, away_goals, winner) values (?, ?, ?, ?, ?)",
                                (player_1[1], player_2[1], home_goals, away_goals, "NULL"))


def show_fixtures():
    """Display league fixtures"""
    fixtures = _search(table="match")
    table = Texttable()
    table.header(["Match_id", "Home_player", "Away_player", "Home_goals", "Away_goals", "Winner"])
    table.set_deco(table.HEADER | table.VLINES)

    for fixture in fixtures:
        row = [*fixture]
        table.add_row(row)
    return table.draw()


def add_result(*, match_id, home_goals, away_goals):
    """adding match result
    :param match_id: match unique identifier
    :type match_id: int
    :param home_goals: home player goals scored
    :type home_goals: int
    :param away_goals: away player goals scored
    :type away_goals: int
    """
    match_id, home_player, away_player, home_goal, away_goal, winner = _search(table="match", match_id=match_id)[0]
    home_player_id, _, _, home_player_matches_played, home_player_goals_scored, home_player_goals_against, home_player_matches_won, home_player_points = _search(first_name=home_player)[0]
    away_player_id, _, _, away_player_matches_played, away_player_goals_scored, away_player_goals_against, away_player_matches_won, away_player_points = _search(first_name=away_player)[0]
    home_player_matches_played += 1
    away_player_matches_played += 1

    if int(home_goals) > int(away_goals):
        winner = home_player
        home_player_goals_scored += home_goals
        home_player_goals_against += away_goals
        away_player_goals_scored += away_goals
        away_player_goals_against += home_goals
        home_player_matches_won += 1
        home_player_points += 3
    else:
        winner = away_player
        away_player_goals_scored += away_goals
        away_player_goals_against += home_goals
        home_player_goals_scored += home_goals
        home_player_goals_against += away_goals
        away_player_matches_won += 1
        away_player_points += 3

    update = f"""UPDATE match SET home_goals = {home_goals}, 
    away_goals = {away_goals}, winner = "{winner}" WHERE (match_id = {match_id});
    UPDATE players SET matches_played = {home_player_matches_played}, 
    goals_scored = {home_player_goals_scored}, goals_conceded = {home_player_goals_against}, 
    matches_won = {home_player_matches_won}, points = {home_player_points} WHERE (player_id = {home_player_id});
    UPDATE players SET matches_played = {away_player_matches_played}, 
    goals_scored = {away_player_goals_scored}, goals_conceded = {away_player_goals_against}, 
    matches_won = {away_player_matches_won}, points = {away_player_points} WHERE (player_id = {away_player_id});
    """
    with closing(sqlite3.connect(db_file)) as db, db:
        cur = db.cursor()
        cur.executescript(update)


def league_table():
    """Display league table"""
    table = Texttable()
    table.header(["Player_id", "Name", "Played", "Won", "For", "Against", "Points"])
    table.set_deco(table.HEADER | table.VLINES)
    player_table = _search(sort=True)
    for player in player_table:
        player_id, first_name, last_name, matches_played, goals_scored, goals_against, matches_won, points = player
        row = [player_id, f"{first_name} {last_name}", matches_played, matches_won, goals_scored, goals_against, points]
        table.add_row(row)
    return table.draw()


if __name__ == "__main__":
    # create_database(force=True)
    # add_player(first_name="Ben", last_name="Sunny")
    # add_player(first_name="Jack", last_name="New")
    # add_player(first_name="rick", last_name="sarge")
    # _fixtures()
    # add_result(match_id=1, home_goals=5, away_goals=7)
    # add_result(match_id=2, home_goals=9, away_goals=6)
    # add_result(match_id=3, home_goals=2, away_goals=4)
    # print(show_fixtures())
    # print("")
    # print(show_fixtures())
    print(league_table())
