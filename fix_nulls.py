import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute("UPDATE phones_listing SET images_json = '[]' WHERE images_json IS NULL")
cursor.execute("UPDATE phones_listing SET replaced_parts = '[]' WHERE replaced_parts IS NULL")
cursor.execute("UPDATE phones_listing SET defects = '[]' WHERE defects IS NULL")
conn.commit()
print(f"Updated rows: {cursor.rowcount}")
conn.close()
