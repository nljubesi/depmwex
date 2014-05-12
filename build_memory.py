#!/usr/bin/python
import sys
import re

lemma_re=re.compile(r'^\w+$',re.UNICODE)

min_triple_freq=int(sys.argv[2])
min_rel_w2_num=int(sys.argv[3])
min_rel_num=int(sys.argv[4])

lexicon=None
if len(sys.argv)==6:
  lexicon=set([e[:-1] for e in open(sys.argv[5])])

distr_triple={}
distr_left={}
distr_right={}

for line in sys.stdin:
  try:
    w1,rel,w2=line.strip().split('\t')
  except:
    continue
  try:
    if lexicon==None:
      if lemma_re.match(w1.decode('utf8')[:2])==None or lemma_re.match(w2.decode('utf8')[:2])==None:
        continue
    else:
      if w1.replace('_se#V','#V') not in lexicon:
        continue
      w2_sub_unk=False
      for w2_sub in w2.split(' '):
        if w2_sub.replace('_se#V','#V') not in lexicon:
          w2_sub_unk=True
          break
      if w2_sub_unk:
        continue
  except:
    continue
  w1_rel=w1+'|'+rel
  distr_left[w1_rel]=distr_left.get(w1_rel,0)+1
  distr_right[w2]=distr_right.get(w2,0)+1
  rel_w2=rel+'|'+w2
  if w1 not in distr_triple:
    distr_triple[w1]={}
  distr_triple[w1][rel_w2]=distr_triple[w1].get(rel_w2,0)+1

logdice={}
from math import log
for w1 in distr_triple:#,key=lambda x:x.split('|')[0]):
  logdice={}
  rel_w2_lf={}
  for rel_w2 in distr_triple[w1]:
    if distr_triple[w1][rel_w2]<min_triple_freq:
      continue
    rel,w2=rel_w2.split('|')
    w1_rel=w1+'|'+rel
    if rel not in rel_w2_lf:
      rel_w2_lf[rel]={}
    rel_w2_lf[rel][w2]=(14+log((2.*distr_triple[w1][rel_w2])/(distr_left[w1_rel]+distr_right[w2]),2),distr_triple[w1][rel_w2])
  if sum([len(rel_w2_lf[e]) for e in rel_w2_lf])>=min_rel_w2_num and len(rel_w2_lf)>=min_rel_num:
    file=open(sys.argv[1]+w1,'w')
    file.write('#############################\n'+w1+'\n#############################\n')
    for rel in sorted(rel_w2_lf,key=lambda x:-len(rel_w2_lf[x])):
      file.write(rel+'\n')
      for w2 in sorted(rel_w2_lf[rel],key=lambda x:-rel_w2_lf[rel][x][0]):
        file.write('\t'+w2+'\t'+str(rel_w2_lf[rel][w2][0])+'\t'+str(rel_w2_lf[rel][w2][1])+'\n')
  #print (logdice[triple]+distr_triple[triple])/2,logdice[triple],distr_triple[triple],triple

#for triple in log