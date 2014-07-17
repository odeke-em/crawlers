#!/usr/bin/python3

import os
import re
import sys
import time

CRAWLER_NAME = 'Rosebot'
BAD_URL_REPORT_FILE = 'badUrlsReport.txt'

ROBOT_CAN_CRAWL = 0
ROBOT_SUCCESS = 1
ROBOT_ERR = 2

pyVersion = int(sys.hexversion/(1<<24))

############################# CONSTANTS HERE ##################################
DEFAULT_TIMEOUT = 5 # Seconds

extensionify = lambda extStr: '([^\s]+)\.(%s)'%(extStr)
mainDomainCompile = re.compile('(https?://[^\/]+\/?)?', re.IGNORECASE|re.UNICODE)
DEFAULT_EXTENSIONS_REGEX = 'jpg|png|gif|pdf'

HTTP_DOMAIN = "http://"
HTTPS_DOMAIN = "https://"
HTTP_HEAD_REGEX  = 'https?://'
HTTP_HEAD_REGEX  = 'https?://'

END_NAME_REGEX = "([^\/\s]+\.\w+)$" # The text right after the last slash '/'
URL_REGEX = '(%s[^\s"]+)'%(HTTP_HEAD_REGEX)
REPEAT_HTTP = "%s{2,}"%(HTTP_HEAD_REGEX)

regexCompile = lambda regex: re.compile(regex, re.IGNORECASE|re.UNICODE)

endNameCompile = regexCompile(END_NAME_REGEX)
fnameCompile = regexCompile("(.*)\.(\w+)$")
urlCompile = re.compile(URL_REGEX, re.MULTILINE|re.IGNORECASE|re.UNICODE)
httpHeadCompile = regexCompile(HTTP_HEAD_REGEX)
pathCleanseCompile = regexCompile('[/:]+')
repeatHttpHeadCompile = regexCompile(REPEAT_HTTP)

if pyVersion >= 3:
  import urllib.request as urlGetter
  encodingArgs = dict(encoding='utf-8')
else:
  import urllib as urlGetter
  encodingArgs = dict()

try:
   from hashlib import md5
   byteFyer = bytes
except ImportError:
   # Support for <= python 2.4 
   from md5 import md5
   byteFyer = lambda st, **fmtArgs : st

# Writes a message to a stream and flushes the stream
streamPrintFlush = lambda msg,stream=sys.stderr:\
    msg and stream.write(msg) and stream.flush()

def getTopDomain(url):
    if url and hasattr(url, '__str__'):
        rSearch = mainDomainCompile.search(url)
        if rSearch:
            return rSearch.groups(1)[0]

def robotsTxt(url):
    topDomain = getTopDomain(url)
    if topDomain:
        return '%s/robots.txt'%(topDomain.strip('/'))

def generateBadUrlReport(missesDict):
  if missesDict:
    streamPrintFlush("\033[33mWriting report to %s\033[00m\n"%(BAD_URL_REPORT_FILE))
    f = open(BAD_URL_REPORT_FILE, "a")
    for urlHash, details in missesDict.items():
      url, badCrawlCount, dateEpoch = details
      f.write("%f| %s :: %s %d\n"%(dateEpoch, urlHash, url, badCrawlCount))
    f.close()

def createDir(dirPath):
  # print("CreateDir:: ", dirPath)
  if dirPath and not os.path.exists(dirPath):
     os.mkdir(dirPath)
     if DEBUG: utils.streamPrintFlush("Done creating %s\n"%(dirPath), sys.stderr)

def showStats(startTimeSecs, hitsDict, missesDict):
  nDownloads = len(hitsDict)
  nMemWrites = len(hitsDict) # fileNameTrie.getAdditions()
  nBadUrls = len(missesDict)
  
  filePlurality = "files"
  dlPlurality = "downloads"
  urlPlurality = "urls"

  if nMemWrites == 1: 
    filePlurality = "file"
  if nDownloads == 1:
    dlPlurality = "download"

  endTimeSecs = time.time()
  endTimeStr = time.ctime(endTimeSecs)
  timeSpent = endTimeSecs - startTimeSecs

  streamPrintFlush ("\033[94m")
  streamPrintFlush (
   "\n\tStarted @: %s \n\tEnded   @: %s"%(time.ctime(startTimeSecs), endTimeStr)
  )
  streamPrintFlush (
    "\n\t\033[95mTotal time spent: %2.3f [seconds]"%(timeSpent)
  )
  streamPrintFlush (
   "\n\tRequested %s %s"%(dlPlurality, nDownloads)
  )
  streamPrintFlush (
    "\n\tWrote %d %s to memory\n"%(
       nMemWrites, filePlurality
    )
  )
  streamPrintFlush ("\n\033[32mBye!\033[00m\n")

  generateBadUrlReport(missesDict)


def main():
  misses = {
    'BiOmXeKyrxo' : ('www.youtube.com/watch?v=BiOmXeKyrxo', 10,time.time())
  }

  generateBadUrlReport(misses)

if __name__ == '__main__':
  main()
