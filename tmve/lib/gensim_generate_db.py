import sys
import numpy 
import math
import sqlite3
from stemming.porter2 import stem
from pprint import pprint   # pretty-printer
from lxml import etree
from collections import defaultdict
from gensim import corpora, models, similarities
from gensim.parsing.preprocessing import *
from gensim.utils import lemmatize
from gensim.models.ldamodel import LdaModel

### score functions ###

def get_doc_score(doca, docb):
    score = 0
    total = 0
    print("doca")
    print(len(doca))
    print("docb")
    print(len(docb))
    for topic_id in range(len(doca)):
        thetaa = doca[topic_id][1]
        thetab = docb[topic_id][1]
        if not ((thetaa != 0.0 and thetab == 0.0) or (thetaa == 0.0 and thetab != 0.0)):
            score += math.pow(thetaa - thetab, 2)
    return 0.5 * score

def get_topic_score(topica, topicb):
    score = 0
    
    total = math.pow(abs(math.sqrt(100) - math.sqrt(0)), 2) * len(topica)
    for term_id in range(len(topica)):
        thetaa = abs(topica[term_id][1])
        thetab = abs(topicb[term_id][1])
        score += math.pow(abs(math.sqrt(thetaa) - math.sqrt(thetab)), 2)
    return 0.5 * score / total

def get_term_score(terma, termb):
    score = 0
    for term_id in range(len(terma)):
        score += math.pow(terma[term_id] - termb[term_id], 2)
    return score


### write relations to db functions ###

def write_doc_doc(con, cur, corpus, topic_count):
    cur.execute('DROP TABLE IF EXISTS doc_doc')
    cur.execute('CREATE TABLE doc_doc (id INTEGER PRIMARY KEY, doc_a INTEGER, doc_b INTEGER, score FLOAT)')
    cur.execute('CREATE INDEX doc_doc_idx1 ON doc_doc(doc_a)')
    cur.execute('CREATE INDEX doc_doc_idx2 ON doc_doc(doc_b)')
    con.commit()
    
    for a in range(len(corpus)):
        if a % 1000 == 0:
            print("doc " + str(a))
        doc_by_doc = {}
        for b in range(a, len(corpus)):
            score = get_doc_score(lda.get_document_topics(corpus[a], 0), lda.get_document_topics(corpus[b],0))
            if score == 0:
                continue
            elif len(doc_by_doc) < 100:
                doc_by_doc[score] = (a, b)
            else:
                max_score = max(doc_by_doc.keys())
                if max_score > score:
                    del doc_by_doc[max_score]
                    doc_by_doc[score] = (a, b)
        
        for doc in doc_by_doc:
            execution_string = 'INSERT INTO doc_doc (id, doc_a, doc_b, score) VALUES(NULL, ?, ?, ?)'
            cur.execute(execution_string, [str(doc_by_doc[doc][0]), str(doc_by_doc[doc][1]), str(doc)])

    con.commit()

def write_doc_topic(con, cur, lda, corpus):
    cur.execute('DROP TABLE IF EXISTS doc_topic')
    cur.execute('CREATE TABLE doc_topic (id INTEGER PRIMARY KEY, doc INTEGER, topic INTEGER, score FLOAT)')
    cur.execute('CREATE INDEX doc_topic_idx1 ON doc_topic(doc)')
    cur.execute('CREATE INDEX doc_topic_idx2 ON doc_topic(topic)')
    con.commit()

    document_id=0;
    for i in corpus:
        topics = lda.get_document_topics(i);
        for topic in topics:
            cur.execute('INSERT INTO doc_topic (id, doc, topic, score) VALUES(NULL, ?, ?, ?)', [document_id, topic[0], topic[1]])
        document_id = document_id+1

    con.commit()
        

def write_topics(con, cur, lda, topic_count, dictionary):
    cur.execute('DROP TABLE IF EXISTS topics')
    cur.execute('CREATE TABLE topics (id INTEGER PRIMARY KEY, title VARCHAR(100))')
    con.commit()
    
    for i in range(topic_count):
        topic = lda.get_topic_terms(i,3)
        cur.execute('INSERT INTO topics (id, title) VALUES(NULL, ?)', ["{" + dictionary[topic[0][0]] + ', ' + dictionary[topic[1][0]] + ', ' + dictionary[topic[2][0]] + '}'])
    
    con.commit()

    
