#!/usr/bin/env python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>

import sys
import random

WORD_RANK_CACHE = dict() # Useful to memoize expensively computed ranks

class DynaItem:
    # Enables application of the '.' method for attributes passed in
    def __init__(self, attrDict=None):
        if isinstance(attrDict, dict):
            for attr, value in attrDict.items():
                setattr(self, attr, value)

    def __str__(self):
        return self.__dict__.__str__()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        return getattr(self, key)
        

def getWordDict(word):
    # Returns a map of letters in a word
    # with their occuring indices as values
    wordDict = dict()
    for i in range(len(word)):
        ch = word[i]
        chDict = wordDict.get(ch, dict())
        chDict[i] = i
        wordDict[ch] = chDict

    return wordDict

def rankWords(subject, query):
    # Return the edit distance of subject to query
    memRank = WORD_RANK_CACHE.get(subject, None)
    if isinstance(memRank, dict):
        queryMemRank = memRank.get(query, None)
        if isinstance(queryMemRank, dict): return queryMemRank

    queryDict = getWordDict(query)
    subjectDict = getWordDict(subject)

    statDict = DynaItem(
        dict(deletions=0, inplace=0, additions=0, moves=0)
    )

    for qCh, indexDict in queryDict.items():
        subjectLookUp = subjectDict.get(qCh, None)
        if not subjectLookUp:
            statDict.deletions += len(indexDict)
        else:
            inplaceIndices = [i for i in indexDict if i in subjectLookUp]
            inplaceLen = len(inplaceIndices)
            statDict.inplace += inplaceLen
            statDict.moves += len(subjectLookUp) - inplaceLen

    additions = [c for c in subjectDict if c not in queryDict]
    statDict.additions += len(additions)

    if isinstance(memRank, dict):
        memRank[query] = statDict
    else:
        savDict = dict()
        savDict[query] = statDict
        WORD_RANK_CACHE[subject] = savDict

    return statDict

def readInFileContent(path):
    # Extract the content from a file and create a map of each word
    # and it's unique locations ie line number, word index on the line
    if not path and os.path.exists(path):
        return dict(reason='%s is a non existant path'%(path))
    else:
        wordsDict = dict()
        with open(path) as f:
            lineNumber = 0
            for l in f.readlines():
                l = l.strip('\n').strip(' ')
                lineNumber += 1
                lineContent = filter(lambda e: e, l.split(' '))
                lWordIndex = 0 # Local word index
                for w in lineContent:
                    wItem = wordsDict.get(w, [])
                    locationStateInfo = dict(
                        lineNumber=lineNumber, indexOnLine=lWordIndex
                    )
                    wItem.append(locationStateInfo)
                    if not wItem is None:
                        wordsDict[w] = wItem

                    lWordIndex += 1
    
    return wordsDict

def rankStatDict(stDict):
    return (stDict.inplace * 3) + (stDict.moves * 2) +\
           ((stDict.deletions + stDict.additions) * -1)

def createClusters(contentDict, clusterCount=2):
    samples = random.sample(contentDict.keys(), clusterCount)

    clusterDict = dict()

    for randPick in samples:
        maxStDict = DynaItem(
            dict(inplace=len(randPick), moves=0, additions=0, deletions=0)
        )
        maxRank = rankStatDict(maxStDict)
        pickList = []
        for key in contentDict:
            if key is not randPick:
                stDict = rankWords(randPick, key)
                rank = rankStatDict(stDict)
                percentRank = (float)(rank)/maxRank
                if percentRank >= 0.5:
                    pickList.append(DynaItem(
                        dict(key=key, rank=percentRank)
                    ))

        print(randPick, pickList)
        clusterDict[randPick] = pickList

    return clusterDict

def main():
    argc = len(sys.argv)
    srcPath = sys.argv[1] if argc > 1 else __file__
    # print(WORD_RANK_CACHE)
    wDict = readInFileContent(srcPath)
    # print(wDict)
    clusterDict = createClusters(wDict, 8)

if __name__ == '__main__':
    main()
