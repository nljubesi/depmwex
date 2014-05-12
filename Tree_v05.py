#!/usr/bin/python
# 03 relation nodes annotated
# 03 lexeme relation memory, optional nodes branched
# 04 criterion "not having child like..." -- reflexive verbs! -- reflexive finally solved on sentence level
# 04 add specific node fetures to names of relations (like prepositions)
# 04 memory contains distributions over MSD, deprel etc.
# 05 removed distributions over MSDs, takes too much memory (for now)
# 05 show_relations() changed
from collections import defaultdict
from copy import deepcopy
import sys
import re

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

class Node(object):

	def __init__(self,data,parent,tree,search=True,relation=None,optional=False):
		self.data=data
		self.children=[]
		self.parent=parent
		self.tree=tree
		if search:
			#self.search=True
			self.found=None
			self.relation=relation
			self.optional=optional

	def add_child(self,obj):
		self.children.append(obj)
		
	#def add_tree(self,tree):
	#	for node 

	def has_child(self,criterion):
		for child in self.children:
			if criterion(child):
				return True
		return False
	
	def show(self,level):
		sys.stdout.write('\t'*level+repr(self.data)+'\n')
		for child in self.children:
			child.show(level+1)
	
	def show_find(self,level):
		sys.stdout.write('\t'*level+repr(self.found)+'\n')
		for child in self.children:
			child.show_find(level+1)
	
	def show_lemma(self,level=0):
		sys.stdout.write('\t'*level+' '.join([self.found[attr] for attr in ['deprel','lemma','token','msd']])+'\n')
		for child in self.children:
			if child.found is not None:
				child.show_lemma(level+1)
	
	def compare_with_node(self,node):
		return self.data(node)
	
	def node_in_search_tree(self,node):
		for search_node in self.tree.nodes.values():
			if node.data==search_node.found:
				return True
		return False

	def search_subtree(self,node):
		if self.compare_with_node(node):
			if not self.node_in_search_tree(node):
				self.found=node.data
				for search_child in self.children:
					for node_child in node.children:
						search_child.search_subtree(node_child)

class Tree(object):
	def __init__(self,search=True):
		self.nodes={0:Node(defaultdict(str,{'root':True}),self,self)}
		self.search=search

	def add_node(self,num,parent,data,relation=None,optional=False):
		node=Node(data,parent,self,self.search,relation,optional)
		if parent!=self:
			self.nodes[parent].add_child(node)
		self.nodes[num]=node
	
	def get_root(self):
		return self.nodes[0]
	
	def show(self):
		self.nodes[0].show(level=0)
	
	def show_find(self):
		self.nodes[0].show_find(level=0)
	
	def show_lemma(self):
		self.nodes[0].show_lemma(level=0)

	def show_relations(self,stream=sys.stdout,position=None):
		for num,node in sorted(self.nodes.items()):
			if node.relation is not None and node.relation!='print':
				stream.write(node.found['lemma']+'#'+node.found['msd'][:2]+'\t@'+node.relation(node.tree)+'@\t')
				if position is not None:
					positions=[str(position+node.found['pos'])]
				for num2,node2 in sorted(self.nodes.items()):
					if num2!=num:
						if node2.found is not None:
							if node2.relation is not None:
								stream.write(node2.found['lemma']+'#'+node2.found['msd'][:2]+' ')
								if position is not None:
									positions.append(str(position+node2.found['pos']))
				if position is not None:
					stream.write('\t'+' '.join(positions))
				stream.write('\n')

	def memorize_relations(self,memory):
		for num,node in sorted(self.nodes.items()):
			if node.relation is not None:
				lemma=node.found['lemma']+'#'+node.found['msd'][0]
				relation=node.relation(node.tree)
				#sys.stdout.write(node.found['lemma']+'\t'+node.relation+'\t')
				phrase=[]
				optional=None
				optional_msd=None
				for num2,node2 in sorted(self.nodes.items()):
					if num2!=num:
						if not node2.optional:
							phrase.append(node2.found['lemma']+'#'+node2.found['msd'][0])
						else:
							if node2.found is not None:
								optional=node2.found['lemma']+'#'+node2.found['msd'][0]
				if lemma not in memory:
					memory[lemma]={}
				if relation not in memory[lemma]:
					memory[lemma][relation]={}
				phrase=' '.join(phrase)
				if phrase not in memory[lemma][relation]:
					memory[lemma][relation][phrase]={'count':0,'optionals':{}}
				memory[lemma][relation][phrase]['count']+=1
				if optional is not None:
					memory[lemma][relation][phrase]['optionals'][optional]=memory[lemma][relation][phrase]['optionals'].get(optional,0)+1


	def search_is_successful(self):
		for index in self.nodes:
			if self.nodes[index].found==None and not self.nodes[index].optional:
				return False
		return True

	def initialize_search_tree(self):
		for index in self.nodes:
			self.nodes[index].found=None

	def search_subtrees(self,search_tree):
		hits=[]
		for index in self.nodes:
			search_tree.get_root().search_subtree(self.nodes[index])
			if search_tree.search_is_successful():
				hits.append(deepcopy(search_tree))
			search_tree.initialize_search_tree()
		return hits

	def get_lemma(self):
		lemma=''
		for index in self.nodes:
			if self.nodes[index].found is not None:
				lemma+=self.nodes[index].found['lemma']+' '
		return lemma

