#!/usr/bin/python3
#Author: Emmanuel Odeke <odeke@ualberta.ca>
#Scrap any website for target files with target extensions eg pdf, png, gif etc
import sys
import urllib.request
import re

################################CONSTANTS HERE#####################################
DEFAULT_EXTENSIONS_REGEX = '\.(jpg|png|gif|pdf)'
HTTP_HEAD  = 'https?://'
URL_REGEX = '(%s[^\s"]+)'%(HTTP_HEAD)
REPEAT_HTTP = "%s{2,}"%(HTTP_HEAD)
END_NAME = "([^\/\s]+)$" #The text right after the last slash '/'

regexCompile = lambda regex : re.compile(regex, re.IGNORECASE)

def getFiles(url, extCompile, recursionDepth=5):
  #Args: url, extCompile=> A pattern object of the extension(s) to match
  #      recursionDepth => An integer that indicates how deep to scrap
  #                        Note: A negative recursion depth indicates that you want
  #                          to keep crawling as far as the program can go
  if not recursionDepth: return
  if not hasattr(extCompile, 'search'):
    print(
     "Expecting a pattern object/result of re.compile(..) for arg 'extCompile'"
    )
    return

  try:
    data = urllib.request.urlopen(url)  
    decodedData = data.read().decode()
  except: pass
  else:
    urls = re.findall(URL_REGEX, decodedData, re.MULTILINE)
    urls = list(map(lambda s : re.sub(REPEAT_HTTP,HTTP_HEAD,s), urls))

    images = filter(lambda s : extCompile.search(s), urls)
    nonImages = filter(lambda s : not extCompile.search(s), urls)

    #Time to download all the images
    dlResults = map(lambda eachImg: dlData(eachImg), images)
    resultsList = list(filter(lambda val: val, dlResults))

    #Report to user successful saves
    print("For url %s downloaded %d files"%(url, len(resultsList)))

    recursionDepth -= 1
    for eachUrl in nonImages:
      getFiles(eachUrl, extCompile, recursionDepth)

def dlData(url):
 #Args: A url
 #Download the data from the url and write it to memory
 #Returns: True iff the data was successfully written, else: False
 if not (url and re.search(HTTP_HEAD,url)): return None
 try: data = urllib.request.urlopen(url)
 except Exception as e: return False
 else:
   fileSearch = re.findall(END_NAME, url)
   if not fileSearch : return False
  
   fileName = fileSearch[0]
   print("From url %s"%(url))

   try:
     with open(fileName,'wb') as f:
       f.write(data.read())
       print("Wrote %s to memory"%(fileName))
       return True
   except: 
     print("Failed to write %s to memory"%(fileName)) 
     return False

def main():
  while True:
    try:
      baseUrl = input("Target Url: ")
      extensions = input("Your extensions separated by '|' eg png|html: ")
      rDepth = int(input(
        "Recursion Depth(a negative depth indicates you want script to go as far): "
      ))

      if not extensions:
        extCompile = regexCompile(DEFAULT_EXTENSIONS_REGEX)
      else:
        extCompile = regexCompile(extensions)

    except ValueError as e:
      print("Recursion depth must be an integer")
    except KeyboardInterrupt as e:
      print("Ctrl-C applied. Exiting now..")
      break
    except Exception:
      continue
    else:
      if not baseUrl:
        continue

      if extCompile:
        getFiles(baseUrl, extCompile, rDepth)
  print("Bye..")
if __name__ == '__main__':
  main()
