#!/usr/bin/python3

'''
*******************************************************************
    Author: Emmanuel Odeke <odeke@ualberta.ca>

     iwebCrawler v1.O:
        Customized so far to crawl 'http:www.bbc.co.uk'
        Modifications to be made for crawling:
         + CNN website
         + TIME magazine website
         + Google News website
         + Amazon website
*******************************************************************
'''

import xml.parsers
import sys
import re
from sitereader import *
from xml.dom import minidom

BBC_URL           = "http://www.bbc.co.uk"

targUrl           = BBC_URL
HREF_STR          = "href="
LINK_REGEX        = "href=\"([^\"]*)\"\s*"
LINK_COMPILE      = re.compile( LINK_REGEX )
CONTENT_REGEX     = ">([^<>\s]*)"
CONTENT_COMPILE   = re.compile( CONTENT_REGEX )
WHITESPACE        = r"([\t\n])*"

fixFullUrl = lambda baseUrl_ChildUrl : ''.join( baseUrl_ChildUrl )

#fix non-full urls by re-appending the parentUrl.
def fullAnchorage( linksList, parentUrl=targUrl ):
    outList = []
    for link in linksList:
        if (not isfullUrl( link )):
            link = "%s%s"%( parentUrl, link )
        outList.append( link )
    return outList

def isfullUrl( testStr ):
     return ( re.search( 'https?://', testStr ) != None )

def htmlTagHandler( htmlTagStr ):
    link        = LINK_COMPILE.findall( htmlTagStr )
    htmlTagStr  = re.sub( WHITESPACE, r'', htmlTagStr )
    content     = CONTENT_COMPILE.findall( htmlTagStr )

    if ( content and link ):
        print( "\n %s"%('-'.join( content )) )
        link = fullAnchorage( link )
        return link

def recurXmlGet( targUrl, stderr, errorVerbosity, recursionDepth=2 ):
    if not recursionDepth:
        return 

    readData = site_opener( targUrl, stderr, False )
    try:
        xmlDoc = minidom.parseString( readData )

    except xml.parsers.expat.ExpatError as e:
        #Not well formed string. Fix by adding <root> and </root> tags
        readData = "<root>"+readData+"</root>"
        xmlDoc  = minidom.parseString( readData )
    except Exception as e:
        print( "unidentified exception: ", e.msg )

    listItems = xmlDoc.getElementsByTagName( "li" )
    recursionDepth -= 1
    for item in listItems:

        isPrintable = hasattr( item, 'toprettyxml' )
        if isPrintable:
            links = htmlTagHandler( item.toprettyxml() )
            if not links:
                continue 

            for link in links:
                print( link )
                try:
                    recurXmlGet( link, stderr, errorVerbosity, recursionDepth )
                except:
                    continue
def main():
    readData = recurXmlGet( targUrl, sys.stderr, False )

if __name__ == '__main__':
    main()
