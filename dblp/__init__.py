from . import xml_manager, es_API
from flask import Flask, render_template, Response, send_from_directory #, escape, request
import os, time

APP = Flask(__name__)

@APP.route('/')
def dblp():
    pass

@APP.route('/upload')
def upload():
    _es = es_API.connect_elasticsearch()
    index_name = "dblp"
    if not _es.indices.exists(index_name):
        _es = es_API.create_index(_es, index_name)

    print(_es)
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
    block_list = xml_manager.readXML("test.xml", element_list, _es)
    return render_template("upload.html", block_list=block_list)


@APP.route('/progress')
def progress():
    def generate():
        x = 0

        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')

@APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    APP.run()