def write_topic_term(con, cur, lda, topic_count, dictionary):
    cur.execute('DROP TABLE IF EXISTS topic_term ')
    cur.execute('CREATE TABLE topic_term (id INTEGER PRIMARY KEY, topic INTEGER, term INTEGER, score FLOAT)')
    cur.execute('CREATE INDEX topic_term_idx1 ON topic_term(topic)')
    cur.execute('CREATE INDEX topic_term_idx2 ON topic_term(term)')
    con.commit()
            
        
    for i in range(topic_count):
        topic = lda.get_topic_terms(i,len(dictionary.iteritems()))
        for term in range(len(topic)):
            cur.execute('INSERT INTO topic_term (id, topic, term, score) VALUES(NULL, ?, ?, ?)', [i, numpy.asscalar(topic[term][0]), topic[term][1]])

    con.commit()


def write_topic_topic(con, cur, lda, topic_count):
    cur.execute('DROP TABLE IF EXISTS topic_topic')
    cur.execute('CREATE TABLE topic_topic (id INTEGER PRIMARY KEY, topic_a INTEGER, topic_b INTEGER, score FLOAT)')
    cur.execute('CREATE INDEX topic_topic_idx1 ON topic_topic(topic_a)')
    cur.execute('CREATE INDEX topic_topic_idx2 ON topic_topic(topic_b)')
    con.commit()
    
    topica_count = 0
    topic_by_topic = []
    for topica in range(topic_count):
        topicb_count = 0
        for topicb in range(topic_count):
            if topic_by_topic.count((topicb_count, topica_count)) != 0:
                topicb_count +=1
                continue
            score = get_topic_score(lda.get_topic_terms(topica, topic_count), lda.get_topic_terms(topicb, topic_count))
            cur.execute('INSERT INTO topic_topic (id, topic_a, topic_b, score) VALUES(NULL, ?, ?, ?)', [topica_count, topicb_count, score])
            
            topic_by_topic.append((topica_count, topicb_count))
            topicb_count = topicb_count + 1
        topica_count = topica_count + 1

    con.commit()

def write_term_term(con, cur, lda, topic_count, dictionary):
    v = {}
    cur.execute('DROP TABLE IF EXISTS IF EXISTS term_term ')
    cur.execute('CREATE TABLE term_term (id INTEGER PRIMARY KEY, term_a INTEGER, term_b INTEGER, score FLOAT)')
    cur.execute('CREATE INDEX term_term_idx1 ON term_term(term_a)')
    cur.execute('CREATE INDEX term_term_idx2 ON term_term(term_b)')
    con.commit()
    
    for i in range(len(dictionary.iteritems())):
        v[i] = []

    for t in range(topic_count):
        topic = lda.get_topic_terms(t,len(dictionary.iteritems()))
        for i in range(len(dictionary.iteritems())):
            v[i].append(math.sqrt(math.exp(topic[i][1])))
    
    for terma in range(len(dictionary.iteritems())):
        if terma % 1000 == 0:
            print("term " + str(terma))
        term_by_term = {}
        for termb in range(terma, len(dictionary.iteritems())):
            score = get_term_score(v[terma], v[termb])
            if score == 0:
                continue
            elif len(term_by_term) < 100:
                term_by_term[score] = (terma, termb)
            else:
                max_score = max(term_by_term.keys())
                if max_score > score:
                    del term_by_term[max_score]
                    term_by_term[score] = (terma, termb)
        
        for term in term_by_term:
            execution_string = 'INSERT INTO term_term (id, term_a, term_b, score) VALUES(NULL, ?, ?, ?)'
            cur.execute(execution_string, [term_by_term[term][0], term_by_term[term][1], term])

    con.commit()
    
