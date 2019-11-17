from . import xml_manager, es_API
from flask import Flask, render_template, request, Response, stream_with_context, redirect, url_for, send_from_directory
from threading import Thread
import os

APP = Flask(__name__)
XML_FILE = "test.xml"

@APP.route('/')
@APP.route("/index")
def dblp():
    return render_template("index.html")

@APP.route('/upload', methods=["GET", "POST"])
def upload():
    global XML_FILE

    if request.method == "GET":
        return render_template("upload.html")

    elif request.method == "POST":
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
        #Response(xml_manager.getUploadPercentage(XML_FILE), mimetype='text/event-stream')
        xml_manager.readXML(XML_FILE, element_list, _es)
        thread = Thread(target=xml_manager.readXML, kwargs={'xml_file': XML_FILE, 'element_list': element_list, '_es': _es})
        thread.start()
        return redirect("index")


@APP.route('/progress')
def progress():
    global XML_FILE
    return Response(stream_with_context(xml_manager.getUploadPercentage(XML_FILE)), mimetype='text/event-stream')

@APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    APP.run(threaded=True)
