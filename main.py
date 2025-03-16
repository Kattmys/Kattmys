import os
import json

from markdown import markdown # pip install markdown

import flask
# from flask import Flask, render_template
Flask = flask.Flask
render_template = flask.render_template

app = Flask(__name__)

with open("data/content.json", encoding="utf-8") as f:
    data = json.load(f)

with open("data/downloads.json", encoding="utf-8") as f:
    downloads = json.load(f)

# Huvudsidan

@app.route("/")
def home():
    return render_template(r"index.html", data=data)

# Nedladdningar

@app.route("/download/<file>")
def page_download(file):
    try:
        download_data = downloads[file]
        return render_template("/download.html", data=download_data)

    except KeyError:
        # return render_template(
        #     "/download.html",
        #     data={
        #         "name": f"404 Invalid address '{file}'",
        #         "error": True
        #     })

        return flask.redirect('/404')

# Småsidor

@app.route("/page/<name>")
def page_page(name):
    try:
        with open(f"static/pages/{name}.md") as file:
            html = markdown(file.read())
            print(html)
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
    app.run(debug=True, host="0.0.0.0", port=50000)
