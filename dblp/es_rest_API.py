from datetime import datetime
from elasticsearch import Elasticsearch

_es = Elasticsearch()

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Connected to ElasticSearch!')
    else:
        print('Could not connect to Elasticsearch!')
    return _es

def create_index(es_object, settings, index_name='dblp' ):
    created = False
    try:
        if not es_object.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_object.indices.create(index=index_name, ignore=400, body=settings)
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        print("bhoch")


if __name__ == '__main__':
    pass    
