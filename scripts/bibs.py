import json


def auths(alist):
    if len(alist) == 1:
        return alist[0]
    else:
        return u", ".join(alist[:-1]) + u" and " + alist[-1]


def enc(x):
    return x.encode('utf-8').strip()


def make_index(data):
    # print data
    papers = {}
    index = {}

    def idx_add(x, pID):
        index[x] = index.get(x, []) + [pID]

    sorted_data = sorted(data.iteritems(),
                         key=lambda x: x[1][u"year"][0],
                         reverse=True)

    template = """<p class=\"paper\">%s
 <small><a href=\"http://dblp.uni-trier.de/rec/bibtex/%s\">bibtex</a>
</small></p>"""

    for pID, rec in sorted_data:
        # print rec
        try:
            title = enc(rec[u"title"][0])
            s = "<strong class=\"ptitle\">%s</strong><br/>" % title
            if u"author" in rec:
                s += "%s. " % enc(auths(rec[u"author"]))
                for a in rec[u"author"]:
                    idx_add(enc(a), pID)
            else:
                s += "%s (Ed.). " % enc(auths(rec[u"editor"]))
                for a in rec[u"editor"]:
                    idx_add(enc(a), pID)
            year = enc(rec[u"year"][0])
            if u"booktitle" in rec:
                booktitle = enc(rec[u"booktitle"][0])
                s += "%s, %s." % (booktitle, year)
                idx_add(booktitle, pID)
            else:
                journal = enc(rec[u"journal"][0])
                s += "%s, %s." % (journal, year)
                idx_add(journal, pID)
            papers[pID] = template % (s, enc(pID))

        except:
            print "Problem with entry:", rec

    return json.dumps({"papers": papers, "index": index})

if __name__ == "__main__":
    data = json.load(file("../data/data.json"))
    jsonindex = make_index(data)
    file("../data/index.json", "w").write(jsonindex)
