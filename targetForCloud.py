#!/usr/bin/python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Sharded version of 'fileDownloader.py' except that it submits urls to a jobTable
# of which the urls will later be indexed accordingly

import sys

import utils
from resty import restDriver
from routeUtils import WorkerDriver, Router

__LOCAL_CACHE = dict()
__ROBOTS_TXT_CACHE__ = dict()

DEFAULT_TIMEOUT = 5 # Seconds

def getRobotsFile(url):
  robotsUrl = utils.robotsTxt(url)
  retr = __ROBOTS_TXT_CACHE__.get(robotsUrl, None)
  if retr is None:
    retr = memoizeRobotsFile(robotsUrl)

  return retr

def memoizeRobotsFile(roboUrl):
  res = utils.ROBOT_ERR
  try:
    robotFile = utils.urlGetter.urlopen(roboUrl)
  except Exception:
    utils.streamPrintFlush('Exception occured during extraction of robots file')
  else:
    if not robotFile.length: # No such file exists
      res = utils.ROBOT_CAN_CRAWL
    else:
      data = robotFile.read().decode()
      '''
      # TODO: Actually parse the file
      splitD = data.split('\n')
      for l in splitD:
        if l:
            pass
      '''
      res = utils.ROBOT_CAN_CRAWL # TODO: Toggle and get value if that url can be visited

  __ROBOTS_TXT_CACHE__[roboUrl] = res
  
  return res

def getFiles(url, extCompile, router, recursionDepth=5, httpDomain=utils.HTTPS_DOMAIN):
  # Args: url, extCompile=> A pattern object of the extension(s) to match
  #      recursionDepth => An integer that indicates how deep to scrap
  #                        Note: A negative recursion depth indicates that you want
  #                          to keep crawling as far as the program can go
  if not recursionDepth:
    return
  elif not hasattr(extCompile, 'search'):
    utils.streamPrintFlush(
     "Expecting a pattern object/result of re.compile(..) for arg 'extCompile'\n", sys.stderr
    )
    return

  if not utils.httpHeadCompile.search(url): 
    url = "%s%s"%(httpDomain, url)

  if getRobotsFile(url) != utils.ROBOT_CAN_CRAWL:
    return
  
  try:
    data = utils.urlGetter.urlopen(url)
    decodedData = data.read().decode() if utils.pyVersion >= 3 else data.read()
  except Exception as e:
    print('During reading of data from', url, e)
    return
  else:
    urls = utils.urlCompile.findall(decodedData)
    urls = list(map(lambda s : utils.repeatHttpHeadCompile.sub(utils.HTTP_HEAD_REGEX, s), urls))

    plainUrls = []
    matchedFileUrls = []

    for u in urls:
        pathSelector = plainUrls
        regSearch = extCompile.search(u)
        if regSearch:
            rGroup = regSearch.groups(1)
            u = '%s.%s'%(rGroup[0], rGroup[1])
            pathSelector = matchedFileUrls

        pathSelector.append(u)

    dlResults = map(
       lambda eachUrl: pushUpJob(eachUrl, router, url), set(matchedFileUrls)
    )
    resultsList = list(filter(lambda val: val, dlResults))

    recursionDepth -= 1
    for eachUrl in plainUrls:
      getFiles(eachUrl, extCompile, router, recursionDepth)

def pushUpJob(url, router, parentUrl=''):
    # First query if this item was already seen by this worker
    if __LOCAL_CACHE.get(url, None) is None:

        # Query if this file is already present 
        rDriver = router.getWorkerDriver(url)
        query = restDriver.produceAndParse(rDriver.restDriver.getJobs, message=url)
        if not (hasattr(query, 'keys') and query.get('data', None) and len(query['data'])):
            saveResponse = rDriver.restDriver.newJob(
                message=url, assignedWorker_id=rDriver.getWorkerId(),
                metaData=parentUrl, author=rDriver.getDefaultAuthor()
            )

            if saveResponse.get('status_code', 400) == 200:
                print('Successfully submitted', url, 'to the cloud')
                __LOCAL_CACHE[url] = True
        else:
            print('Was submitted to the cloud by another crawler', url)
            __LOCAL_CACHE[url] = True

    else:
        print('Already locally memoized as submitted to cloud', url)

def readFromStream(stream=sys.stdin):
  try:
    lineIn = stream.readline()
  except:
    return None, None
  else:
    EOFState = (lineIn == "")
    return lineIn, EOFState

def main():
  args, options = restDriver.cliParser()

  # Route manager
  router = Router([
    'http://127.0.0.1:8000', 'http://127.0.0.1:8008'
  ])
  while True:
    try:
      utils.streamPrintFlush(
        "\nTarget Url: eg [www.example.org or http://www.h.com] ", sys.stderr
      )
      lineIn, eofState = readFromStream()
      if eofState: break

      if lineIn:
        baseUrl = lineIn.strip("\n")

      else:
        continue

      utils.streamPrintFlush(
       "Your extensions separated by '|' eg png|html: ", sys.stderr
      )

      lineIn, eofState = readFromStream()
      if eofState: break
      extensions = lineIn.strip("\n")
      
      utils.streamPrintFlush(
        "\nRecursion Depth(a negative depth indicates you want script to go as far): ", sys.stderr
      )

      lineIn, eofState = readFromStream()
      if eofState: break

      elif lineIn:
        rDepth = int(lineIn.strip("\n") or 1)
      else:
        rDepth = 1

      formedRegex = utils.extensionify(extensions or utils.DEFAULT_EXTENSIONS_REGEX)
      extCompile = utils.regexCompile(formedRegex)

    except ValueError:
      utils.streamPrintFlush("Recursion depth must be an integer\n", sys.stderr)
    except KeyboardInterrupt:
      utils.streamPrintFlush("Ctrl-C applied. Exiting now..\n", sys.stderr)
      break
    except Exception:
      print('Generic exception encountered')
      continue
    else:
      if not baseUrl:
        continue

      if extCompile:
        getFiles(baseUrl, extCompile, router, rDepth)

  utils.streamPrintFlush("Bye..\n",sys.stderr)

if __name__ == '__main__':
  try:
    main()
  except Exception:
    sys.stderr.write('During processing, exception encountered.\nExiting now!\n')
