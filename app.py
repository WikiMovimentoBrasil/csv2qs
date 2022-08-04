import os
import yaml
from csv2qs import csv2qs_builder
import pandas as pd
from flask import Flask, render_template, request, session, redirect
from flask_babel import Babel, gettext

__dir__ = os.path.dirname(__file__)
app = Flask(__name__)
app.config.update(yaml.safe_load(open(os.path.join(__dir__, "config.yaml"))))

BABEL = Babel(app)


##############################################################
# LOCALIZATION
##############################################################
@BABEL.localeselector
def get_locale():
    """
    Function to get the preferred language of the user
    :return: language code
    """
    if request.args.get("lang"):
        session["lang"] = request.args.get("lang")
    return session.get("lang", "pt")


@app.route("/set_locale")
def set_locale():
    """
    Function to change the language of the app
    :return: redirect to the page the user was
    """
    next_page = request.args.get("return_to")
    lang = request.args.get("lang")

    session["lang"] = lang
    redirected = redirect(next_page)
    return redirected


def pt_to_ptbr(lang):
    """
    Function to change pt to pt-br for convenience
    :param lang: language code of the user
    :return: language code
    """
    if lang == "pt" or lang == "pt-br":
        return "pt-br"
    else:
        return lang


##############################################################
# PAGES
##############################################################
@app.route("/", methods=["GET", "POST"])
def home():
    """
    Function to show the home page, that the user sends the files
    :return: redirect the user to QuickStatements when POST,
    and show the form page when GET
    """
    lang = get_locale()
    if request.method == "POST":
        file_uploaded = request.files.get("file_uploaded")
        dataframe = pd.read_csv(file_uploaded)
        qs_to_return = qs(dataframe)
        return redirect(qs_to_return)
    else:
        return render_template("home.html",
                               lang=lang)


@app.route("/about", methods=["GET"])
def about():
    """
    Page of description of the app
    :return: Page of description of the app
    """
    lang = get_locale()
    return render_template("about.html",
                           lang=lang)


def qs(dataframe):
    """
    Runs the script to translate the csv to QuickStatements syntax
    :param dataframe: CSV file uploaded by the user
    :return: URL of the QuickStatements commands ready to upload
    """
    qs_to_return = csv2qs_builder(dataframe)
    return qs_to_return


if __name__ == "__main__":
    app.run(debug=True)
