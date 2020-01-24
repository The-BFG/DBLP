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
    t_FIELD = r'^((publication|venue|article|incollection|inproceedings|phdthesis|mastersthesis|book)(\.(author|title|year|publisher|journal))?|^(crossref))'
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
                fields = [
                    "article.crossref.#text",
                    "incollection.crossref.#text",
                    "inproceedings.crossref.#text",
                    "phdthesis.crossref.#text",
                    "mastersthesis.crossref.#text",
                    "book.crossref.#text"
                ]
            elif p[1] == "publication":
                fields = [
                    "article.title.#text",
                    "incollection.title.#text",
                    "inproceedings.title.#text",
                    "phdthesis.title.#text",
                    "mastersthesis.title.#text",
                    "article.author.#text",
                    "incollection.author.#text",
                    "inproceedings.author.#text",
                    "phdthesis.author.#text",
                    "mastersthesis.author.#text",
                    "article.year.#text",
                    "incollection.year.#text",
                    "inproceedings.year.#text",
                    "phdthesis.year.#text",
                    "mastersthesis.year.#text"
                ]
            elif p[1] == "publication.title":
                fields = [
                    "article.title.#text",
                    "incollection.title.#text",
                    "inproceedings.title.#text",
                    "phdthesis.title.#text",
                    "mastersthesis.title.#text"
                ]
            elif p[1] == "publication.author":
                fields = [
                    "article.author.#text",
                    "incollection.author.#text",
                    "inproceedings.author.#text",
                    "phdthesis.author.#text",
                    "mastersthesis.author.#text"
                ]
            elif p[1] == "publication.year":
                fields = [
                    "article.year.#text",
                    "incollection.year.#text",
                    "inproceedings.year.#text",
                    "phdthesis.year.#text",
                    "mastersthesis.year.#text"
                ]
            elif p[1] == "venue":
                fields = [
                    "inproceedings.title.#text",
                    "book.title.#text",
                    "inproceedings.publisher.#text",
                    "book.publisher.#text",
                    "article.journal.#text",
                    "incollection.journal.#text",
                    "inproceedings.journal.#text",
                    "phdthesis.journal.#text",
                    "mastersthesis.journal.#text"
                ]
            elif p[1] == "venue.title":
                fields = [
                    "inproceedings.title.#text",
                    "book.title.#text"
                ]
            elif p[1] == "venue.publisher":
                fields = [
                    "inproceedings.publisher.#text",
                    "book.publisher.#text"
                ]
            else:
                fields = [p[1] + ".#text"]

            boost = 4 if rank == "MostSpecific" else 1

        else:
            fields = [
                "article.title.#text",
                "incollection.title.#text",
                "inproceedings.title.#text",
                "phdthesis.title.#text",
                "mastersthesis.title.#text",
                "book.title.#text",
                "article.author.#text",
                "incollection.author.#text",
                "inproceedings.author.#text",
                "phdthesis.author.#text",
                "mastersthesis.author.#text",
                "book.author.#text",
                "article.year.#text",
                "incollection.year.#text",
                "inproceedings.year.#text",
                "phdthesis.year.#text",
                "mastersthesis.year.#text",
                "book.year.#text",
                "article.publisher.#text",
                "incollection.publisher.#text",
                "inproceedings.publisher.#text",
                "phdthesis.publisher.#text",
                "mastersthesis.publisher.#text",
                "book.publisher.#text",
                "article.journal.#text",
                "incollection.journal.#text",
                "inproceedings.journal.#text",
                "phdthesis.journal.#text",
                "mastersthesis.journal.#text",
                "book.journal.#text",
            ]
            boost = 4 if rank == "LessSpecific" else 1
        
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

    # print(query)
    return query
