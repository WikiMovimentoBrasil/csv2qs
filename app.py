import os
import csv_for_qs
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)
__dir__ = os.path.dirname(__file__)


@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/arquivo", methods=["GET", "POST"])
def post_arquivo():
    if request.method == "POST":
        arquivo = request.files.get("meuArquivo")
        dataframe = pd.read_csv(arquivo)
        return qs(dataframe)
    else:
        return render_template("arquivo.html")


@app.route("/qs")
def qs(dataframe):
    QS = csv_for_qs.main(dataframe)
    return render_template("qs.html", QS=QS)


if __name__ == "__main__":
    app.run(debug=True)
