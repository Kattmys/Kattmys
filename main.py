import os
import toml
import json

import flask
from werkzeug.middleware.proxy_fix import ProxyFix
from markdown import markdown

from kattbas.database import User, Database
from kattbas.errors import *

render_template = flask.render_template
request = flask.request
redirect = flask.redirect

app = flask.Flask(__name__)

# App is behind one proxy that sets the -For and -Host headers.
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1
)

Database.init()

with open("data/content.toml", encoding="utf-8") as f:
    content = toml.load(f)["posts"]

with open("data/downloads.toml", encoding="utf-8") as f:
    downloads = toml.load(f)

# NOTE: Ska användas av andra sidor.
#       Kanske temporärt.
@app.route("/get-cookie")
def get_cookie():
    cookie = request.cookies.get("auth")
    if cookie:
        return json.dumps({
            "found": True,
            "cookie": cookie
        })
    else:
        return json.dumps({"found": False})

@app.context_processor
def inject_user():
    try:
        user = User.from_cookie(request)
        return dict(user=user)

    except CookieError as e:
        return dict(user=None)

# Huvudsidan

@app.route("/")
def home():
    return render_template("index.html", data=content)

# Felmeddelanden

error_msgs = {
    404: "Den angivna addressen hittades inte på sidan. Om du angav addressen manuellt, kontrollera din stavning och försök igen!",
    500: "Någon av Kattmysnätverkets utvecklare kan inte programmera, och ett fel har därför uppstått i koden. Rapportera det gärna till oss!",
}

@app.errorhandler(404)
def err_page_not_found(e):
    return render_template(r"error.html", code="404", msg=error_msgs[404])

@app.errorhandler(500)
def err_internal_server_error(e):
    return render_template(r"error.html", code="500", msg=error_msgs[500])

# Nedladdningar

@app.route("/download/<file>")
def page_download(file):
    try:
        download_data = downloads[file]
        return render_template("/download.html", data=download_data)

    except KeyError:
        return redirect('/404')

# Småsidor

@app.route("/page/<name>")
def page_page(name):
    try:
        with open(f"static/pages/{name}.md", encoding="utf-8") as file:
            html = markdown(file.read())
            # NOTE: pissful .replace användning
            return render_template("/page.html").replace("REPLACE_THIS", html)

    except FileNotFoundError:
        return redirect('/404')

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
    return render_template(r"login.html", sign_up=False)

@app.route("/handle_log_in", methods=["POST"])
def handle_log_in():
    email = request.form["email"]
    password = request.form["psw"]

    try:
        user, db_cookie = User.log_in(email, password)

    except (InvalidPassword, InvalidEmail):
        return render_template(r"login.html", 
                               sign_up=False, 
                               msg="Fel mejladdress eller lösenord. Försök igen.")
        
    # ska visa användarprofil i framtiden
    response = flask.make_response(redirect("/"))

    # if db_cookie is not None:
    response.set_cookie(
        "auth", db_cookie, max_age=604800,
        httponly=True, samesite="Lax"
    )

    return response

@app.route("/signup")
def page_sign_up():
    return render_template(r"login.html", sign_up=True)

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
                                   msg="Mejladdressen är upptagen.")

        except UsernameOccupied:
            return render_template(r"login.html", 
                                   sign_up=True, 
                                   msg="Användarnamnet är upptaget.")

        except (BadEmail, BadUsername, BadPassword) as e:
            return render_template(r"login.html", 
                                   sign_up=True, 
                                   msg=str(e))

        response = flask.make_response(redirect("/"))

        if cookie is not None:
            response.set_cookie(
                "auth", cookie, max_age=604800,
                httponly=True, samesite="Lax"
            )

        return response

@app.route("/logout")
def page_log_out():
    response = flask.make_response(redirect("/"))

    response.set_cookie(
        "auth", expires=0,
        httponly=True, samesite="Lax"
    )

    return response

# admin (extremt temporärt; gör det snabbt för att theo sög)
# @app.route("/change_password")
# def psw_change():
#     try:
#         user = User.from_cookie(request)

#     except CookieError as e:
#         return redirect("/")

#     if user.id in admin_ids:
#         return render_template(r"change_psw.html")

# @app.route("/handle_psw_change", methods=["POST"])
# def handle_psw_change():
#     user = User.from_cookie(request)
    
#     if user.id not in admin_ids:
#         return redirect("/", data=data)

#     user = User(username=request.form["uname"])
#     user.change_password(request.form["psw"])

#     return redirect("/")

@app.route("/user/<user>") #, methods=["POST"]
def user_home(user):
    user     = User(username=user)
    return render_template(r"home.html", user_page=user)

# Start

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)#, debug=True)
