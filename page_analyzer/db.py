import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def add_site(site):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)",
                        (site, 'now()'))
            conn.commit()


def all_sites():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT urls.id, urls.name, '
                        'url_checks.created_at, url_checks.status_code '
                        'FROM urls LEFT JOIN url_checks '
                        'ON urls.id=url_checks.url_id '
                        'AND url_checks.created_at=(SELECT MAX(created_at) '
                        'FROM url_checks WHERE url_id=urls.id) '
                        'ORDER BY urls.id DESC'
                        )
            rows = cur.fetchall()

    return [{'id': row[0],
             'name': row[1],
             'date': row[2].strftime("%d.%m.%y") if row[2] else '',
             'status_code': row[3]} for row in rows]


def get_site(id):
    """
    Получить идентификатор и вернуть данные сайта(dict) из базы данных
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM urls WHERE id = %s', (id,))
            row = cur.fetchone()

    return {
        'id': row[0],
        'name': row[1],
        'created_at': row[2].strftime("%d.%m.%y") if row[2] else ''
    }


def get_id_by_name(site_name):
    """
    Получить URL-адрес и вернуть идентификатор из базы данных, если существует,
    иначе возвращает None.
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM urls WHERE name=%s', (site_name,))
            id_ = cur.fetchone()

    return id_[0] if id_ else None


def add_check(data):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO url_checks (url_id, status_code, h1,'
                'title, description, created_at)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (data.get('id'), data.get('code'),
                 data.get('h1'), data.get('title'),
                 data.get('description'),
                 'now()')
            )
            conn.commit()


def get_checks(id):
    """
    Получить id и вернуть
    результаты проверки (list of dicts) из базы данных.
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM url_checks '
                        'WHERE url_id=%s ORDER BY id DESC', (id,))
            rows = cur.fetchall()

    return [{'id': row[1],
             'code': row[2],
             'h1': row[3],
             'title': row[4],
             'description': row[5],
             'created_at': row[6].strftime("%d.%m.%y") if row[6] else ''
             } for row in rows]
