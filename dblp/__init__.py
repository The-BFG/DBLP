from . import xml_manager, es_API
from flask import Flask, render_template, request, Response, stream_with_context, redirect, url_for, send_from_directory
from threading import Thread
import os

APP = Flask(__name__)
XML_FILE = "dblp.xml"
INDEX_NAME = "dblp"
_ES = es_API.connect_elasticsearch()

@APP.route('/')
@APP.route("/index")
def dblp():
    return render_template("index.html")

@APP.route('/upload', methods=["GET", "POST"])
def upload():
    global XML_FILE, _ES, INDEX_NAME
    mapping = es_API.check_mapping_exist(_ES, INDEX_NAME)
    print(mapping)
    if request.method == "GET":
        return render_template("upload.html", mapping=mapping)

    elif request.method == "POST":
        if not _ES.indices.exists(INDEX_NAME):
            _ES = es_API.create_index(_ES, INDEX_NAME)
        #print(_ES)

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
        xml_manager.readXML(XML_FILE, element_list, _ES, INDEX_NAME)
        # thread = Thread(target=xml_manager.readXML, kwargs={'xml_file': XML_FILE, 'element_list': element_list, '_ES': _ES})
        # thread.start()
        return render_template("upload.html")


@APP.route('/progress')
def progress():
    global XML_FILE
    return Response(stream_with_context(xml_manager.getUploadPercentage(XML_FILE)), mimetype='text/event-stream')

@APP.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(APP.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    APP.run(threaded=True)