def create_tree_from_sentence(sent):
	tree=Tree(search=False)
	known_nodes=set([0])
	while len(sent)>0:
		for known_node in list(known_nodes):
			for feats in sent[known_node]:
				tree.add_node(num=feats[0],parent=feats[4],data=defaultdict(str,{'pos':feats[0],'token':feats[1],'lemma':feats[2],'msd':feats[3],'deprel':feats[5]}))
				known_nodes.add(feats[0])
			del sent[known_node]
	return tree

def merge_reflexive_verb(tree): # should be written better, overall tree index + tree recursion should not be mixed
	to_delete=[]
	for index in tree.nodes:
		if tree.nodes[index].data['msd']=='':
			continue
		if tree.nodes[index].data['msd'].startswith('Vm'):
			for child in tree.nodes[index].children:
				if child.data['deprel']=='Aux' and child.data['lemma']=='sebe':
					tree.nodes[index].data['lemma']=tree.nodes[index].data['lemma']+'_se'
					for index2 in tree.nodes:
						if tree.nodes[index2]==child:
							to_delete.append(index2)
					tree.nodes[index].children.remove(child)
					break
	for index in to_delete:
		del tree.nodes[index]
					
def hrwac_sent_trees(stream):
	sent=defaultdict(list)
	pos=0
	len_sent=0
	for line in stream:
		pos+=1
		if line=='\n':
			tree=Tree()
			tree=create_tree_from_sentence(sent)
			yield tree,pos-len_sent-1
			sent=defaultdict(list)
			len_sent=0
		else:
			feats=line[:-1].split('\t')
			feats[0]=int(feats[0])
			feats[4]=int(feats[4])
			sent[feats[4]].append(feats)
			len_sent+=1

def kres_sent_trees(stream):
	sent=defaultdict(list)
	i=0
	for line in stream:
		i+=1
		#if i%1000000==0:
		#	print i
		if line.startswith('\n'):
			tree=Tree()
			tree=create_tree_from_sentence(sent)
			yield tree
			sent=defaultdict(list)
		else:
			#if not line.startswith('<'):
			feats=line[:-1].split('\t')
			feats[0]=int(feats[0])
			feats[5]=int(feats[5])
			feats[6]=feats[6].split('-')[0]
			sent[feats[5]].append(feats[:3]+feats[4:])

