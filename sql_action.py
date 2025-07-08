import sqlite3

def get_connection(db_name):
    try:
        return sqlite3.connect(db_name)
    except Exception as e:
        print(e)
        raise

def create_table(connection):
    query = """
    CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY,
    summary TEXT,
    videoId TEXT NOT NULL,
    playlistId TEXT
    )
    """
    
    try:
        with connection:
            connection.execute(query)
        print("Table was created!")
    except Exception as e:
        print(f"Error: {e}")

# Add Summary to DB
def insert_summary(connection, summary:str, videoId:str, playlistId = None):
    query = "INSERT INTO summaries (summary, videoId, playlistId) VALUES (?, ?, ?)"
    try:
        with connection:
            connection.execute(query, (summary, videoId, playlistId))
        print(f"Video: {videoId} was added to your database!")
    except Exception as e:
        print(e)

# Query the DB
def fetch_summary(connection, condition: str = None) -> list[tuple]:
    query =  "SELECT * FROM summaries"
    if condition:
        query += f"WHERE {condition}"
    
    try:
        with connection:
            rows = connection.execute(query).fetchall()
        return rows
    except Exception as e:
        print(e)

# Main Function Wrapper
def main():
    # Initialize DB
    connection = get_connection("summaries.db")
    try:
        # Create a Table in the DB
        create_table(connection)
        while True:
            start = input("Enter Option (Add, Search, Cmd+C to Quit): ").lower()
            if start == "add":
                summary = input("Enter Name: ")
                videoId = int(input("Enter Age: "))
                playlistId = input("Enter Email: ")
                insert_summary(connection, summary, videoId, playlistId)

            elif start == "search":
                print("All summaries:")
                for user in fetch_summary(connection):
                    print(user)
        
    finally:
        connection.close()



if __name__ == "__main__":
    main()