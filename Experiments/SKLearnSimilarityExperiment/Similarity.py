import os
import fnmatch
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from lxml import etree

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def run():
    #files = list(find_files('Yeats', '*.txt'))
    #documents = [open(f).read() for f in files]
    file = "ap.txt"
    read_file = open(file, "r", encoding="utf-8").read()
    documents = read_file.split("\n\n\n")
    documents2 = []
    for i in documents:
        try:
            xml = etree.fromstring(i)
            documents2.append(xml)
        except Exception as e:
            continue
    documents = [x.xpath('//TEXT/text()')[0].strip() for x in documents2]

    tfidf = TfidfVectorizer().fit_transform(documents)
    pairwise_similarity = tfidf * tfidf.T
    reduced_data = PCA(n_components=2).fit_transform(pairwise_similarity.toarray())
    kmeans = KMeans(init='k-means++', n_clusters=3, n_init=10)
    kmeans.fit(reduced_data)

    h = .02
    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
    y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1)
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')

    plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=169, linewidths=3,
                color='w', zorder=10)
    plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
              'Centroids are marked with white cross')
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.show()
    
    #doc_to_index = dict()
    #index_to_doc = dict()
    #for i,d in enumerate(files):
    #    doc_to_index[d] = i
    #    index_to_doc[i] = d
    #sims = []
    #for i in pairwise_similarity[doc_to_index[files[2]]].A:
    #    for doc_id, similarity in enumerate(i):
    #        sims.append((doc_id, similarity))
    #sims = sorted(sims, key=lambda x: x[1], reverse=True)
    #for i in sims[:10]:
    #    print(index_to_doc[i[0]], i[1])


def main():
    run()

if __name__ == '__main__':
    main()