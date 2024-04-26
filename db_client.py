import sqlite3
from pprint import pprint


def get_conn():
    conn = sqlite3.connect('flat.db')
    return conn


def create_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS flat(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flat_id TEXT unique,
    title TEXT,
    price INTEGER,
    image TEXT,
    discription TEXT,
    room INTEGER,
    square INTEGER,
    year INTEGER,
    floor INTEGER,
    type_house TEXT,
    region TEXT,
    city TEXT,
    street TEXT,
    district TEXT,
    coordinate TEXT
    )
    """)

    conn.close()

def insert_flat(flat: dict) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO flat(
    flat_id,
    title,
    price,
    image,
    discription,
    room,
    square,
    year,
    floor,
    type_house,
    region,
    city,
    street,
    district,
    coordinate
    ) VALUES (
    :flat_id,
    :title,
    :price,
    :image,
    :discription,
    :room,
    :square,
    :year,
    :floor,
    :type_house,
    :region,
    :city,
    :street,
    :district,
    :coordinate
    ) ON CONFLICT (flat_id) DO UPDATE SET price = :price
    """, flat)

    conn.commit()

    conn.close()


def get_data(query: str, params=None):
    conn = get_conn()
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    res = cur.fetchall()

    conn.close()
    return res

q = """SELECT * FROM flat"""
flats = get_data(q)
pprint(flats)
