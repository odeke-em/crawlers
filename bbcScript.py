#!/usr/bin/python3

#Author: Emmanuel Odeke <odeke@ualberta.ca>
#bbcScript.py v1.0 Crawl the bbc.co.uk. website.
#Extract an xml tree, and recursively traverse the tree's links.

import re
import sys

from xml.dom import minidom

from sitereader import *
from newsfuncs  import *
from newsreaderConstants import *

################################CONSTANTS###################################

bbc_url	    = 'http://www.bbc.co.uk'
NEWLINE	    = '\n'
TAB	    = '\t'
NULL_STR    = ''

##############################REGEXS########################################

URL_REGEX	= r'<a\s+.*\s*href="([^<>]*)">.*</a>'
HEADLINE_REGEX	= r'([^>]*)</a>'
LIST_ITEM_STR	= 'li'

###########################################################################

def isfullUrl(linkStr):
   return ( re.search( HTTP_S_HEADER,linkStr) != None )

def getXMLTree( htmlString ):
   xml_tree = minidom.parseString( htmlString )
   return xml_tree

def getBBCSiteData( bbc_url, stderrStream, errorVerbosity ):
   "Return a list of links extracted from reading html content of a bbc url.\n\
    Pass in the stderrStream io_buffer to write to output as well as the\
     'errorVerbosity' flag to turn on/off active error reporting"
   bbc_html_data = site_opener( bbc_url, stderrStream, errorVerbosity ) 
   if not bbc_html_data:
      return None

   try:
      xml_tree = getXMLTree( bbc_html_data )

   except Exception as e:
      return None
   
   elements = xml_tree.documentElement
   li_items = elements.getElementsByTagName( LIST_ITEM_STR )

   outdata  = NULL_STR
   links    = []

   for item in li_items:

      value = item.toprettyxml()

      value = value.replace( HTML_AMPERSAND,ASCII_AMPERSAND )
      value = value.replace( NEWLINE,NULL_STR )
      value = value.replace( TAB,NULL_STR )

      LINK_MATCH     = re.findall( URL_REGEX,value )
      HEADLINE_MATCH = re.search( HEADLINE_REGEX,value )

      if HEADLINE_MATCH:
         headline = HEADLINE_MATCH.groups(1)[0]
         outdata += '%-65s %s'%( headline, TAB )

      if LINK_MATCH:
         child_link = LINK_MATCH[0]
         child_link = child_link.strip( '"' )
         child_link = correctMalformed( child_link )
         REV_FOUND  = child_link.find( 'rev="' )

         if REV_FOUND != -1:
            child_link = child_link[ :REV_FOUND ]

         child_link = re.sub( 'rev="(.*)"',"", str( child_link ))

         if not ( isfullUrl( child_link ) ):
            child_link = bbc_url  + child_link

         links   += [ child_link ]
         outdata += child_link

      outdata += NEWLINE

   stderrStream.write( outdata )
   stderrStream.flush()

   return links

def recurLinks( parent_link, stderr, errorVerbosity ):
   children_links    = getBBCSiteData( parent_link, stderr, errorVerbosity )

   if not children_links: 
      return None

   for child in children_links:
      grand_children_links = recurLinks( child, stderr, errorVerbosity )
      
def main():
   parser          = command_line_parse()
   options, args   = parser

   stderrFName     = options.outStderr
   errorVerbosity  = options.errorVerbosity
   
   stderr = setStderr( stderrFName )   
   links  = getBBCSiteData( bbc_url, stderr, errorVerbosity )

   for link in links:
      getBBCSiteData( link, stderr, errorVerbosity )   

if __name__ == '__main__':
   main()
