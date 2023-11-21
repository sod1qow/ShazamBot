import sqlite3 as sql


async def sql_connector():
    con = sql.connect('market.db')
    cur = con.cursor()
    
    return con, cur


async def create_tables():
    con, cur = await sql_connector()
    
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                user_id BIGINT PRIMARY KEY
        )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS products(
                title VARCHAR(200),
                size VARCHAR(50),
                color VARCHAR(50),
                price REAL,
                available BOOLEAN,
                category INTEGER,
                img TEXT
        )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS category(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50)
        )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS channels(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50),
            link VARCHAR(50),
            channel_id VARCHAR(50)
        )""")


async def get_categories():
    con, cur = await sql_connector()
    
    data = cur.execute("SELECT name FROM category").fetchall()
    return data


async def get_products(category):
    con, cur = await sql_connector()
    
    cat = cur.execute("SELECT id FROM category WHERE name = ?", (category,)).fetchone()
    if cat:
        data = cur.execute("SELECT * FROM products WHERE category = ?", (cat[0],)).fetchall()
        return data
    else:
        return False


async def get_product_info(product_id):
    con, cur = await sql_connector()

    product = cur.execute("SELECT * FROM products WHERE title = ?", (product_id,)).fetchone()
    return product





async def get_channels():
    con, cur = await sql_connector()
    
    channels = cur.execute("SELECT * FROM channels").fetchall()
    return channels