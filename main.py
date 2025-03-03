import os
import json
from flask import Flask, render_template

# apa

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
@app.route("/download/<file>")
def download(file):
    try:
        download_data = downloads[file]
        return render_template("/download.html", data=download_data)

    except KeyError:
        return render_template(
            "/download.html",
            data={
                "name": f"404 Invalid address '{file}'",
                "error": True
            })


# Katter

@app.route("/sigge")
def katt_sigge():
    return render_template(r"katter/sigge.html")

@app.route("/bonzo")
def katt_bonzo():
    return render_template(r"katter/bonzo.html")



if __name__ == "__main__":
    app.run(debug=True)

