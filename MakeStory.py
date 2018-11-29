import sys
import argparse
import os
import os.path as path
import re
from collections import Counter
import string

import json
import nltk
import random
from numpy.random import choice

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--characterConfig")

def main(**argv):

    characterConfig = argv["characterConfig"]

    # Story parts
    characters = []
    characterMap = {}
    tagUsage = {}
    minWordCount = 50000.0

    # load input index    
    indexFile = json.load(open(path.join("Data", "index.json")))
    tags = getTags(indexFile)

    # load names
    firstNamesJson = json.load(open("FirstNames.json"))
    firstNames = firstNamesJson["firstNames"]
    lastNamesJson = json.load(open("LastNames.json"))
    lastNames = lastNamesJson["lastNames"]

    # Get narrative structure

    # Get characters
    if characterConfig is None:
        characterMap, tagUsage = buildCharacterMap(random.randint(3, 7), random.randint(7, 12), tags, firstNames, lastNames)
    else: 
        characterMap = json.load(open(characterConfig))
        tagUsage = {}
        for c in characterMap["mainCharacters"]:
            for t in c["requiredTags"]:
                if t in tagUsage:
                    tagUsage[t] += 1
                else:
                    tagUsage[t] = 1
                    
            for t in c["requiredTags"]:
                if t in tagUsage:
                    tagUsage[t] += 1
                else:
                    tagUsage[t] = 1
                    
        for c in characterMap["secondaryCharacters"]:
            for t in c["requiredTags"]:
                if t in tagUsage:
                    tagUsage[t] += 1
                else:
                    tagUsage[t] = 1
                    
            for t in c["requiredTags"]:
                if t in tagUsage:
                    tagUsage[t] += 1
                else:
                    tagUsage[t] = 1

    # Get character vocabs
    indexValues = list(indexFile.values())
    for c in characterMap["mainCharacters"]:
#        files = list(filter(lambda y: all(t in y["tags"] for t in characterMap["mainCharacters"][c]["requiredTags"]) and any(t in y["tags"] for t in characterMap["mainCharacters"][c]["optionalTags"]), indexValues))
        files = list(filter(lambda y: all(t in y["tags"] for t in characterMap["mainCharacters"][c]["requiredTags"]), indexValues))
        files = list(f["fileName"] for f in files)

        # Load vocab files and combine models
        edges = None
        reverseEdges = None
        for f in files:
            text = json.load(open(path.join("Data", f)))
            if edges is None:
                edges = text["edges"]
                reverseEdges = text["reverseEdges"]
            else: 
                edges = combineModels(edges, text["edges"])
                reverseEdges = combineModels(reverseEdges, text["reverseEdges"])

#        edges = cleanEdgesDict(edges)
#        reverseEdges = cleanEdgesDict(reverseEdges)

        characterMap["mainCharacters"][c]["edges"] = edges
        characterMap["mainCharacters"][c]["reverseEdges"] = reverseEdges
        
    for c in characterMap["secondaryCharacters"]:
        #files = list(filter(lambda y: all(t in y["tags"] for t in characterMap["secondaryCharacters"][c]["requiredTags"]) and any(t in y["tags"] for t in characterMap["secondaryCharacters"][c]["optionalTags"]), indexValues))
        files = list(filter(lambda y: all(t in y["tags"] for t in characterMap["secondaryCharacters"][c]["requiredTags"]), indexValues))
        files = list(f["fileName"] for f in files)

        # Load vocab files and combine models
        edges = None
        reverseEdges = None
        for f in files:
            text = json.load(open(path.join("Data", f)))
            if edges is None:
                edges = text["edges"]
                reverseEdges = text["reverseEdges"]
            else: 
                edges = combineModels(edges, text["edges"])
                reverseEdges = combineModels(reverseEdges, text["reverseEdges"])

 #       edges = cleanEdgesDict(edges)
 #       reverseEdges = cleanEdgesDict(reverseEdges)
        characterMap["secondaryCharacters"][c]["edges"] = edges
        characterMap["secondaryCharacters"][c]["reverseEdges"] = reverseEdges

    # Get narrator
    requiredTags = []
    requiredTags.extend(random.sample(tags, 1))
    optionalTags = []
    optionalTags.extend(random.sample(tags.difference(set(requiredTags)), 2))
