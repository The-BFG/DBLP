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

def create_exact_match_query(fields, query, boost):
    if query[0] == '"':
        return {"query_string": {"query" : query , "fields" : fields, "boost": boost * 2}}
    else:
        return {"multi_match": {"query" : query, "fields" : fields, "boost": boost}}
    

def create_query(search_string, rank, page=1):

    alias_by_key = {
        "publication": ["article", "incollection", "phdthesis", "mastersthesis"],
        "venue": ["inproceedings", "book"]
    }

    fields_by_key = {
        "publication": ["author", "title", "year"],
        "venue": ["title", "publisher"]
    }

    all_alias = [elem for (key, value) in alias_by_key.items() for elem in value]
    all_fields = [elem for (key, value) in fields_by_key.items() for elem in value]

    # List of token names.   This is always required
    tokens = (
        'QUOTES',
        'COLON',
        'PHRASE',
        'FIELD',
        'KEYWORD'
    )

    # Regular expression rules for simple tokens
    t_QUOTES = r'\"'
    t_COLON = r':'
    t_PHRASE = r'\"[^\"\n]+\"'
    t_FIELD = r'^((publication|venue|article|incollection|inproceedings|phdthesis|mastersthesis|book)(\.(' + "|".join(all_fields) + '))?|^(crossref))'
    t_KEYWORD = r'[^:\ \"\n]+'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    lexer = lex.lex()

    def p_query(p):
        '''query : expression
                 | query expression'''
        if len(p) > 2:
            p[0] = p[1] + [p[2]]
            # print("P0", p[0], "P1", p[1], "P2", p[2])
        else:
            p[0] = [p[1]]

    def p_expression(p):
        '''expression : FIELD COLON value
                      | value'''
        
        if len(p) > 2:
            if p[1] == "crossref":
                fields = [alias + ".crossref.#text" for alias in all_alias]
            elif p[1] == "publication":
                fields = ["{}.{}.#text".format(a, f) for a in alias_by_key["publication"] for f in fields_by_key["publication"] ]
            elif p[1] == "publication.title":
                fields = ["{}.{}.#text".format(a, "title") for a in alias_by_key["publication"]]
            elif p[1] == "publication.author":
                fields = ["{}.{}.#text".format(a, "author") for a in alias_by_key["publication"]]
            elif p[1] == "publication.year":
                fields = ["{}.{}.#text".format(a, "year") for a in alias_by_key["publication"]]
            elif p[1] == "venue":
                fields = ["{}.{}.#text".format(a, f) for a in alias_by_key["venue"] for f in fields_by_key["venue"] ]
            elif p[1] == "venue.title":
                fields = ["{}.{}.#text".format(a, "title") for a in alias_by_key["venue"]]
            elif p[1] == "venue.publisher":
                fields = ["{}.{}.#text".format(a, "publisher") for a in alias_by_key["venue"]]
            else:
                fields = [p[1] + ".#text"]

            boost = 4 if rank == "MostSpecific" else 1

        else:
            fields = ["{}.{}.#text".format(a, f) for a in alias_by_key["publication"] for f in fields_by_key["publication"]]
            fields = fields + ["{}.{}.#text".format(a, f) for a in alias_by_key["venue"] for f in fields_by_key["venue"]]

            boost = 4 if rank == "LessSpecific" else 1

        print("FIELDS: ", fields)
        
        p[0] = create_exact_match_query(fields=fields, query=p[3] if len(p) > 2 else p[1], boost=boost)

    def p_value(p):
        '''value : PHRASE
                 | KEYWORD'''
        p[0] = p[1]

    def p_phrase(p):
        '''phrase : KEYWORD
                  | KEYWORD KEYWORD'''
        p[0] = p[1] + p[2] if p[2] else ""

    # Error rule for syntax errors
    def p_error(p):
        print("Syntax error in input!")

    parser = yacc.yacc(debug=True)
    parsed = parser.parse(search_string, lexer=lexer, debug=True)
    #print(parsed)
    
    query = {
        "query": {
            "dis_max": {
                "queries": parsed
            }
        },
        "from": (page-1)*100,
        "size":100
    }

    print(query)
    return query
