from . import xml_manager, es_API
from flask import Flask, render_template, request, Response, stream_with_context, redirect, url_for, send_from_directory
from threading import Thread
import os

APP = Flask(__name__)
XML_FILE = "dblp.xml"
INDEX_NAME = "dblp"
_ES = es_API.connect_elasticsearch()

@APP.route('/', methods=["GET", "POST"])
@APP.route("/index", methods=["GET", "POST"])
def dblp():
    global _ES, INDEX_NAME
    uploaded = _ES.indices.exists(INDEX_NAME)
    if request.method == "GET":
        return render_template("index.html", page=0, uploaded=uploaded)

    if request.method == "POST":
        search_string = request.form["query"]
        rank = request.form["rank"]
        page = int(request.form["page"])
        query = es_API.create_query(search_string, rank, page)
        data = _ES.search(index=INDEX_NAME, body=query)
        #print(data)
        return render_template("index.html", data=data, search_string=search_string, rank=rank, page=page, uploaded=uploaded)


@APP.route("/index/<query>/<rank>/<int:page>", methods=["GET"])
def change_page(query, rank, page):
    global _ES, INDEX_NAME
    uploaded = _ES.indices.exists(INDEX_NAME)
    if request.method == "GET":
        search_string = query
        rank = rank
        page = page
        query = es_API.create_query(search_string, rank, page)
        data = _ES.search(index=INDEX_NAME, body=query)
        return render_template("index.html", data=data, search_string=search_string, rank=rank, page=page, uploaded=uploaded)
    else:
        return render_template("index.html", page=0)


@APP.route('/upload', methods=["GET", "POST"])
def upload():
    global XML_FILE, _ES, INDEX_NAME
    uploaded = _ES.indices.exists(INDEX_NAME)
    if request.method == "GET":
        return render_template("upload.html", uploaded=uploaded)
    elif request.method == "POST":
        if not uploaded:
            with open("mapping.json", 'r') as f:
                mapping = f.read()
            #print(mapping)
            _ES, created = es_API.create_index(_ES, index_name=INDEX_NAME, mapping=mapping)
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