def write_doc_term(con, cur, corpus):
    cur.execute('DROP TABLE IF EXISTS IF EXISTS doc_term')
    cur.execute('CREATE TABLE doc_term (id INTEGER PRIMARY KEY, doc INTEGER, term INTEGER, score FLOAT)')
    cur.execute('CREATE INDEX doc_term_idx1 ON doc_term(doc)')
    cur.execute('CREATE INDEX doc_term_idx2 ON doc_term(term)')
    con.commit()
        
    for document_id in range(len(corpus)):
        for term in corpus[document_id]:
            cur.execute('INSERT INTO doc_term (id, doc, term, score) VALUES(NULL, ?, ?, ?)', [document_id, term[0], term[1]])
    
    con.commit()

def write_terms(con, cur, dictionary):
    cur.execute('DROP TABLE IF EXISTS terms')
    con.commit()
    cur.execute('CREATE TABLE terms (id INTEGER PRIMARY KEY, title VARCHAR(100))')
    con.commit()

    for term in dictionary.iteritems():
        cur.execute('INSERT INTO terms (id, title) VALUES(NULL, ?)', [term[1]])

    con.commit()

def write_docs(con, cur, documents):
    cur.execute('DROP TABLE IF EXISTS docs')
    con.commit()
    cur.execute('CREATE TABLE docs (id INTEGER PRIMARY KEY, title VARCHAR(100))')
    con.commit()

    for doc in documents:
        cur.execute('INSERT INTO docs (id, title) VALUES(NULL, ?)', [doc])

    con.commit()

def tokenize(document):
    return [word for word in document if word not in set(["says", "said"])]
    
def create_dictionary():
    file = "ap.txt"
    read_file = open(file, "r", encoding="utf-8").read()
    documents = read_file.split("\n\n\n")
    documents2 = []
    for i in documents:
        try:
            xml = etree.fromstring(i)
            documents2.append(xml)
        except(Exception):
            continue
    documents = [x.xpath('//TEXT/text()')[0].strip() for x in documents2]
    texts = [tokenize(document)
              for document in preprocess_documents(documents)]
    
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 3]
              for text in texts]
    
    dictionary = corpora.Dictionary(texts)
    
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    return (documents, dictionary, corpus)

### main ###

if (__name__ == '__main__'):
    # if (len(sys.argv) != 7):
    #    print('usage: python generate_csvs.py <db-filename> <doc-wordcount-file> <beta-file> <gamma-file> <vocab-file> <doc-file>\n')
    #    sys.exit(1)
    topics_count = 20
    #lda = sys.argv[1]
    # filename = sys.argv[1]
    # doc_wordcount_file = sys.argv[2]
    # beta_file = sys.argv[3]
    # gamma_file = sys.argv[4]
    # vocab_file = sys.argv[5]
    # doc_file = sys.argv[6]

    dictionary = corpora.dictionary.Dictionary();
    documents, dictionary, corpus = create_dictionary();
    #dictionary.save('dict')
    #dictionary.load('dict')
    lda = LdaModel.load(sys.argv[1])
    lda.id2word = dictionary
    
    # connect to database, which is presumed to not already exist
    con = sqlite3.connect('test_db')
    cur = con.cursor()


    # write the relevant rlations to the database, see individual functions for details
    print("writing terms to db...")
    write_terms(con, cur, dictionary)
    
    print("writing docs to db...")
    write_docs(con, cur, documents)
    
        
    print("writing doc_topic to db...")
    write_doc_topic(con, cur, lda, corpus)

    print("writing topics to db...")
    write_topics(con, cur, lda, topics_count, dictionary)
    
    print("writing topic_term to db...")
    write_topic_term(con, cur, lda, topics_count, dictionary)
    
    print("writing doc_term to db...")
    write_doc_term(con, cur, corpus)    
    
    print("writing term_term to db...")
    # write_term_term(con, cur, lda, topics_count, dictionary)

    print("writing topic_topic to db...")
    write_topic_topic(con, cur, lda, topics_count)
            
    print("writing doc_doc to db...")
    write_doc_doc(con, cur, corpus, topics_count)