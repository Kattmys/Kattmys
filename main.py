import os
import json
import random

import flask
from flask import Flask, render_template, url_for, request
from markdown import markdown

app = Flask(__name__)

with open("data/content.json", encoding="utf-8") as f:
    data = json.load(f)

with open("data/downloads.json", encoding="utf-8") as f:
    downloads = json.load(f)

with open("data/todo.json", encoding="utf-8") as f:
    todo_lists = json.load(f)

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


# Todo app

# def add_task(lists, list_id, task_name=""):
#     for lst in lists:
#         if lst["id"] == list_id:
#             new_id = max(task["id"] for task in lst["tasks"]) + 1 if lst["tasks"] else 1

#             lst["tasks"].append({
#                 "id": new_id, 
#                 "name": task_name, 
#                 "checed": False
#             })

#             return True
#     return False


@app.route("/todo", methods=["GET", "POST"])
def todo():
    # if request.method == "POST":
    #     todo_name = request.form["todo_name"]
    #     list_id = int(request.form["list_id"])

    #     add_task(todo_lists, list_id, todo_name)
    return render_template("todo.html", data=todo_lists)

# @app.route("/todo/delete/<int:list_id>/<int:todo_id>", methods=["POST"])
# def delete_todo(list_id, todo_id):
#     global todo_lists
#     for lst in todo_lists:
#         if lst["id"] == list_id:
#             for task in lst:
#                 if task["id"] == todo_id:
#                     lst.remove(task)

@app.route("/todo/<list_id>", methods=["GET", "POST"])
def todoList(list_id):
    if list_id == None:
        return flask.redirect("/todo")

    for p_list in todo_lists:
        p_list_id = p_list["id"]
        print("list:")
        print(str(p_list["id"]) + "\n\n")
        print("lists:")
        print(str("list-id: " + list_id) + "\n\n\n\n")
        if p_list_id == list_id:
            print(f"DET VAR {p_list}")
            return render_template("todo_list.html", data=p_list)

    return flask.redirect("/todo")
    

# Start

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=50000)
