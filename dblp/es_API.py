from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print(' * Connected to ElasticSearch!')
    else:
        print(' * Could not connect to Elasticsearch!')
    return _es

def create_index(_es, index_name='new_index', mapping='None'):
    created = False
    try:
        if not _es.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            print('Creating Index...', index_name)
            print(_es.indices.create(index=index_name, body=mapping))
            print("Index created.")
            created = True
        else:
            print("Index already exists.")
    except Exception as ex:
        print(str(ex))        
    return _es, created

def get_mapping(_es, index_name='new_index'):
    mapping = False
    try:
        mapping = IndicesClient.get_mapping(index_name)
    except Exception as e:
        print(e)
    return mapping
