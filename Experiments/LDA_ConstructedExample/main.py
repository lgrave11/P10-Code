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
    return [word for word in document]

def run():
    documents = ["CT scan of the nasal sinuses was performed without a contrast medium. No abnormalities.",
                 "MRI scan of the brain was performed. Abnormalities found: Tumour in the right cerebral hemisphere.",
                 "CAT scan of the abdomen. No abnormalities found.",
                 "An MRI scan of the kidney was performed with a contrast medium. Abnormalities found.",
                 "Patient had broken leg set.",
                 "Patient had broken arm set."
                ]
    DEFAULT_FILTERS = [str.lower, strip_tags, strip_punctuation, strip_multiple_whitespaces,
                   strip_numeric, remove_stopwords, strip_short]
    texts = [preprocess_string(document, filters=DEFAULT_FILTERS)
              for document in documents]
    
    #frequency = defaultdict(int)
    #for text in texts:
    #    for token in text:
    #        frequency[token] += 1
    #
    #texts = [[token for token in text if frequency[token] > 3]
    #          for text in texts]
    dictionary = corpora.Dictionary(texts)
    #dictionary.save('%s.dict' % file) # store the dictionary, for future reference
    corpus = [dictionary.doc2bow(text) for text in texts]
    #tfidf = models.TfidfModel(corpus)
    #tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
    #corpus_tfidf = tfidf[corpus]
    #corpora.MmCorpus.serialize('%s.mm' % file, corpus) # store to disk, for later use
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=2, update_every=1, chunksize=1, passes=1000)
    for i in texts[:10]:
        print(' '.join(i[:10]))
        topics = lda.get_document_topics(dictionary.doc2bow(i))
        for j in topics:
            print("%d,%.2f" % (j[0], j[1]), end="; ")
    lda.print_topics(2)


def main():
    run()

if __name__ == '__main__':
    main()
