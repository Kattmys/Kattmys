import os
import toml
import json

import flask
from werkzeug.middleware.proxy_fix import ProxyFix
from markdown import markdown

from kattbas.database import User, Database
from kattbas.errors import *

Flask = flask.Flask
render_template = flask.render_template
request = flask.request

app = Flask(__name__)

# App is behind one proxy that sets the -For and -Host headers.
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1
)

Database.init()

with open("data/content.toml", encoding="utf-8") as f:
    data = toml.load(f)["posts"]

with open("data/downloads.toml", encoding="utf-8") as f:
    downloads = toml.load(f)

# Huvudsidan

@app.route("/")
@app.route("/home")
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
    return render_template(r"sigge.html")

@app.route("/bonzo")
def page_katt_bonzo():
    return render_template(r"bonzo.html")

# login
@app.route("/login")
def page_login():
    try:
        user = User.from_cookie(request)

    except CookieError as e:
        print(type(e))
        return render_template(r"login.html", sign_up=False)

    return render_template(r"index.html", user=user)

@app.route("/signup")
def page_sign_up():
    return render_template(r"login.html", sign_up=True)

@app.route("/logout")
def page_log_out():
    response = flask.make_response(render_template(r"index.html", user=None))

    response.set_cookie("AUTH", json.dumps(None))

    return response

@app.route("/handle_sign_up", methods=["POST"])
def handle_sign_up():
    if request.method == "POST":
        username = request.form["uname"]
        email = request.form["email"]
        password = request.form["psw"]

        try:
            user, cookie = User.sign_up(username, email, password)

        except EmailOccupied:
            return render_template(r"login.html", 
                                   sign_up=True, 
                                   msg="Epost-adressen är redan regestrerad till ett annat konto!")

        except UsernameOccupied:
            return render_template(r"login.html", 
                                   sign_up=True, 
                                   msg="Användarnamnet är upptaget, välj ett annat.")

        response = flask.make_response(render_template(r"index.html", user=user))

        if cookie is not None:
            response.set_cookie("AUTH", cookie)

        return response
@app.route("/handle_log_in", methods=["POST"])
def handle_log_in():
    email = request.form["email"]
    password = request.form["psw"]

    try:
        user, cookie = User.log_in(email, password)

    except (InvalidPassword, InvalidEmail):
        return render_template(r"login.html", 
                               sign_up=False, 
                               msg="Fel epost eller lösenord. Försök igen.")
        
    # ska visa användarprofil i framtiden
    response = flask.make_response(render_template(r"index.html", user=user))

    if cookie is not None:
        response.set_cookie("AUTH", cookie)
    return response

# Start

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
