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

def create_index(_es, index_name='new_index', settings='{"dynamic": true}'):
    created = False
    try:
        if not _es.indices.exists(index_name):
            # Ignore 400 means to ignore "Index Already Exist" error.
            _es.indices.create(index=index_name, ignore=400)#
            print('Creating Index...')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        print("Index created.")
    return _es, created


if __name__ == '__main__':
    pass    
