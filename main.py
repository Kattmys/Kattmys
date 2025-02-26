import os
import json
from flask import Flask, render_template

app = Flask(__name__)

with open("data/content.json", encoding="utf-8") as f:
    data = json.load(f)

with open("data/downloads.json", encoding="utf-8") as f:
    downloads = json.load(f)

if __name__ == '__main__':
   app.run()

# Huvudsidan

@app.route("/")
def home():
    return render_template(r"index.html", data=data)

# Nedladdningar

for url in downloads:
    app.route(f"/download/{url}.html")(
        lambda: render_template(f"/download/{url}.html", data=downloads[url])
    )

# Katter

@app.route("/sigge")
def katt_sigge():
    return render_template(r"katter/sigge.html")

@app.route("/bonzo")
def katt_bonzo():
    return render_template(r"katter/bonzo.html")



if __name__ == "__main__":
    app.run(debug=True)

