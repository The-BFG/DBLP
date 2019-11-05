# GAVI - Gestione Avanzata dell'Informazione
University project for Full Text Search using docker and elastic search.

## Installing

### Prerequisite:

1. Install Docker for Ubuntu: [Docker Documentation](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

2. Install [Elasticsearch for Docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)  ( version 7.4.2 ):
    ```bash
    docker pull docker.elastic.co/elasticsearch/elasticsearch:7.4.2
    ```
    ```bash
    docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co elasticsearch/elasticsearch:7.4.2
    ```
3. Install Flask:
    * upgrade `pip`
        ```bash
        pip3 install --upgrade pip --user
        ```
    * and install `flask`
        ```bash
        pip3 install flask --user
        ```
    * or upgrade it if already installed
        ```bash
        pip3 install --upgrade flask --user
        ```

4. Download the repository from Github:
    ```bash 
    git clone "https://github.com/The-BFG/GAVI.git
    ```
5. Run application:
    * Enter in the project directory:
        ```bash
        cd DBLP
        ```
    * Create environment variable
        ```bash
        export FLASK_APP=dblp.py
        ```
        for debug mode:
        ```bash
        export FLASK_ENV=development
        ```
    * Install application:
        ```bash
        pip3 install -e . --user
        ```
    * run application with:
        ```bash
        flask run
        ```
        if debug mode is active use:
        ```bash
        flask run --no-reload    
        ```
        due to a bug in the Flask-SocketIO package which replaces the flask run command.


dblp:
1. article:
    * Attributes:
        * mdate
        * key
        * publtype
    * Subelements:
        * author
        * title
        * journal
        * volume
        * month (opzionale)
        * year
        * ee (opzionale)
        * url (opzionale)
        * cdrom
        * publisher
        * note (opzionale)
2. book
    * Attributes:
        * mdate
        * key
    * Subelements:
        * title
        * publisher
        * year
        * ee
        * isbn
3. proceedings
    * Attributes:
        * mdate
        * key
        * publtype
    * Subelements:
        * editor
        * title
        * booktitle
        * series
        * volumes
        * year
        * url/procee
4. inproceedings 
    * Attributes:
        * mdate
        * key
    * Subelements:
        * author
        * title
        * booktitle
        * year
        * url
        * crossref
        * ee
5. www:
    * Attributes:
        * mdate 
        * key
    * Subelements:
        * author
        * title
        * year
        * ee
6. <mastersthesis mdate="2018-06-13" key="ms/Vollmer2006">
<author>Stephan Vollmer</author>
<title>Portierung des DBLP-Systems auf ein relationales Datenbanksystem und Evaluation der Performance.</title>
<year>2006</year>
<school>Diplomarbeit, Universit&auml;t Trier, FB IV, Informatik</school>
<ee>http://dbis.uni-trier.de/Diplomanden/Vollmer/vollmer.shtml</ee>
</mastersthesis>

