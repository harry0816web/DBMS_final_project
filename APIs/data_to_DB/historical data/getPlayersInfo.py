import csv
import pymysql

def insert_into_database(player_data):
    # Establish a connection to the MySQL database
    conn = pymysql.connect(
        host="nba-database.czg6ogiualx5.ap-southeast-2.rds.amazonaws.com",
        user="admin",
        password="admin1234",
        database="nba_database",
        charset="utf8mb4"
    )
    cursor = conn.cursor()
    try:
        # Define the SQL query for inserting data
        query = """
        INSERT INTO player_details (PERSON_ID, DISPLAY_FIRST_LAST, TEAM_NAME, TEAM_ABBREVIATION, JERSEY, HEIGHT, WEIGHT, POSITION)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Execute the query with the player data
        cursor.executemany(query, player_data)
        conn.commit()
        print("Data successfully inserted into the database!")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

def read_csv_and_insert_to_db(csv_file):
    player_data = []
    # Open the CSV file and read its content
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            player_data.append((
                int(row["PERSON_ID"]),
                row["DISPLAY_FIRST_LAST"],
                row["TEAM_NAME"],
                row["TEAM_ABBREVIATION"],
                row["JERSEY"] if row["JERSEY"] else None,
                row["HEIGHT"] if row["HEIGHT"] else None,
                row["WEIGHT"] if row["WEIGHT"] else None,
                row["POSITION"] if row["POSITION"] else None
            ))

    # Insert the data into the database
    insert_into_database(player_data)

# Run the script
if __name__ == "__main__":
    # Path to the CSV file
    csv_file = "common_all_players_detailed.csv"
    read_csv_and_insert_to_db(csv_file)
