from flask import Flask, render_template, request, redirect, url_for, flash, \
    get_flashed_messages
from page_analyzer import db
import validators
from urllib.parse import urlparse
import requests
from requests import exceptions as exc
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'super secret key'


def parse_site(resp):
    soup = BeautifulSoup(resp.text, 'html.parser')
    h1 = '' if soup.h1 is None else soup.h1.get_text()
    title = '' if soup.title is None else soup.title.get_text()
    content_meta = soup.find('meta', attrs={'name': 'description'})
    content = '' if content_meta is None else content_meta['content']

    return {'h1': h1, 'title': title, 'description': content}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    messages = get_flashed_messages(with_categories=True)
    if request.method == 'POST':
        url_site = request.form['url']
        parsed_url = urlparse(url_site)
        norm_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

        if not validators.url(norm_url):
            flash('Некорректный URL', 'alert-danger')
            return render_template('index.html',
                                   url=url_site,
                                   messages=messages), 422

        # parsed_url = urlparse(url_site)
        # norm_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

        if db.get_id_by_name(norm_url):
            flash("Страница уже существует", "alert-info")
        else:
            flash("Страница успешно добавлена", "alert-success")
            db.add_site(norm_url)
        site_id = db.get_id_by_name(norm_url)
        return redirect(url_for('site', site_id=site_id))

    urls = db.all_sites()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:site_id>')
def site(site_id):
    messages = get_flashed_messages(with_categories=True)
    site = db.get_site(site_id)
    checks = db.get_checks(site_id)
    return render_template('site.html', url=site,
                           checks=checks, messages=messages)


@app.post('/urls/<int:site_id>/checks')
def check_url(site_id):
    url = db.get_site(site_id)
    try:
        resp = requests.get(url['name'])
        resp.raise_for_status()
        seo_data = parse_site(resp)
        db.add_check({'id': site_id,
                      'code': resp.status_code,
                      'h1': seo_data['h1'],
                      'title': seo_data['title'],
                      'description': seo_data['description']
                      })
        flash('Страница успешно проверена', 'alert-success')

        return redirect(url_for('site', site_id=site_id))

    except (exc.ConnectionError, exc.HTTPError):
        flash('Произошла ошибка при проверке', 'alert-danger')

        return redirect(url_for('site', site_id=site_id))