def hrwac_tryouts():
	stSVO=Tree()
	stSVO.add_node(0,stSVO,lambda x:x.data['deprel']=='Pred' and x.data['msd'].startswith('Vm'))
	stSVO.add_node(1,0,lambda x:x.data['deprel']=='Sb' and re.match(r'Nc..n',x.data['msd'])!=None)
	stSVO.add_node(2,1,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('A') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5],optional=True)
	stSVO.add_node(3,0,lambda x:x.data['deprel']=='Obj'and re.match(r'Nc..a',x.data['msd'])!=None)
	stSVO.add_node(4,3,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('A') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5],optional=True)
	#stSVO.show()
	stRVO=Tree()
	stRVO.add_node(0,stRVO,lambda x:x.data['deprel']=='Pred')
	stRVO.add_node(1,0,lambda x:x.data['token']=='se' and x.data['deprel']=='Aux')
	stRVO.add_node(2,0,lambda x:x.data['deprel']=='Sb')
	stRVO.add_node(3,2,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('A') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5],optional=True)
	stRVO.add_node(4,2,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('A') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5],optional=True)
	stNP=Tree()
	stNP.add_node(0,stNP,lambda x:x.data['msd'].startswith('Nc'))
	stNP.add_node(1,0,lambda x:x.data['msd'].startswith('Ag') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5])
	stNPG=Tree()
	stNPG.add_node(0,stNPG,lambda x:x.data['msd'].startswith('Nc'))
	stNPG.add_node(1,0,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('A') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5],optional=True)
	stNPG.add_node(2,0,lambda x:x.data['deprel']=='Atr' and re.match(r'Nc..g',x.data['msd'])!=None)
	stNPG.add_node(3,2,lambda x:x.data['deprel']=='Atr' and re.match(r'A....g',x.data['msd'])!=None,optional=True)
	stNPPP=Tree()
	stNPPP.add_node(0,stNPPP,lambda x:x.data['msd'].startswith('Nc'))
	stNPPP.add_node(1,0,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('A') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5],optional=True)
	stNPPP.add_node(2,0,lambda x:x.data['deprel']=='Prep')
	stNPPP.add_node(3,2,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('Nc'))
	stNPPP.add_node(4,3,lambda x:x.data['deprel']=='Atr' and x.data['msd'].startswith('A') and x.data['msd'][3:6]==x.tree.nodes[x.parent].data['msd'][2:5],optional=True)
	stNPPP.add_node(5,3,lambda x:x.data['deprel']=='Atr' and re.match(r'Nc..g',x.data['msd'])!=None)
	stNPPP.add_node(6,5,lambda x:x.data['deprel']=='Atr' and re.match(r'A....g',x.data['msd'])!=None,optional=True)
	patterns=[stSVO]
	result=defaultdict(lambda: defaultdict(int))
	sent=defaultdict(list)
	i=0
	for tree in hrwac_sent_trees(open('temp')):#/home/nikola/hrwac/hrwac2.0.split.000.taglem.mate')):
		i+=1
		for index,pattern in enumerate(patterns):
			for subtree in tree.search_subtrees(pattern):
				#result[index][subtree.get_lemma()]+=1
				#print i,
				subtree.show_lemma()
				print
	#print sorted(result[0].items(),key=lambda x:-x[1])[:100]

def kres_tryouts():
	stSVO=Tree(search=True)
	stSVO.add_node(0,stSVO,lambda x:x.data.get('deprel','')=='modra')
	stSVO.add_node(1,0,lambda x:x.data.get('deprel','')=='ena-S_i')
	stSVO.add_node(2,0,lambda x:x.data.get('deprel','')=='dve-S_t')
	for tree in kres_sent_trees(open('/home/nikola/kres_parsed/kres.parsed_ske-out-stiri.txt')):
		#tree.show()
		for subtree in tree.search_subtrees(stSVO):
			print subtree.get_lemma()

if __name__=='__main__':
	hrwac_tryouts()
