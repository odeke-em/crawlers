#!/usr/bin/python3
#Author: Emmanuel Odeke <odeke@ualberta.ca>

import sys
import os
from optparse import *

def command_line_parse():
  parser = OptionParser()

  parser.add_option( "-o", "--outStderr", dest="outStderr", help=\
    "Set the stream for standard error. If no argument is passed, the default standard error stream will be sys.stderr", default="" )
  parser.add_option( "-v", "--errorVerbosity", dest="errorVerbosity", help=\
    "Set whether to write errors and exception messages to the standard error",
    default=True )
  ( options,args ) = parser.parse_args()
  return ( options,args )

def setStderr( stderrPath='', fmode=r'a' ):
  if ( not stderrPath ):
    return sys.stderr

  PATH_EXISTANT = os.path.exists( stderrPath )

  if ( not PATH_EXISTANT ): #If none existant path, create one
    fmode = r'w'

  try:
    fStream = open( stderrPath , fmode )

  except ValueError:
    
    raise Exception( "Invalid file opening mode: %s"%( fmode ))
    exit( 1 )

  else:
    assert( fStream )
    return fStream

