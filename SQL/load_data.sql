LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/common_all_players.csv' 
INTO TABLE common_all_players
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;




