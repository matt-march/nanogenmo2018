import sys
import argparse

import json
import nltk
import os.path as path

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url")
parser.add_argument("-t", "--title")
parser.add_argument("--tags")

def main(**argv):

##    print(argv)

    title = "Frankenstein"
    tags = ["science fiction", "horror", "1800s", "english", "gothic", "fiction", "prose"]

    if (argv["title"] is not None):
        title = argv["title"]

    if (argv["tags"] is not None):
        tags = []
        for t in argv["tags"].split(';'):
            tags.append(t)

    try:
        f = open(path.join("Input", title + ".txt"), "r", encoding='utf-8-sig')
        lines = f.read().strip()
    except:
        f = open(path.join("Input", title + ".txt"), "r")
        lines = f.read().strip()

    # remove unwanted words/characters
    removeTokenList = ['’', '`', '”', '“', '_', "''", '(', ')', '[', ']', '``']

    beforeLength = len(lines)
    for s in removeTokenList:
        lines = lines.replace(s, '')

    afterLength = len(lines)

    print("before: " + str(beforeLength))
    print("after: " + str(afterLength))

    tokens = nltk.word_tokenize(lines)
    print("first tokens length: " + str(len(tokens)))

    tokens = list(filter(lambda x: x not in removeTokenList, tokens))
    print("second tokens length: " + str(len(tokens)))

    edges = {"(start)": {tokens[0]: 1}}
    reverseEdges = {"(end)": {tokens[-1]: 1}}

    def addEdge(word, next, collection):
        if word not in collection:
            collection[word] = {}
        
        if next not in collection[word]:
            collection[word][next] = 0

        collection[word][next] += 1

    for i in range(0, len(tokens) - 1):
        addEdge(tokens[i], tokens[i+1], edges)

    tokens = list(reversed(tokens))

    for i in range(0, len(tokens) - 1):
        addEdge(tokens[i], tokens[i+1], reverseEdges)

    data = {"edges": edges, "reverseEdges": reverseEdges}

    fileName = title + "_edges.json"
    with open(path.join("Data", fileName), 'w') as fileStream:
        json.dump(data, fileStream)

    try:
        indexFile = open(path.join("Data", "index.json"))
        index = json.load(indexFile)
        index[title] = {"fileName": fileName, "tags": tags}
    except:
        index = {}
        index[title] = {"fileName": fileName, "tags": tags}

    indexFile = open(path.join("Data", "index.json"), 'w')
    json.dump(index, indexFile)

if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))