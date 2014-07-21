#!/usr/bin/python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# CNNscript.py v1.0 
# Script to crawl the CNN website:
#     Recursively crawl the links on the page. To control the amount of crawling, 
#     the attribute 'recursionDepth' is checked and gives the kick to signal
#     an end to crawling a link 

import re
import sys

from sitereader import *
from newsfuncs  import *
from newsreaderConstants import *

#########################################CONSTANTS#####################################
CNN_URL               = 'http://www.cnn.com/'
FROM_CLASS_LINK_REGEX = r'<li class=".*"><a href="(.*)"><span>(.*)</span></a></li>\s*'
LINK_INNER_HTML_REGEX = r'<a href="(.*)">(.*)</a>\s*'
HEADINGS_REGEX        = r'.*<h[1-9]><span><a href="(.*)">(.*)</a></span></h[1-9]>\s*'
IMG_ATTRIBUTES        = ['alt','width','border','height']
#######################################################################################

def getLinks( xmlLine, stderr, errorVerbosity, photoLinkStorage, recursionDepth ):
    "Extracts and prints headlines and links extracted from the xmlLine\n\
    Mutually calls 'getCNNXML(...)' recursively, to extract xmldata for every link"
    if ( not xmlLine ) or ( not recursionDepth ):
        return 

    recursionDepth -= 1
    xmlLine = re.sub( HTML_AMPERSAND, ASCII_AMPERSAND, xmlLine )
    urlLocSearchQuery = re.search( FROM_CLASS_LINK_REGEX, xmlLine )

    if not urlLocSearchQuery: #Try another urlLoc pattern
        urlLocSearchQuery = re.search( LINK_INNER_HTML_REGEX, xmlLine )

    if urlLocSearchQuery:
        urlLoc,urlLocHeadline = urlLocSearchQuery.groups()
    
        for attr in IMG_ATTRIBUTES:
            #Test and Rip-out the photoLink
            IMGSRC_REGEX = r'<.*="(https?:[^"]*\.\w+)"\s*%s=.*'%( attr )
            imgsrcpat = re.search( IMGSRC_REGEX, urlLocHeadline )

            if imgsrcpat:
                imgresults = imgsrcpat.groups( 1 )[0]
                photoLinkStorage += [ imgresults ]

        urlLocCleaned = re.findall( r'"?(https?:[^"]*)">([^<]*)', urlLoc )
        if urlLocCleaned:
            for extraLink in urlLocCleaned:
                urlLoc, headLine = extraLink
                print( '{}   :   {}\n'.format( headLine, urlLoc ))
        else:
            print( '{}   :   {}\n'.format( urlLocHeadline, urlLoc ) )
        getCNNXML( urlLoc, stderr, errorVerbosity, photoLinkStorage, recursionDepth )

def getCNNXML( CNN_URL, stderr, errorVerbosity, photoStorage, recursionDepth=5 ):
    "Opens the url, returning the xmldata retrieved, and for every line in the data\n\
    mutually calls 'getLinks(...)' recursively, to extract headlines, and links"
    data = site_opener( CNN_URL, stderr, errorVerbosity )
    if ( not data ) or ( not recursionDepth ):
        return 

    data = data.split( '\n' )
    recursionDepth -= 1
    #print( "RecursionDepth: ", recursionDepth )

    for line in data:
        getLinks( line, stderr, errorVerbosity, photoStorage, recursionDepth )
def main():
    parser          = command_line_parse()
    options, args   = parser
    stderrFName     = options.outStderr
    stderr          = setStderr( stderrFName )
    errorVerbosity  = int( options.errorVerbosity )

    photoLinks = []
    recursionDepth = 5

    getCNNXML( CNN_URL, stderr, errorVerbosity, photoLinks, recursionDepth )

    for imgLink in photoLinks:
        print( imgLink )

if __name__ == '__main__':
    main()
