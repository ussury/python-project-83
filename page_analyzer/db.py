import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def add_site(site):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                    (site, 'now()'))
        conn.commit()
    conn.close()


def all_sites():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute('SELECT id, name FROM urls ORDER BY created_at DESC')
        rows = cur.fetchall()
    conn.close()
    urls = [{'id': row[0], 'name': row[1]} for row in rows]
    return urls


def get_site(site_id):
    conn = psycopg2.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s", (site_id,))
        row = cur.fetchone()
    conn.close()
    return {'id': row[0],
            'name': row[1],
            'created_at': row[2].strftime("%d/%m/%y")}


def get_id_by_name(url):
    """
    Получить URL-адрес и вернуть идентификатор из базы данных, если существует,
    иначе возвращает None.
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE name=%s', (url,))
            id_ = cur.fetchone()
    conn.close()

    return id_[0] if id_ else None
