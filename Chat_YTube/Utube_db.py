import sqlite3

conn= sqlite3.connect("Utube_watch.db")

create_query= """CREATE TABLE IF NOT EXISTS Watchlist( sno integer primary key, 
                search_query VARCHAR(100), desire_tone VARCHAR(100), llm_response VARCHAR(100), url VARCHAR(100), 
                category VARCHAR(100), title VARCHAR(100), descr_video VARCHAR(150)) 
              """

conn.execute(create_query)
print("Table Created !")
conn.commit()

def insert_values_tables(sno: int, query, tone, llm_response, url, category, title, descr):
    insert_query = """INSERT INTO Watchlist (sno, search_query, desire_tone, llm_response, url, category, title, descr_video)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    conn.execute(insert_query, (sno, query, tone, llm_response, url, category, title, descr))
    print("Values Inserted!")

insert_values_tables(1, "Motivation", "motivated", "Motivational Songs Tamil","https://www.youtube.com/watch?v=01x2y3z","motive", "Fearless", "Lost Sky")
conn.commit()