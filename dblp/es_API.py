from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from . import lex
from . import yacc


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

def create_query(search_string, rank):
    # List of token names.   This is always required
    tokens = (
        'COLON',
        'KEYWORD',
        'FIELD',
        'PHRASE',
    )

    # Regular expression rules for simple tokens
    t_COLON = r':'
    t_KEYWORD = r'[^:\ \"\n]+'
    t_FIELD = r'^((publication|article|incollection|inproc|phThesis|masterThesis)(\.(author|title|year))?|^(crossref)|^(inproceedings|book|journal)(\.(title|publisher))?)'
    t_PHRASE = r'^[^\"\n]+$'
    
    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()
    print(lexer)

    def p_query(p):
        '''query : expression
                 | query expression'''
        if len(p)>2:
            print("testttquery",p[1],p[2])
            p[0] = p[1] + [p[2]]
        else:
            print("testtt111query",p[1])
            p[0] = [p[1]]

    def p_expression(p):
        '''expression : FIELD COLON value
                      | value'''
        if len(p)>2:
            if p[1] == "crossref":
                fields = [
                    "publication.crossref.#text",
                    "article.crossref.#text" #aggiungere tutti elementi con crossref
                ]
                p[0] = {"multi_match": {"query" : p[1], "fields" : fields}}
            else :
                key = p[1] + ".#text"
                p[0] = {"match": {key : {"query" : p[3], "boost" : 2}}}
        else:
            fields = [
                "publication.title.#text",
                "article.title.#text" #aggiungere tutti i campi dei field
            ]
            p[0] = {"multi_match": {"query" : p[1], "fields" : fields}}

    def p_value(p):
        '''value : KEYWORD
                 | '"' PHRASE '"' '''
        p[0] = p[2] if p[1] == '"' else p[1]

    # Error rule for syntax errors
    def p_error(p):
        print("Syntax error in input!")

    parser = yacc.yacc(debug=True)
    parsed = parser.parse(search_string, lexer=lexer, debug=True)
    print(parsed)

    query = {
            "query": {
                "dis_max": {
                    "queries": parsed
                }
            },
            "size":100
        }
    print(query)
    # query = {
    #         "query": {
    #             "bool": {
    #                 "must": [
    #                     {
    #                         "match": {
    #                             "article.title.#text": search_string
    #                         }
    #                     }
    #                 ]
    #             }
    #         }
    #     }
    return query
