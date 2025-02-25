import os
import json
import pprint
from flask import Flask, render_template

# Hej!

app = Flask(__name__)
with open("data/content.json", encoding="utf-8") as f:
    data = json.load(f)
    pprint.pp(data)

if __name__ == '__main__':
   app.run()

@app.route("/")
def home():
    return render_template(r"index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)