#    files = list(filter(lambda y: all(t in y["tags"] for t in requiredTags) and any(t in y["tags"] for t in optionalTags), indexValues))
    files = list(filter(lambda y: all(t in y["tags"] for t in requiredTags), indexValues))
    files = list(f["fileName"] for f in files)
    narratorEdges = None
    narratorReverseEdges = None
    for f in files:
        text = json.load(open(path.join("Data", f)))
        if narratorEdges is None:
            narratorEdges = text["edges"]
            narratorReverseEdges = text["reverseEdges"]
        else: 
            narratorEdges = combineModels(narratorEdges, text["edges"])
            narratorReverseEdges = combineModels(narratorReverseEdges, text["reverseEdges"])


 #   narratorEdges = cleanEdgesDict(narratorEdges)
 #   narratorReverseEdges = cleanEdgesDict(narratorReverseEdges)

    # Write scenes
    scenes = []
    scenesWith = list(characterMap["scenesWith"])
    scenesWith2 = list()
    mainNames = list(characterMap["mainCharacters"].keys())
    # secondaryNames = list(characterMap["secondaryCharacters"].keys())
    for s in scenesWith:
        if s[0] in mainNames and s[1] in mainNames:
            scenesWith2.append(s)

    scenesWith.extend(scenesWith2)
    random.shuffle(scenesWith)

    wordsPerScene = int(minWordCount / len(characterMap["scenesWith"])) + 1
    characters = characterMap["mainCharacters"]
    characters.update(characterMap["secondaryCharacters"])

    for s in scenesWith:
        scenes.append(writeScene({"narratorEdges": narratorEdges, "narratorReverseEdges": narratorReverseEdges}, s[0], characters[s[0]], s[1], characters[s[1]], wordsPerScene))

        # if len(scenes) > 5:
        #     break

    # Get scene sentiment

    # Organize scenes

    sceneTexts = [i[0] for i in scenes]
    sceneTitles = [i[1] for i in scenes]

    tableOfContents = 'TABLE OF CONTENTS\n\n'
    novel = ''

    for i in range(0, len(sceneTexts)):
        chapterTitleString = "Chapter " + str(i) + ": " + sceneTitles[i] + "\n"
        novel += chapterTitleString + "\n\n"
        novel += sceneTexts[i] + "\n\n\n\n"
        tableOfContents += chapterTitleString

    staring = 'STARING\n\n'
    for c in characterMap["mainCharacters"]:
        staring += characterMap["mainCharacters"][c]["requiredTags"][0] + " " + c + "\n"
        
    for c in characterMap["secondaryCharacters"]:
        staring += characterMap["secondaryCharacters"][c]["requiredTags"][0] + " " + c + "\n"

    novel = staring + "\n\n\n" + novel
    novel = tableOfContents + "\n\n\n" + novel

    novelTitle = random.choice(sceneTitles)
    novel = novelTitle + "\n\n\n\n" + novel

    with open(novelTitle + ".txt", 'wb') as output:
        output.write(novel.replace("\n", os.linesep).encode("utf-8"))

    print("done writing " + novelTitle)

def getTags(indexFile):
    tags = set()

    for i in indexFile:
        for t in indexFile[i]["tags"]:
            tags.add(t)

    return tags

def buildCharacterMap(mainCharacterCount, secondaryCharacterCount, tags, firstNames, lastNames):
    mainCharacters = {}
    secondaryCharacters = {}

    for i in range(0, mainCharacterCount):
        ### Create character names
        charName = random.choice(firstNames) + " " + random.choice(lastNames)

        requiredTags = []
        requiredTags.extend(random.sample(tags, 1))

        optionalTags = []
        optionalTags.extend(random.sample(tags.difference(set(requiredTags)), 2))

        mainCharacters[charName] = {"requiredTags": requiredTags, "optionalTags": optionalTags}

    for i in range(0, secondaryCharacterCount):
        ### Create character names
        charName = random.choice(firstNames)

        requiredTags = []
        requiredTags.extend(random.sample(tags, 1))

        optionalTags = []
        optionalTags.extend(random.sample(tags.difference(set(requiredTags)), 2))

        secondaryCharacters[charName] = {"requiredTags": requiredTags, "optionalTags": optionalTags}

    scenesWith = set()

    for m in mainCharacters:
        for n in mainCharacters:
            if n is not m:
                scenesWith.add((m,n) if m < n else (n,m))

    for s in secondaryCharacters:
        for m in random.sample(mainCharacters.keys(), max(int(0.3*len(mainCharacters)), 1)):
            scenesWith.add((m,s) if m < s else (s,m))

    return {"mainCharacters": mainCharacters, "secondaryCharacters": secondaryCharacters, "scenesWith": scenesWith}, None

