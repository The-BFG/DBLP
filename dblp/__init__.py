from flask import Flask, render_template, send_from_directory #, escape, request
import os
from . import xmlManager

APP = Flask(__name__)

@APP.route('/')
def dblp():
    element_list = ["article",
                    "author",
                    "book",
                    "cite",
                    "editor",
                    "ee",
                    "incollection",
                    "inproceedings",
                    "mastersthesis",
                    "note",
                    "phdthesis",
                    "proceedings",
                    "www"]
    block_list = xmlManager.readXML("test.xml", element_list)
    return render_template("index.html", block_list=block_list)

@APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    APP.debug = True
    APP.run()