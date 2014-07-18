#!/usr/bin/env python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>

import os
import sys
import time
import random

WORD_RANK_CACHE = dict() # Useful to memoize expensively computed ranks
fOpenArgs = {}
pyVersion = int(sys.hexversion/(1<<24))
if pyVersion >= 3:
    fOpenArgs = {'encoding': 'utf-8'}

class DynaItem:
    # Enables application of the '.' method for attributes passed in
    def __init__(self, **attrDict):
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
        deletions=0, inplace=0, additions=0, moves=0
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

def readInFileContent(pathList):
    # Extract the content from a file and create a map of each word
    # and it's unique locations ie line number, word index on the line
    if not pathList:
        return {'reason': 'Expecting a pathList'}

    paths = set(
        filter(lambda p: p and os.path.exists(p) and os.path.isfile(p), pathList)
    )
    if not paths:
        return {'reason': 'No valid path could be found'}

    pLen = len(paths)
    wordsDict = dict()
    start = time.time()
    for i, path in enumerate(paths):
        with open(path, **fOpenArgs) as f:
            lineno = 0
            try:
                for l in f:
                    l = l.strip('\n').strip(' ')
                    lineno += 1
                    lineContent = filter(lambda e: e, l.split(' '))
                    charno = 0 # Local word index
                    for w in lineContent:
                        wItem = wordsDict.get(w, [])
                        locationStateInfo = dict(
                            lineno=lineno, charno=charno, source=path
                        )
                        wItem.append(locationStateInfo)
                        if not wItem is None:
                            wordsDict[w] = wItem

                        charno += len(w)

            except Exception: # TODO: Handle this error
                sys.stderr.write(
                    '\033[91mSkipping processing of: %s\033[00m\n'%(path)
                )

        sys.stdout.write('Processed: %d/%d files in %2.2f seconds\r'%(
            i + 1, pLen, time.time()-start)
        )
    sys.stdout.write(
        '\nFile Processing done in %2.2f seconds\n'%(time.time() - start)
    )
    return wordsDict

def rankStatDict(stDict):
    return (stDict.inplace * 3) + (stDict.moves * 2) +\
           ((stDict.deletions + stDict.additions) * -1)

def createClusters(content, pivotCount=2, summary=False, sorting=False, threshold=0.5, retrPivots=[]):
    pivots = retrPivots
    insufficient = lambda p: len(p) < pivotCount
    while insufficient(pivots):
        pivots += random.sample(content.keys(), pivotCount - len(pivots))
        pivots = set(pivots)

    clusterDict = dict()

    for pivot in pivots:
        maxStDict = DynaItem(inplace=len(pivot), moves=0, additions=0, deletions=0)
        maxRank = rankStatDict(maxStDict)
        pickList = []

        for key in content:
            if key is not pivot:
                stDict = rankWords(pivot, key)
                rank = rankStatDict(stDict)
                percentRank = (float)(rank)/maxRank
                if percentRank >= threshold:
                    pickList.append(DynaItem(
                        key=key, rank=percentRank, occurances=content[key]
                    ))

        if sorting:
            pickList.sort(key=lambda a: a.rank, reverse=True)

        sys.stdout.write('\033[47m%s\033[00m %s'%(
            pivot, 'Hits:' 
        ))
        if summary:
            sys.stdout.write(' %d\n'%(len(pickList)))
        else:
            sys.stdout.write('\n')
            for p in pickList:
                sys.stdout.write('\t%s\n'%(p))

        clusterDict[pivot] = pickList

    return clusterDict

def main():
    argc = len(sys.argv)
    srcPath = sys.argv[1:] if argc > 1 else [__file__]
    wDict = readInFileContent(srcPath)
    clusterDict = createClusters(wDict, threshold=0.85,
        retrPivots=[
            'Africa', 'Messi', 'Egypt', 'Hunger', 'NSA', 'Gaza',
            'Privacy', 'Ukraine', 'Snowden', 'Bloomberg', 'Spam'
            
        ]
    )

if __name__ == '__main__':
    main()