def combineModels(model1, model2):
    for k in model2:
        if k in model1:
            model1[k] = dict(Counter(model1[k]) + Counter(model2[k]))
        else:
            model1[k] = model2[k]

    return model1

def writeScene(narrator, character1Name, character1, character2Name, character2, wordsPerScene):
    text = ""
    title = ""
    wordCount = 0
    subject = None
    topics = []

    characters = [character1, character2]
    random.shuffle(characters)
    narratorMaxSentence = 6
    characterMaxSentence = 4

    while wordCount < wordsPerScene:
        # Narrator
        sentenceCount = 0
        paragraph = ""
        seed = None
        narratorSentenceMax = random.randint(1, narratorMaxSentence)
        while sentenceCount <= narratorSentenceMax:
            sentenceTopic = subject if sentenceCount == 0 or random.random() < 0.25 else None
            sentence = writeSentence(narrator["narratorEdges"], narrator["narratorReverseEdges"], sentenceTopic, seed)
            paragraph += sentence
            sentenceCount += 1

        wordCount += len(str.split(paragraph))
        text += paragraph + "\n\n\n"

        foundTopics = findTopics(paragraph)

        subject = None
        if len(foundTopics) > 0:
            topics.append(foundTopics[0][0])

            for t in foundTopics:
                if t[0] in characters[0]["edges"].keys():
                    subject = t[0]
                    break

        # character 1
        sentenceCount = 0
        paragraph = ""
        seed = None
        characterSentenceMax = random.randint(1, characterMaxSentence)
        while sentenceCount <= characterSentenceMax:
            sentenceTopic = subject if sentenceCount == 0 or random.random() < 0.3 else None
            sentence = writeSentence(characters[0]["edges"], characters[0]["reverseEdges"], sentenceTopic, seed)
            if sentenceCount == 0:
                saidText = " said " + character1Name + ". \"" if random.random() < 0.5 else " " + character1Name + " said. \"" 
                sentence = '"' + sentence.strip() + '"' + saidText
            #     paragraph += sentence
            # else:
            #     paragraph += sentence + " "
            
            paragraph += sentence
            
            sentenceCount += 1

        paragraph = paragraph.strip() + '"'
        wordCount += len(str.split(paragraph))
        text += paragraph + "\n\n\n"

        foundTopics = findTopics(paragraph)

        subject = None
        if len(foundTopics) > 0:
            topics.append(foundTopics[0][0])

            for t in foundTopics:
                if t[0] in characters[1]["edges"].keys():
                    subject = t[0]
                    break

        # character 2
        sentenceCount = 0
        paragraph = ""
        seed = None
        characterSentenceMax = random.randint(1, characterMaxSentence)
        while sentenceCount <= characterSentenceMax:
            sentenceTopic = subject if sentenceCount == 0 or random.random() < 0.3 else None
            sentence = writeSentence(characters[1]["edges"], characters[1]["reverseEdges"], sentenceTopic, seed)
            if sentenceCount == 0:
                saidText = " said " + character2Name + ". \"" if random.random() < 0.5 else " " + character2Name + " said. \"" 
                sentence = '"' + sentence.strip() + '"' + saidText
            #     paragraph += sentence
            # else:
            #     paragraph += sentence + " "

            paragraph += sentence
            sentenceCount += 1

        paragraph = paragraph.strip() + '"'
        wordCount += len(str.split(paragraph))
        text += paragraph + "\n\n\n"

        foundTopics = findTopics(paragraph)
        
        subject = None
        if len(foundTopics) > 0:
            topics.append(foundTopics[0][0])

            for t in foundTopics:
                if t[0] in narrator["narratorEdges"].keys():
                    subject = t[0]
                    break

    topics = list(map(lambda x: re.sub(r'\.', '', x), topics))

    if len(topics) < 1 or random.random() < 0.15:
        title = character1Name + " and " + character2Name
    elif len(topics) < 2 or random.random() < 0.2:
        title = character1Name + " and " + character2Name + " discuss " + topics[0]
    elif len(topics) < 3 or random.random() < 0.3:
        title = character1Name + " and " + character2Name + " discuss " + topics[0] + " and " + topics[1]
    else:
        titleTopics = random.sample(topics, 3)
        random.shuffle(titleTopics)
        title = titleTopics[0] + ", " + titleTopics[1] + ", and " + titleTopics[2]

    return text, title

