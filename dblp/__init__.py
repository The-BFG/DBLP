from flask import Flask, render_template, send_from_directory #, escape, request
import os
from xmlManager import *

APP = Flask(__name__)

@APP.route('/')
def dblp():
    xmlManager.readXML("")
    return render_template("index.html", par=par)

@APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    APP.debug = True
    APP.run()