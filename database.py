import aiosqlite
import json
from config import config

async def init_db():
    async with aiosqlite.connect(config.DB_NAME) as db:
        # Re-initialize ads table with all columns
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                brand TEXT,
                model TEXT,
                photos TEXT,
                battery TEXT,
                storage TEXT,
                condition TEXT,
                screen_condition TEXT,
                body_condition TEXT,
                description TEXT,
                region TEXT,
                box TEXT,
                price TEXT,
                contact TEXT,
                branch TEXT,
                replaced_parts TEXT,
                defects TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS price_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                model TEXT,
                photos TEXT,
                battery_range TEXT,
                storage TEXT,
                condition TEXT,
                screen_condition TEXT,
                body_condition TEXT,
                region TEXT,
                box TEXT,
                replaced_parts TEXT,
                defects TEXT,
                calculated_price TEXT,
                admin_price TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                location TEXT
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'uz',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed initial branches
        await db.execute("DELETE FROM branches")
        initial_branches = [
            ("Malika", "https://maps.google.com/maps?q=41.339919,69.270824&ll=41.339919,69.270824&z=16"),
            ("Chilonzor", "https://maps.google.com/maps?q=41.274714,69.203840&ll=41.274714,69.203840&z=16")
        ]
        await db.executemany("INSERT INTO branches (name, location) VALUES (?, ?)", initial_branches)

        # Migration columns
        columns_ads = [
            ("branch", "TEXT"), ("region", "TEXT"), ("box", "TEXT"), 
            ("status", "TEXT DEFAULT 'pending'"), ("price", "TEXT"),
            ("replaced_parts", "TEXT"), ("defects", "TEXT"),
            ("screen_condition", "TEXT"), ("body_condition", "TEXT")
        ]
        columns_price = [
            ("replaced_parts", "TEXT"), ("defects", "TEXT"),
            ("screen_condition", "TEXT"), ("body_condition", "TEXT"),
            ("region", "TEXT"), ("box", "TEXT")
        ]
        
        for col_name, col_type in columns_ads:
            try: await db.execute(f"ALTER TABLE ads ADD COLUMN {col_name} {col_type}")
            except: pass
        for col_name, col_type in columns_price:
            try: await db.execute(f"ALTER TABLE price_requests ADD COLUMN {col_name} {col_type}")
            except: pass

        await db.commit()

async def get_all_branches():
    async with aiosqlite.connect(config.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM branches") as cursor:
            return await cursor.fetchall()

async def add_branch(name: str, location: str = ""):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO branches (name, location) VALUES (?, ?)", (name, location))
        await db.commit()

async def delete_branch(name: str):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute("DELETE FROM branches WHERE name = ?", (name,))
        await db.commit()

async def delete_ad(ad_id: int):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
        await db.commit()

async def add_ad(data: dict):
    async with aiosqlite.connect(config.DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO ads (user_id, brand, model, photos, battery, storage, condition, screen_condition, body_condition, description, region, box, price, contact, branch, replaced_parts, defects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('user_id'),
            data.get('brand', 'iPhone'),
            data.get('model'),
            ",".join(data.get('photos', [])),
            data.get('battery'),
            data.get('storage', data.get('memory')),
            data.get('condition'),
            data.get('screen_condition'),
            data.get('body_condition'),
            data.get('description'),
            data.get('region'),
            data.get('box'),
            data.get('price'),
            data.get('contact'),
            data.get('branch'),
            json.dumps(data.get('replaced_parts', [])),
            json.dumps(data.get('defects', []))
        ))
        ad_id = cursor.lastrowid
        await db.commit()
        return ad_id

async def add_price_request(data: dict):
    async with aiosqlite.connect(config.DB_NAME) as db:
        cursor = await db.execute("""
            INSERT INTO price_requests (user_id, model, photos, battery_range, storage, condition, screen_condition, body_condition, region, box, replaced_parts, defects, calculated_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('user_id'),
            data.get('model'),
            ",".join(data.get('photos', [])),
            data.get('battery_range', data.get('battery')),
            data.get('storage'),
            data.get('condition'),
            data.get('screen_condition'),
            data.get('body_condition'),
            data.get('region'),
            data.get('box'),
            json.dumps(data.get('replaced_parts', [])),
            json.dumps(data.get('defects', [])),
            data.get('calculated_price')
        ))
        req_id = cursor.lastrowid
        await db.commit()
        return req_id

async def update_price_request(req_id: int, admin_price: str):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute("UPDATE price_requests SET admin_price = ?, status = 'responded' WHERE id = ?", (admin_price, req_id))
        await db.commit()

async def get_price_request(req_id: int):
    async with aiosqlite.connect(config.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM price_requests WHERE id = ?", (req_id,)) as cursor:
            return await cursor.fetchone()

async def update_ad_status(ad_id: int, status: str, branch: str = None):
    async with aiosqlite.connect(config.DB_NAME) as db:
        if branch:
            await db.execute("UPDATE ads SET status = ?, branch = ? WHERE id = ?", (status, branch, ad_id))
        else:
            await db.execute("UPDATE ads SET status = ? WHERE id = ?", (status, ad_id))
        await db.commit()

async def get_ad_by_id(ad_id: int):
    async with aiosqlite.connect(config.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)) as cursor:
            return await cursor.fetchone()

async def search_ads(model=None, branch=None):
    # Search from Django DB directly to sync with Web App
    import os
    django_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
    if not os.path.exists(django_db_path):
        django_db_path = 'db.sqlite3' # fallback
        
    async with aiosqlite.connect(django_db_path) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT id, model_name as model, memory as storage, battery_health as battery, condition, price, branch, image as photos FROM phones_listing WHERE is_approved = 1 AND is_booked = 0"
        params = []
        if model:
            model = model.strip()
            query += " AND model_name LIKE ?"
            params.append(f"%{model}%")
        if branch:
            branch = branch.strip()
            query += " AND branch = ?"
            params.append(branch.lower())
        
        query += " ORDER BY created_at DESC"
        
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

async def book_listing(listing_id: int, hours: int = 48):
    import os
    from datetime import datetime, timedelta
    django_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
    if not os.path.exists(django_db_path): django_db_path = 'db.sqlite3'
    
    until = (datetime.now() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    async with aiosqlite.connect(django_db_path) as db:
        await db.execute("UPDATE phones_listing SET is_booked = 1, booked_until = ? WHERE id = ?", (until, listing_id))
        await db.commit()

async def update_user_language(user_id, lang):
    async with aiosqlite.connect(config.DB_NAME) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()

async def get_user_language(user_id):
    async with aiosqlite.connect(config.DB_NAME) as db:
        # First ensure user exists
        async with db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
                await db.commit()
                return 'uz'
async def get_admin_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM ads") as cursor:
            total_ads = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM price_requests") as cursor:
            total_price_requests = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM ads WHERE status = 'approved'") as cursor:
            active_ads = (await cursor.fetchone())[0]
            
        return {
            'users': total_users,
            'ads': total_ads,
            'price_requests': total_price_requests,
            'active_ads': active_ads
        }