def writeSentence(edges, reverseEdges, topic, seed):
    sentence = []
    sentenceStart = []
    lastWord = None

    if topic is not None:
        lastWord = topic

        sentenceStart.append(lastWord)

        # Note that currently proper nouns as topics will always become the start of a sentence
        while not lastWord.istitle():
            lastWord = choseNext(lastWord, reverseEdges)
            sentenceStart.insert(0, lastWord)

            if lastWord == '*....':
                break

            # if lastWord[0] in ['.', ',', ';', '?', '!', ':', '\'']:
            #     sentenceStart = sentenceStart.lstrip()

            # if len(sentenceStart.split()) > 20: 
            #     sentenceStart = "..." + sentenceStart
            #     break

            if len(sentenceStart) > 3 and sentenceStart[0] == sentenceStart[1] == sentenceStart[2]:
                break

        lastWord = topic
        sentence = sentenceStart
        # sentence = ' '.join(sentenceStart)
        # sentence = (sentence + " " if not(sentence == '') else "") + lastWord + " "

    if topic is None and seed is None:
        capitalized = list(filter(lambda x: x.istitle() and "." not in x, edges.keys()))
        lastWord = choice(capitalized)
        sentence.append(lastWord)
    elif lastWord is None:
        lastWord = choseNext(seed, edges)
        sentence.append(lastWord)

    while lastWord not in [".", "!", "?", "...", "*...."]:
        lastWord = choseNext(lastWord, edges)

        # if lastWord[0] in ['.', ',', ';', '?', '!', ':', '\'', '...', '*....']:
        #     sentence = sentence.strip()

        # sentence += lastWord + " "

        sentence.append(lastWord)

        # if len(sentence.split()) - len(sentenceStart.split()) > 25: 
        #     sentence = sentence + "..."
        #     break

    sentence = " ".join(sentence).strip().lstrip()
    for c in [' .', ' ,', ' ;', ' ?', ' !', ' :', ' \'', ' ...', ' *....']:
        sentence = sentence.replace(c, c.lstrip())

    return sentence + " "

def choseNext(word, edges):
    tabooList = []
    next = choseWeighted(edges[word], tabooList)

    while next not in edges.keys():

        tabooList.append(next)

        next = choseWeighted(edges[word], tabooList)

        if next == '':
            next = "*...."
            break

    return next

def choseWeighted(weightedList, tabooList):

    weightedListFiltered = {k:v for k,v in weightedList.items() if k not in tabooList}
    choices = list(weightedListFiltered.keys())
    weights = list(weightedListFiltered.values())
    weights = list(weights)

    # count = len(choices)

    # for i in range(0, count):



    # choices = [c for c in choices if c not in tabooList]

    if len(choices) < 1:
        return ''

    total = sum(weights)
    weights = list(map(lambda x: x / total, weights))

    return choice(list(choices), p=weights)

def findTopics(text):
    topics = nltk.word_tokenize(text)
    topics = list(filter(lambda x: x[1] == 'NN', nltk.pos_tag(topics)))
    topics = [i[0] for i in topics]
    topics = Counter(topics).most_common(5)

    return topics

# def cleanEdgesDict(edges):

#     return edges

#     newEdges = {}
#     for k in edges.keys():
#         newValues = {}
#         if not(k == '”') and not(k == '“') and not(k == '"') and not(k == "''") and not(k == "’") and not(k == "'") and not(k == "``"):
#             for l in edges[k]:
#                 if not(l == '”') and not(l == '“') and not(l == '"') and not(k == "''") and not(k == "'’") and not(k == "'") and not(k == "``"):
#                     newValues[stripPunctuation(l)] = edges[k][l]

#             if len(newValues) > 0:
#                 newEdges[stripPunctuation(k)] = newValues

#     # edges = {k: v for k,v in edges.items() if wordFilterCondition(k)}

#     # keys = edges.keys()
#     # for k in keys:
#     #     e = edges[k]
#     #     e = {k: v for k,v in e.items() if wordFilterCondition(k)}
#     #     e = {k: v for k,v in e.items() if cleanWord(k)}
#     #     if len(e.keys()) > 0:
#     #         newEdges[k] = e

#     return newEdges

# def stripPunctuation(word):
#     newWord = word

#     newWord = re.sub(r'[.!_\'"”“]', '', newWord)

#     return newWord if newWord is not "" else word

# def wordFilterCondition(word):
#     return not('"' in word) and not('_' in word) and not('”' in word) and not('“' in word) and not('`' in word)

if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))