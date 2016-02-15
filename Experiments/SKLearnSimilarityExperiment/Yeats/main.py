import lxml.html
import requests
import string
import os

def run():
    index = 0
    url = "http://www.csun.edu/~hceng029/yeats/collectedpoems.html"
    req = requests.get(url) # Main directory
    content = lxml.html.fromstring(req.text)
    content.make_links_absolute("http://www.csun.edu/~hceng029/yeats/")
    urls = content.xpath('//a/@href')[:14]
    foldernames = content.xpath('//a/text()')[:14]
    for u,f in zip(urls, foldernames):
        req2 = requests.get(u) # Subdirectory
        os.mkdir(f)
        os.chdir(f)
        content2 = lxml.html.fromstring(req2.text)
        content2.make_links_absolute("http://www.csun.edu/~hceng029/yeats/yeatspoems/")
        poem_names = content2.xpath('//a/text()')
        urls = content2.xpath('//a/@href')
        for j in zip(urls, poem_names):
            print("on poem %d" % index)
            req3 = requests.get(j[0])
            with open("%s.txt" % ''.join([x for x in j[1] if x in string.ascii_letters]), "w") as f:
                f.write(req3.text)
            index += 1
        os.chdir("..")

def main():
    run()

if __name__ == '__main__':
    main()