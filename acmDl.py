#!/usr/bin/env python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>
#         Download the problem sets for the ACM finals for various years

import re, urllib.request

nameCompile = re.compile(".*/problems/(.*pdf)", re.UNICODE|re.IGNORECASE)
probsCompile = re.compile(
    '"(http://[^"]*/problems/[^"]*\.pdf)"', re.UNICODE|re.IGNORECASE
)

data = urllib.request.urlopen("http://www.acmicpc.org/worldfinals/problems")
readData = re.sub("[\n\t]", "", data.read().decode()) # Take out tabs and newlines
matches = probsCompile.findall(readData)

for match in matches:
    nameQuery = nameCompile.search(match)
    if nameQuery:
        fileName = nameQuery.groups(1)[0]
        if not fileName:
            print('Could not extract a name from', match)
        else:
            dlData = urllib.request.urlopen(match)
            with open(fileName, 'wb') as f:
                f.write(dlData.read()) and print("%s written to memory"%(fileName))
