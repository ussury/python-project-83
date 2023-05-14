from flask import Flask, render_template, request, redirect, url_for, flash, \
    get_flashed_messages
from page_analyzer import db
from validators import url as is_correct
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'super secret key'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    messag = get_flashed_messages(with_categories=True)
    if request.method == 'POST':
        url_site = request.form['url']

        if not is_correct(url_site):
            flash('Некорректный URL', 'alert-danger')
            return render_template('index.html', messag), 422

        parsed_url = urlparse(url_site)
        norm_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

        if db.get_id_by_name(norm_url):
            flash("Страница уже существует", "alert-info")
        else:
            flash("Страница успешно добавлена", "alert-success")
            db.add_site(norm_url)
        site_id = db.get_id_by_name(norm_url)
        return redirect(url_for('site', site_id=site_id))

    urls = db.all_sites()
    return render_template('urls.html', urls=urls, messages=messag)


@app.route('/urls/<int:site_id>')
def site(site_id):
    site = db.get_site(site_id)
    return render_template('site.html', url=site)
