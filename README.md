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
    mkdir /var/elasticData
    ```
    ```bash
    sudo docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -v /var/elasticData:/usr/share/elasticsearch/data docker.elastic.co/elasticsearch/elasticsearch:7.4.2

    ```

3. Upgrade `pip`:
    ```bash
    pip3 install --upgrade pip --user
    ```

4. Install python requirements:
    * install `flask`:
        ```bash
        pip3 install flask --user
        ```
    * install `elasticsearch`:
        ```bash
        pip3 install elasticsearch --user
        ```
    * install `xmltodict`:
        ```bash
        pip3 install xmltodict --user
        ```

5. Download the repository from Github:
    ```bash 
    git clone "https://github.com/The-BFG/DBLP.git"
    ```
6. Run application:
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

    * Open a browser and go to: [localhost:5000](http://localhost:5000)
        * If you haven't already uploaded the dblp.xml on elasticsearch click on the "Upload DBLP Data" and then "Upload"


        