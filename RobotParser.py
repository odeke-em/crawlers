#!/usr/bin/env python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>

import time
import utils

firstLetterCompile = utils.regexCompile('([a-z])')

class RobotParser:
    def __init__(self):
        self.__initTime__ = time.time()
        self.__rulesDict__ = dict()

    def addRobotRule(self, url): 
        topDomain = utils.getTopDomain(url)
        if topDomain:
            robotPath = utils.robotsTxt(topDomain)

    def parseRobotFile(self, domain, robotFile):
        if not robotFile:
            return None
        splitL = robotFile.split('\n')
        spLen = len(splitL)
        tokenCreator = lambda v, s=':': tuple(map(lambda a: a.strip(' '), v.split(s)))
        domainAllows = {}
        domainDisAllows = {}
        for i in range(spLen):
            line = splitL[i]
            if (not line) or line[0] == '#':
                continue

            attrs = tokenCreator(line)
            if attrs and attrs[0] == 'User-agent':
                clausePresent = (attrs[1] == utils.CRAWLER_NAME or attrs[1] == '*')
                if not clausePresent:
                    continue

                i += 1

                while i < spLen:
                    l = splitL[i]
                    cont = tokenCreator(l)
                    if cont[0] == 'User-agent':
                        break

                    i += 1
                    if (not l) or l[0] == '#':
                       continue 
                   
                    selector = domainDisAllows 
                    if cont[0] == 'Allow':
                        selector = domainAllows
                    elif not (cont[0] == 'Disallow' and cont[1]):
                        continue
                
                    firstCh = firstLetterCompile.search(cont[1])
                    key = '*'
                    if firstCh:
                        key = firstCh.groups(1)[0]

                    try:
                        selector.setdefault(key, []).append(utils.regexCompile(cont[1]))
                    except:
                        pass

        self.__rulesDict__[domain] = {'allow': domainAllows, 'disallow': domainDisAllows}
        return True

    def canVisit(self, url):
        topDomain = utils.getTopDomain(url)
        retrRules = self.__rulesDict__.get(topDomain, None)
        if retrRules is None: # Cache miss
            robotsUrl = utils.robotsTxt(url)
            roboFileBuf = utils.dlAndDecode(robotsUrl)
            if not self.parseRobotFile(topDomain, roboFileBuf):
                return False
            retr = self.__rulesDict__[topDomain]

        sp = tuple(filter(lambda a: a, url.split(topDomain)))
        if sp:
            firstCh = firstLetterCompile.search(sp[0])
            if firstCh:
                # Time to probe
                fCh = firstCh.groups(1)[0]
                retr = self.__rulesDict__[topDomain]['disallow']
                compList = retr.get(fCh, None)
                if compList:
                    for comp in compList:
                        if comp.search(sp[0]):
                            return False 

                    return True
        return True
                    

    def getRules(self):
        return self.__rulesDict__

    def popRobotRule(self, url):
        pass

    def editRobotRule(self, url):
        pass

def main():
    rb = RobotParser()
    qList = [
        'http://cnn.com/', 'http://time.com/time',
        'http://www.cnn.com/2014/07/14/showbiz/music/unlocking-the-truth-sony-record-deal/index.html?hpt=us_t3',
        'http://www.google.com/search', 'http://www.google.com/maps/ukraine', 'https://www.youtube.com/watch?v=Ei8nL3SvRSY'
    ]
    for q in qList:
        print(q, rb.canVisit(q))

if __name__ == '__main__':
    main()
