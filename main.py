import os
import json
import flask
from werkzeug.middleware.proxy_fix import ProxyFix

from markdown import markdown

Flask = flask.Flask
render_template = flask.render_template

app = Flask(__name__)

# App is behind one proxy that sets the -For and -Host headers.
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1
)

with open("data/content.json", encoding="utf-8") as f:
    data = json.load(f)

with open("data/downloads.json", encoding="utf-8") as f:
    downloads = json.load(f)

# Huvudsidan

@app.route("/")
def home():
    return render_template(r"index.html", data=data)

# 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template(r"404.html"), 404

# Nedladdningar

@app.route("/download/<file>")
def page_download(file):
    try:
        download_data = downloads[file]
        return render_template("/download.html", data=download_data)

    except KeyError:
        return flask.redirect('/404')

# Småsidor

@app.route("/page/<name>")
def page_page(name):
    try:
        with open(f"static/pages/{name}.md") as file:
            html = markdown(file.read())
            # NOTE: pissful .replace användning
            return render_template("/page.html").replace("REPLACE_THIS", html)

    except FileNotFoundError:
        return flask.redirect('/404')

# Katter

@app.route("/sigge")
def page_katt_sigge():
    return render_template(r"katter/sigge.html")

@app.route("/bonzo")
def page_katt_bonzo():
    return render_template(r"katter/bonzo.html")

# Start

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
