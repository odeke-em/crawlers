#!/usr/bin/python
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Scrap any website for files with target extensions eg pdf, png, gif etc
# Tested on, and supporting versions: Python2.X and above
# Example: ./fileDownloader.py

import os
import sys
import time

import utils

DEBUG = True # Set to False to turn off verbosity
startTimeSecs = time.time()

hitsDict = {}
missesDict = {}
dlCache = dict(misses=missesDict, hits=hitsDict)

def getFiles(url, extCompile, recursionDepth=5, httpDomain=utils.HTTPS_DOMAIN, baseDir=None):
  # Args: url, extCompile=> A pattern object of the extension(s) to match
  #      recursionDepth => An integer that indicates how deep to scrap
  #                        Note: A negative recursion depth indicates that you want
  #                          to keep crawling as far as the program can go
  if not recursionDepth:
    return
  elif not hasattr(extCompile, 'search'):
    utils.streamPrintFlush(
     "Expecting a pattern object/result of re.compile(..) for arg 'extCompile'\n"
    , sys.stderr)
    return

  if not utils.httpHeadCompile.search(url): 
    url = "%s%s"%(httpDomain, url)

  decodedData = utils.dlAndDecode(url)
  if not decodedData:
    return
  else:
    urls = utils.urlCompile.findall(decodedData)
    urls = list(
        map(lambda s: utils.repeatHttpHeadCompile.sub(utils.HTTP_HEAD_REGEX, s), urls)
    )

    if not urls:
       capableUrls = utils.urlCapableCompile.findall(decodedData)
       trimmedHeadUrl = url.strip('/')

       for capableUrl in capableUrls:
          trimmed = capableUrl.strip('/')
          fixedUrl = '%s/%s'%(trimmedHeadUrl, trimmed)
          urls.append(fixedUrl)

    plainUrls = []
    matchedFileUrls = []

    for u in urls:
        pathSelector = plainUrls
        regSearch = extCompile.search(u)
        if regSearch:
            g = regSearch.groups(1)
            u = '%s.%s'%(g[0], g[1])
            pathSelector = matchedFileUrls

        pathSelector.append(u)

    if not baseDir:
      baseDir = os.path.abspath(".")

    fullUrlToMemPath = os.path.join(baseDir, utils.pathCleanseCompile.sub('_', url))
    utils.createDir(fullUrlToMemPath)

    # Time to download all the matched files 
    dlResults = []
    for eachUrl in matchedFileUrls:
        dlResults.append(dlData(eachUrl, fullUrlToMemPath))

    resultsList = list(filter(lambda val: val, dlResults))

    # Report to user successful saves
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

      missesDict[urlHash] = (url, badCrawlCount, time.time())
      return # Cut this journey short
    else:
      utils.streamPrintFlush(
       "For url %s downloaded %d files\n"%(url, downloadCount), sys.stderr
      )

    recursionDepth -= 1
    for eachUrl in plainUrls:
      getFiles(eachUrl, extCompile, recursionDepth, baseDir=fullUrlToMemPath)

def getHash(data):
  try:
    bEncodedData = utils.byteFyer(data, **utils.encodingArgs) 
    hashDigest = utils.md5(bEncodedData).hexdigest()
  except Exception:
   return None
  else:
   return hashDigest

def dlData(url, dirStoragePath=None):
 # Args: A url
 # Download the data from the url and write it to memory
 # Returns: True iff the data was successfully written, else: False
 if not (url and utils.httpHeadCompile.search(url)):
    return None

 urlStrHash = getHash(url)
 if not urlStrHash:
   utils.streamPrintFlush("Cannot hash the provided URL")
   return
  
 isMiss = missesDict.get(urlStrHash, None) 
 if isMiss:
    if DEBUG:
      utils.streamPrintFlush("Uncrawlable link: %s"%(url))
    return None

 alreadyIn = hitsDict.get(urlStrHash, None)
 if alreadyIn:
   if DEBUG: utils.streamPrintFlush("\033[32mAlready downloaded %s\033[00m\n"%(url))
   return None

 try:
   data = utils.urlGetter.urlopen(url)
 except Exception:
   return False
 else:
   fileSearch = utils.endNameCompile.findall(url)
   if not fileSearch:
     return False

   fileName = fileSearch[0]
   fnameExtensionSeparate = utils.fnameCompile.findall(fileName)
   if not fnameExtensionSeparate:
     return False # Raise error possibly

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

   utils.streamPrintFlush("From url %s\n"%(url), sys.stderr)

   try:
     f = open(fileName, 'wb')
     f.write(data.read())
     f.close()
   except: 
     utils.streamPrintFlush("Failed to write %s to memory\n"%(fileName), sys.stderr) 
     return False
   else:
     utils.streamPrintFlush("Wrote %s to memory\n"%(fileName), sys.stderr)
     
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
      utils.streamPrintFlush(
        "\nTarget Url: eg [www.example.org or http://www.h.com] ", sys.stderr
      )
      lineIn, eofState = readFromStream()
      if eofState: break

      baseUrl = lineIn.strip("\n")

      utils.streamPrintFlush(
       "Your extensions separated by '|' eg png|html: ", sys.stderr
      )

      lineIn, eofState = readFromStream()
      if eofState: break
      extensions = lineIn.strip("\n")
      
      utils.streamPrintFlush(
        "\nRecursion Depth(a negative depth indicates you want script to go as far): "
      ,sys.stderr)

      lineIn, eofState = readFromStream()
      if eofState: break
      
      rDepth = int(lineIn.strip("\n"))

      formedRegex = utils.extensionify(extensions or utils.DEFAULT_EXTENSIONS_REGEX)
      extCompile = utils.regexCompile(formedRegex)

    except ValueError:
      utils.streamPrintFlush("Recursion depth must be an integer\n", sys.stderr)
    except KeyboardInterrupt:
      utils.streamPrintFlush("Ctrl-C applied. Exiting now..\n",sys.stderr)
      break
    except Exception:
      continue
    else:
      if not baseUrl:
        continue

      if extCompile:
        getFiles(baseUrl, extCompile, rDepth)

  utils.streamPrintFlush("Bye..\n",sys.stderr)
if __name__ == '__main__':
  try:
    main()
  except Exception:
    pass
  finally:
    utils.showStats(startTimeSecs, hitsDict, missesDict)
