#!/usr/bin/python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Scrap any website for files with target extensions eg pdf, png, gif etc
# Tested on, and supporting versions: Python2.X and above
# Example: ./fileDownloader.py

import re
import os
import sys
import time

from utils import streamPrintFlush, generateBadUrlReport, showStats

pyVersion = sys.hexversion/(1<<24)
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

DEBUG = False# Set to False to turn off verbosity

startTimeSecs = time.time()

dlCache = dict(
  misses=dict(),
  hits=dict()
)

hitsDict = dlCache['hits']
missesDict = dlCache['misses']

fileNameCache = dict()

################################CONSTANTS HERE#####################################
DEFAULT_EXTENSIONS_REGEX = '\.(jpg|png|gif|pdf)'
HTTP_HEAD_REGEX  = 'https?://'
URL_REGEX = '(%s[^\s"]+)'%(HTTP_HEAD_REGEX)
REPEAT_HTTP = "%s{2,}"%(HTTP_HEAD_REGEX)
END_NAME = "([^\/\s]+\.\w+)$" #The text right after the last slash '/'

HTTP_DOMAIN = "http://"
HTTPS_DOMAIN = "https://"

DEFAULT_TIMEOUT = 5 # Seconds

regexCompile = lambda regex : re.compile(regex, re.IGNORECASE)
def prepareUrl(url, httpDomain): 
  # Args: url eg http://www.ualberta.ca, https://github.com, www.ualberta.ca
  # This will handle http domain checking eg http vs https
  # sanitizing of urls and other preparations
  pass

def createDir(dirPath):
  # print("CreateDir:: ", dirPath)
  if dirPath and not os.path.exists(dirPath):
     os.mkdir(dirPath)
     if DEBUG: streamPrintFlush("Done creating %s\n"%(dirPath), sys.stderr)

def getFiles(
  url, extCompile, recursionDepth=5, httpDomain=HTTPS_DOMAIN, baseDir=None):
  #Args: url, extCompile=> A pattern object of the extension(s) to match
  #      recursionDepth => An integer that indicates how deep to scrap
  #                        Note: A negative recursion depth indicates that you want
  #                          to keep crawling as far as the program can go
  if not recursionDepth: return
  if not hasattr(extCompile, 'search'):
    streamPrintFlush(
     "Expecting a pattern object/result of re.compile(..) for arg 'extCompile'\n"
    , sys.stderr)
    return

  if not re.search(HTTP_HEAD_REGEX,url): 
    url = "%s%s"%(httpDomain, url)
    print("URL ", url)

  try:
    data = urlGetter.urlopen(url) #, timeout=DEFAULT_TIMEOUT)
    if pyVersion >= 3:decodedData = data.read().decode()
    else: decodedData = data.read()
    
  except Exception: pass
  else:
    urls = re.findall(URL_REGEX, decodedData, re.MULTILINE)
    urls = list(map(lambda s : re.sub(REPEAT_HTTP,HTTP_HEAD_REGEX,s), urls))

    matchedFileUrls = filter(lambda s : extCompile.search(s), urls)
    plainUrls = filter(lambda s : s not in matchedFileUrls, urls)
    # print(matchedFileUrls)
    # First create that directory
    if not baseDir:
      baseDir = os.path.abspath(".")
    cleanedPath = re.sub('[/:]+','_', url)
    fullUrlToMemPath = os.path.join(baseDir, cleanedPath)
    # print("FULLURL to Mem ", fullUrlToMemPath)
    createDir(fullUrlToMemPath)

    #Time to download all the matched files 
    dlResults = map(
       lambda eachUrl: dlData(eachUrl, fullUrlToMemPath), matchedFileUrls
    )
    resultsList = list(filter(lambda val: val, dlResults))
    #Report to user successful saves
    downloadCount = len(resultsList)
    # print(downloadCount) 
    if not downloadCount:
      # Mark this url as a bad one/miss and for the sake of crawling 
      # not hitting dead ends, we won't crawl it anymore unless otherwise specified
      urlHash = getHash(url)
      urlScoreTuple = missesDict.get(urlHash, None)
      badCrawlCount = 0

      if urlScoreTuple and len(urlScoreTuple) != 2: 
         badCrawlCount = (urlScoreTuple[1]) + 1 # Increment the bad crawl score

      missesDict[urlHash] = (url, badCrawlCount)
      return # Cut this journey short
    else:
      streamPrintFlush(
       "For url %s downloaded %d files\n"%(url, downloadCount), sys.stderr
      )

    recursionDepth -= 1
    for eachUrl in plainUrls:
      getFiles(eachUrl, extCompile, recursionDepth, baseDir=fullUrlToMemPath)

