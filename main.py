import os
import json
from flask import Flask, render_template

app = Flask(__name__)
with open("data/content.json", encoding="utf-8") as f:
    data = json.load(f)

if __name__ == '__main__':
   app.run()

@app.route("/")
def home():
    return render_template(r"index.html", data=data)



@app.route("/download/snake_jack.html")
def snake_jack():
    return render_template(r"download/snake_jack.html")

@app.route("/download/snake_francis.html")
def snake_francis():
    return render_template(r"download/snake_francis.html")



@app.route("/sigge")
def katt_sigge():
    return render_template(r"katter/sigge.html")

@app.route("/bonzo")
def katt_bonzo():
    return render_template(r"katter/bonzo.html")

if __name__ == "__main__":
    app.run(debug=True)

