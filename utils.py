#!/usr/bin/python3

import sys
import time
BAD_URL_REPORT_FILE = "badUrlsReport.txt"

#Writes a message to a stream and flushes the stream
streamPrintFlush = lambda msg,stream=sys.stderr: msg and stream.write(msg) and stream.flush()


def generateBadUrlReport(missesDict):
  if missesDict:
    streamPrintFlush("\033[00mWriting report to %s\033[33m\n"%(BAD_URL_REPORT_FILE))
    with open(BAD_URL_REPORT_FILE, "a") as f:
      for urlHash, details in missesDict.items():
        url, badCrawlCount = details
        f.write("%s :: %s %d\n"%(urlHash, url, badCrawlCount))

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
    'BiOmXeKyrxo' : ('www.youtube.com/watch?v=BiOmXeKyrxo', 10)
  }

  generateBadUrlReport(misses)

if __name__ == '__main__':
  main()
