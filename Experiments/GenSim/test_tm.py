from gensim import corpora, models, similarities
from gensim.parsing.preprocessing import *
from gensim.utils import lemmatize
from collections import defaultdict
from pprint import pprint   # pretty-printer
from lxml import etree
import sys
import logging
import string
from stemming.porter2 import stem

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO  # ipython sometimes messes up the logging setup; restore

def tokenize(document):
    return [word for word in document if word not in set(["says", "said"])]

def run():
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
    #dictionary.save('%s.dict' % file) # store the dictionary, for future reference
    corpus = [dictionary.doc2bow(text) for text in texts]
    #tfidf = models.TfidfModel(corpus)
    #tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    #corpus_tfidf = tfidf[corpus]
    #corpora.MmCorpus.serialize('%s.mm' % file, corpus) # store to disk, for later use
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=20, update_every=1, chunksize=10, passes=5)
    for i in texts[:10]:
        print(' '.join(i[:10]))
        print(lda.get_document_topics(dictionary.doc2bow(i)))
    #for i in lda.print_topics(20):
    #    print(i)


def main():
    run()

if __name__ == '__main__':
    main()