# def getAvailableName(proposedName):
#  isAvailable = fileTrie.getAvailableSuggestions(proposedName)
#  if isAvailable: return proposedName

def getHash(data):
  try:
    bEncodedData = byteFyer(data, **encodingArgs) 
    hashDigest = md5(bEncodedData).hexdigest()
  except:
   return None
  else:
   return hashDigest

def dlData(url, dirStoragePath=None):
 #Args: A url
 #Download the data from the url and write it to memory
 #Returns: True iff the data was successfully written, else: False
 if not (url and re.search(HTTP_HEAD_REGEX,url)): return None

 # Let's check the cache first
 # Computing the url's hash
 
 urlStrHash = getHash(url)
 if not urlStrHash:
   streamPrintFlush("Cannot hash the provided URL")
   return
  
 isMiss = missesDict.get(urlStrHash, None) 
 if isMiss:
    if DEBUG: streamPrintFlush("Uncrawlable link: %s"%(url))
    return None

 alreadyIn = hitsDict.get(urlStrHash, None)
 if alreadyIn:
   if DEBUG: streamPrintFlush("\033[32mAlready downloaded %s\033[00m\n"%(url))
   return None

 try: data = urlGetter.urlopen(url)
 except Exception: return False
 else:
   fileSearch = re.findall(END_NAME, url)
   if not fileSearch : return False

   fileName = fileSearch[0]
   fnameExtensionSeparate = re.findall("(.*)\.(\w+)$", fileName, re.UNICODE)
   if not fnameExtensionSeparate: return False # Raise error possibly
   proposedName, extension = fnameExtensionSeparate[0]
    
   # availableName = fileNameTrie.getSuggestion(proposedName)
   # if not availableName:
   #    print(
   #      "Sorry no alternate suggestions for %s could be proposed"%(fileName)
   #    )
   #    return False

   fileName = "%s.%s"%(proposedName, extension)
   # fileNameTrie.addSeq(availableName, 0, len(availableName)) # Mark this entry as taken
   if dirStoragePath and os.path.exists(dirStoragePath):
      fileName = os.path.join(dirStoragePath, fileName)

   streamPrintFlush("From url %s\n"%(url), sys.stderr)

   try:
     f = open(fileName,'wb')
     f.write(data.read())
     f.close()
   except: 
     streamPrintFlush("Failed to write %s to memory\n"%(fileName), sys.stderr) 
     return False
   else:
     streamPrintFlush("Wrote %s to memory\n"%(fileName), sys.stderr)
     
     # Let's now cache that url and mark it's content as already visited
     # where the urlString hash is the key and downloaded urls are the values
     markedContent = hitsDict.get(urlStrHash, [])
     markedContent.append(url)
     hitsDict[urlStrHash] = markedContent

     return True

def readFromStream(stream=sys.stdin):
  try:
    lineIn = stream.readline()
  except:
    return None, None
  else:
    EOFState = (lineIn == "")
    return lineIn, EOFState

def main():
  while True:
    try:
      streamPrintFlush(
        "\nTarget Url: eg [www.example.org or http://www.h.com] ", sys.stderr
      )
      lineIn, eofState = readFromStream()
      if eofState: break

      baseUrl = lineIn.strip("\n")

      streamPrintFlush(
       "Your extensions separated by '|' eg png|html: ", sys.stderr
      )

      lineIn, eofState = readFromStream()
      if eofState: break
      extensions = lineIn.strip("\n")
      
      streamPrintFlush(
        "\nRecursion Depth(a negative depth indicates you want script to go as far): "
      ,sys.stderr)

      lineIn, eofState = readFromStream()
      if eofState: break

      rDepth = int(lineIn.strip("\n"))

      if not extensions:
        extCompile = regexCompile(DEFAULT_EXTENSIONS_REGEX)
      else:
        extCompile = regexCompile(extensions)

    except ValueError:
      streamPrintFlush("Recursion depth must be an integer\n", sys.stderr)
    except KeyboardInterrupt:
      streamPrintFlush("Ctrl-C applied. Exiting now..\n",sys.stderr)
      break
    except Exception:
      continue
    else:
      if not baseUrl:
        continue

      if extCompile:
        getFiles(baseUrl, extCompile, rDepth)

  streamPrintFlush("Bye..\n",sys.stderr)
if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(e)
  showStats(startTimeSecs, hitsDict, missesDict)
