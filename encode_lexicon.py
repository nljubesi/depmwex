#!/usr/bin/python
#-*-coding:utf8-*-
from xml.dom.minidom import *
import sys
import os
dir=sys.argv[1]

doc=Document()
lexicon=doc.createElement('lexicon')
doc.appendChild(lexicon)
sys.stdout.write('<?xml version="1.0" encoding="utf8"?>\n<lexicon>\n')
for file in  os.listdir(dir):
  lex,p=file.decode('utf8').split('#')
  entry=doc.createElement('entry')
  #txt=doc.createTextNode(file.decode('utf8'))
  #lexeme.appendChild(txt)
  lexeme=doc.createElement('lexeme')
  txt=doc.createTextNode(lex)
  lexeme.appendChild(txt)
  pos=doc.createAttribute('pos')
  pos.value=p
  lexeme.setAttributeNode(pos)
  entry.appendChild(lexeme)
  #lexeme.value=file.decode('utf8')
  #entry.setAttributeNode(lexeme)
  #lexeme.createAttributeattributes['lexeme'].value=file.decode('utf8')
  #lexicon.appendChild(entry)
  for line in open(dir+file):
    if line.startswith('@'):
      gramrel=doc.createElement('pattern')
      type=doc.createAttribute('type')
      type.value=line[1:-2].decode('utf8').replace(' ','_')
      gramrel.setAttributeNode(type)
      entry.appendChild(gramrel)
    elif line.startswith('\t'):
      line=line.strip().split('\t')
      mwe=doc.createElement('dependents')
      logdice=doc.createAttribute('logdice')
      logdice.value=str(round(float(line[1]),5))
      mwe.setAttributeNode(logdice)
      freq=doc.createAttribute('freq')
      freq.value=line[2]
      mwe.setAttributeNode(freq)
      for lex in line[0].decode('utf8').split(' '):
        lex,p=lex.split('#')
        lexeme=doc.createElement('lexeme')
        txt=doc.createTextNode(lex)
        lexeme.appendChild(txt)
        pos=doc.createAttribute('pos')
        pos.value=p
        lexeme.setAttributeNode(pos)
        mwe.appendChild(lexeme)
      gramrel.appendChild(mwe)
  #if len(lexicon.childNodes)==10:
  #  break
  sys.stdout.write(entry.toprettyxml(encoding='utf8'))
sys.stdout.write('</lexicon>\n')