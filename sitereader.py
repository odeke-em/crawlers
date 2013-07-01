#!/usr/bin/python3
#Author: Emmanuel Odeke <odeke@ualberta.ca>

import urllib.request,urllib.error,re

IPAD_UAGENT = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) '+\
              'AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4'+\
              ' Mobile/7B334b Safari/531.21.102011-10-16'

UBUNTU_UAGENT ='Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:13.0) Gecko/20100101 Firefox/13.0'

def correctMalformed( malUrl ):
  reComp = re.compile( r'(.*)"' )
  reSearch = reComp.sub( r'', malUrl )
  return reSearch
    

def site_opener( url,stderr,errorVerbosity, user_agent=IPAD_UAGENT ):
  "Create a custom url opener using a fake browser useragent."    

  modified_opener   = urllib.request.build_opener()
  user_agent_tuple = ('user-agent',user_agent)
  modified_opener.addheaders = [user_agent_tuple]

  try:
    data = modified_opener.open(url)

  except Exception as e:
    if isinstance( e, urllib.error.URLError ):
      if ( errorVerbosity ):
        stderr.write( "URLError instance found on: %s\n"%( url ))
        stderr.flush()
    return None

  outdata = data.read()

  try:
    decoded_data = outdata.decode()
  except Exception as e:
    #Manage error later#
    if ( errorVerbosity ):
      stderr.write( "Decoding error: errorBelow: %s\n"%( e ))
      stderr.flush()
    return None

  return decoded_data
