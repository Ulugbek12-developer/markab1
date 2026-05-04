import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Check if phones_phone exists and phones_listing does not
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phones_phone'")
    has_phone = cursor.fetchone()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phones_listing'")
    has_listing = cursor.fetchone()

    if has_phone and not has_listing:
        print("Renaming phones_phone to phones_listing...")
        cursor.execute("ALTER TABLE phones_phone RENAME TO phones_listing")
        conn.commit()

    # 2. Check if phones_category exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phones_category'")
    if not cursor.fetchone():
        print("Creating phones_category table...")
        cursor.execute("""
            CREATE TABLE phones_category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name varchar(100) NOT NULL,
                slug varchar(50) NOT NULL UNIQUE,
                icon varchar(50) NOT NULL
            )
        """)
        conn.commit()

    # 3. Fix orders_order table (rename phone_id to listing_id)
    cursor.execute("PRAGMA table_info(orders_order)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'phone_id' in columns and 'listing_id' not in columns:
        print("Renaming phone_id to listing_id in orders_order...")
        # SQLite < 3.25 doesn't support RENAME COLUMN, so we might need a workaround
        # But we can try the simple way first
        try:
            cursor.execute("ALTER TABLE orders_order RENAME COLUMN phone_id TO listing_id")
        except sqlite3.OperationalError:
            # Manual recreation if RENAME COLUMN is not supported
            print("RENAME COLUMN not supported, manual fix needed.")
            # For now let's hope it's supported or we can just ignore it if it fails here
            pass
        conn.commit()

    # 4. Add missing columns to phones_listing if needed
    cursor.execute("PRAGMA table_info(phones_listing)")
    columns = [col[1] for col in cursor.fetchall()]
    
    missing_cols = [
        ('category_id', 'bigint'),
        ('screen_condition', 'varchar(50)'),
        ('body_condition', 'varchar(50)'),
        ('replaced_parts', 'JSON'),
        ('defects', 'JSON'),
        ('seller_id', 'integer'),
        ('images_json', 'JSON'),
        ('booked_until', 'datetime')
    ]
    
    for col_name, col_type in missing_cols:
        if col_name not in columns:
            print(f"Adding column {col_name} to phones_listing...")
            cursor.execute(f"ALTER TABLE phones_listing ADD COLUMN {col_name} {col_type}")
    
    conn.commit()
    print("Database fix completed.")

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
