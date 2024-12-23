LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/nba_teams_with_correct_team_ids.csv' 
INTO TABLE nba_teams
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;




