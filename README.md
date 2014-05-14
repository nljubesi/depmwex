DepMWEx - a tool for extracting multiword-expressions from dependency trees

Tree_v05.py -- contains the definitions of Node and Tree classes necessary for defining search trees, transforming parser outputs to trees and searching for search tree results inside those parse trees

grammar_sl_v03.py -- current version of the grammar for Slovene consisting of 75 search trees

grammar_hr_v04.py -- current version of the grammar for Croatian and Serbian consisting of 62 search trees

build_lexicon.py -- script merging the extracts obtained from grammar_*.py scripts, each MWE candidate satisfying the frequency criterion is scored by log-Dice and frequency

encode_lexicon.py -- script that compiles an XML lexicon from the result of the build_lexicon.py script
