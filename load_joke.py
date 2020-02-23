# script for loading jokes from a json file to database

import sqlite3
import json

joke_file = "jokes.json"
database = "db.sqlite3"

conn = sqlite3.connect(database)
# why the need for a cursor:
# https://stackoverflow.com/questions/6318126/why-do-you-need-to-create-a-cursor-when-querying-a-sqlite-database
cur = conn.cursor()
with open(joke_file) as f:
    data = json.load(f)
assert len(data) > 0

sql = "INSERT INTO cookschedule_joke(type, setup, punchline) VALUES(?, ?, ?)"
for entry in data:
    cur.execute(sql, (entry['type'], entry['setup'], entry['punchline']))
conn.commit()
conn.close()
