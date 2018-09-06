
CREATE TABLE players (
  player_id INTEGER PRIMARY KEY,
  first_name TEXT,
  second_name TEXT,
  matches_played INT,
  goals_score INT,
  goals_conceded int
 );
CREATE TABLE matches (
  match_id INTEGER  PRIMARY KEY,
  away_player TEXT,
  home_player TEXT,
  away_goals INT,
  home_goals INT,
  winner INT
);

