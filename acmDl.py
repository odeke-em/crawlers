#!/usr/bin/python3

#Author: Emmanuel Odeke <odeke@ualberta.ca>
#        Download the problem sets for the ACM finals for various years

import urllib.request, re
url = "http://www.acmicpc.org/worldfinals/problems"

data = urllib.request.urlopen( url )
readData = ( data.read() ).decode()
readData = re.sub( "[\n\t]","", readData ) #Take out tabs and newlines

PROBS_REGEX  = '"(http://[^"]*/problems/[^"]*\.pdf)"'
probsCompile = re.compile( PROBS_REGEX )

matches = probsCompile.findall( readData )
#print( matches )
for match in matches:
    nameQuery = re.search( ".*/problems/(.*pdf)", match )
    if nameQuery:
       dlData = urllib.request.urlopen( match )
       outData = dlData.read()
       fileName = ( nameQuery.groups( 1 )[0])
       f = open( fileName, 'wb' )
       f.write( outData )

       f.flush()
       f.close()
       print( "%s written to memory"%( fileName ))
