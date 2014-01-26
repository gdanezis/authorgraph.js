import requests
from xml.etree import ElementTree
from collections import Counter
import json

from bibs import make_index
import sys


if len(sys.argv) > 1:
    print "DBLP URLs from %s" % sys.argv[1]
    urls = file(sys.argv[1]).read()
else:
    print "DBLP URLs from ../data/urls.txt"
    urls = file("../data/urls.txt").read()

urls = urls.strip().split("\n")

Core = set()
Secondary = []
Venues = []
SecondaryV = []


pairs = []
records = {}
trans = {}


def ff(x):
    if x in trans:
        return trans[x]
    return x

for url in urls:
    print "Fetching %s ..." % url
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)

    targets = [x.text for x in tree.find("person").findall("author")]
    for t in targets:
        trans[t] = targets[-1]
    targetset = set(targets)
    Core.add(targets[-1])

    for pub in tree:
            if pub.tag == "r":
                record = {}
                record["type"] = pub[0].tag

                publtype = pub[0].attrib.get("publtype", None)
                if publtype == "informal publication":
                    continue

                records[pub[0].attrib["key"]] = record
                for content in pub[0]:
                    prev = record.get(content.tag, [])
                    record[content.tag] = prev + [content.text]

                    if content.tag == "author":
                        if content.text not in targetset:
                            Secondary += [ff(content.text)]
                            pairs += [(ff(targets[-1]), ff(content.text))]

                    if content.tag == "booktitle":
                        Venues += [(ff(targets[-1]), content.text)]
                        SecondaryV += [content.text]
                    if content.tag == "journal":
                        Venues += [(ff(targets[-1]), content.text)]
                        SecondaryV += [content.text]

                for a in record.get("author", []):
                    for b in record["author"]:
                        if a in targetset or b in targetset:
                            continue
                        if a >= b:
                            continue
                        pairs += [(a, b)]


seclist = Counter(Secondary)
links = Counter(pairs)

authorList = []
for c in Core:
    authorList += [{"name": c, "group": 1}]
for c in seclist:
    if c not in Core:
        if seclist[c] > 1:
            authorList += [{"name": c, "group": 2}]
        #else:
        #    authorList += [{"name": c, "group": 3}]

idx = [d["name"] for d in authorList]

linkList = []
for (a, b) in pairs:
    try:
        linkList += [{"source": idx.index(a),
                      "target": idx.index(b),
                      "value": links[(a, b)]}]
    except:
        pass

authorL2 = authorList
#for c in Core:
#    authorL2 += [{"name": c, "group": 1}]


vs = Counter([v for _, v in Venues])
SecondaryV = Counter([v for _, v in Counter(Venues)])

for v in vs:
    if (v in SecondaryV and SecondaryV[v] > 1):
        authorL2 += [{"name": v, "group": 5}]
        continue
    if vs[v] > 0:
        authorL2 += [{"name": v, "group": 4}]
    # elif:
    #    authorL2 += [{"name": v, "group": 5}]

Venues = Counter(Venues)
idx = [d["name"] for d in authorL2]
# linkList = []
for (a, b) in Venues:
    try:
        linkList += [{"source": idx.index(a),
                      "target": idx.index(b),
                      "value": Venues[(a, b)]}]
    except:
        pass

data = {"nodes": authorL2, "links": linkList}
index = make_index(records)
file("../data/graph.json", "w").write(json.dumps(data))
file("../data/data.json", "w").write(json.dumps(records))
file("../data/index.json", "w").write(index)


