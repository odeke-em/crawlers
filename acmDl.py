#!/usr/bin/python3
#Author: Emmanuel Odeke <odeke@ualberta.ca>
#        Download the problem sets for the ACM finals for various years

import urllib.request, re

probsCompile = re.compile('"(http://[^"]*/problems/[^"]*\.pdf)"')

data = urllib.request.urlopen("http://www.acmicpc.org/worldfinals/problems")
readData = data.read().decode()
readData = re.sub("[\n\t]", "", readData) # Take out tabs and newlines

matches = probsCompile.findall(readData)

for match in matches:
    nameQuery = re.search(".*/problems/(.*pdf)", match)
    if nameQuery:
       dlData = urllib.request.urlopen(match)
       outData = dlData.read()
       fileName = (nameQuery.groups(1)[0])

       with open(fileName, 'wb') as f:
         f.write(outData) and print("%s written to memory"%(fileName))
