#!/usr/bin/python3
# Author: Emmanuel Odeke <odeke@ualberta.ca>

import re

intStartCompile = re.compile(r'^\d', re.UNICODE)
chStartCompile = re.compile(r'^\w', re.UNICODE)

radixDomain = [chr(i) for i in range(ord('0'), ord('9')+1)] + \
              [chr(i) for i in range(ord('a'), ord('z')+1)]


DEBUG = False # Set to False to turn off verbosity
RADIX_SIZE = len(radixDomain)

intRadixer = lambda ch : ord(ch[0]) - ord('0')
chRadixer = lambda ch : intRadixer('9') + (ord(ch[0].lower()) - ord('a'))

def getCategory(ch):
  if not ch:
    print("A non-empty string is needed")
  else:
    converter = None
    if intStartCompile.search(ch): 
      converter = intRadixer
    elif chStartCompile.search(ch):
      converter = chRadixer

    return converter

class Trie(object):
  def __init__(self, index):
    self.__index = index
    self.__additions = 0
    self.__filledIndices = set()
    self.__indices = [0 for idx in range(RADIX_SIZE)]

  def __str__(self):
    outStr = "{0}".format(self.__index)
    # print(self.__indices)
    for trieElem in self.__indices:
      if not trieElem: continue
      outStr += "\n\t=>{}".format(trieElem.__str__())

    return outStr

  def __repr__(self):
    return "Trie<{0}: Adds {1}>".format(self.__index, self.__additions)

  def addSeq(self, string, start=0, end=-1):
    # print("Str ", string)
    if (end < start): 
      if DEBUG: 
         print(
          "End is less than start, resetting and finding the string "
           "length from len(string)"
         )
      stringLen = len(string)
      end = stringLen
    else:
       stringLen = end-start

    if not stringLen: return
    try: # Deliberate out of bounds indexing exception
      headElem = string[start]
    except: return

    converterFunc = getCategory(headElem)
    if not converterFunc: return

    index = converterFunc(headElem)
    if index not in self.__filledIndices: 
       self.__indices[index] = Trie(index)
       self.__filledIndices.add(index)

    self.__additions += 1
    if stringLen > 1:
       self.__indices[index].addSeq(string, start+1, end)


  def __indexResolve(self, string, start, end):
    # print("Str ", string)
    if (end < start): 
      if DEBUG: 
         print(
          "End is less than start, resetting and finding the string "
           "length from len(string)"
         )
      stringLen = len(string)
    else:
       stringLen = end-start

    if not stringLen: return False 

    headElem = string[start]

    converterFunc = getCategory(headElem)
    if not converterFunc: return False

    index = converterFunc(headElem)
    if index not in self.__filledIndices: return None

  def search(self, string, start=0, end=-1):
    # print("Str ", string)
    if (end < start): 
      if DEBUG: 
         print(
          "End is less than start, resetting and finding the string "
           "length from len(string)"
         )
      stringLen = len(string)
      end = stringLen
    else:
       stringLen = end-start

    if (not stringLen): return False 

    print(start, end, stringLen)
    headElem = None
    try: # Deliberately catch the index-out of bounds exception
      headElem = string[start]
    except: return False

    converterFunc = getCategory(headElem)
    if not converterFunc: return False

    index = converterFunc(headElem)
    if index not in self.__filledIndices: return False

    if stringLen > 1:
      return self.__indices[index].search(string, start+1, end)

    else: return True

def trieFy(string):
  if not string: return None
 
  stLen = len(string) 
  newTrie = Trie(string[0])

  if stLen > 1:
    newTrie.addSeq(string, 0, stLen)

  return newTrie

def main():
  T = trieFy('0') # Create the root
  T.addSeq('o4eke3')
  T.addSeq('o4eke8')
  T.addSeq('o4eke2')
  T.addSeq('o4eke1')
  T.addSeq('rdeke')
  T.addSeq('sdEke')


  print([T, trieFy('b')])
  print(T.search('o4eK3e'))

if __name__ == "__main__":
  main()
