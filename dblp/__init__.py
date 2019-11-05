from flask import Flask, render_template, send_from_directory #, escape, request
import os
from . import xmlManager

APP = Flask(__name__)

@APP.route('/')
def dblp():
    #rootel = xmlManager.readXML("dblp.xml")
    print("ciao")
    return render_template("index.html", par="CIAO")

@APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    APP.debug = True
    APP.run()