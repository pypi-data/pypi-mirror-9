# -*- coding: utf-8 -*-

# BibReview
# Copyright (C) 2012 Jean-Baptiste LAMY (jibalamy at free . fr)
# BibReview is developped by Jean-Baptiste LAMY, at LIM&BIO,
# UFR SMBH, Université Paris 13, Sorbonne Paris Cité.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# python ./bibreview/bibreview --query-pubmed '("Journal of environmental management"[Journal] OR "Medical decision making : an international journal of the Society for Medical Decision Making"[Journal] OR "Expert systems with applications"[Journal] OR "Artificial intelligence in medicine"[Journal] OR "Computer methods and programs in biomedicine"[Journal] OR "Patient education and counseling"[Journal] OR "Journal of biomedical informatics"[Journal] OR "Bmc Medical Informatics And Decision Making"[Journal] OR "International journal of medical informatics"[Journal] OR "Journal of medical systems"[Journal] OR "J Am Med Inform Assoc"[Journal]) AND ("2012/01/01"[Date - Publication] : "2012/12/31"[Date - Publication] NOT pubstatusaheadofprint) AND ("english"[Language]) AND ("journal article"[Publication Type])' --save-as /home/jiba/zip/labo/yearbook/apprentissage/info_med_2012.xml
# python ./bibreview/bibreview --substract /home/jiba/zip/labo/yearbook/apprentissage/info_med_2012.xml /home/jiba/zip/labo/yearbook/apprentissage/base_2012.xml --set-review-status CURRENT -4 --save-as /home/jiba/zip/labo/yearbook/apprentissage/info_med_2012_hors_sad.xml

# python ./bibreview/bibreview --query-pubmed '("decision support"[Title/Abstract]) AND ("Medical decision making : an international journal of the Society for Medical Decision Making"[Journal] OR "Expert systems with applications"[Journal] OR "Artificial intelligence in medicine"[Journal] OR "Computer methods and programs in biomedicine"[Journal] OR "Patient education and counseling"[Journal] OR "Journal of biomedical informatics"[Journal] OR "Bmc Medical Informatics And Decision Making"[Journal] OR "International journal of medical informatics"[Journal] OR "Journal of medical systems"[Journal] OR "J Am Med Inform Assoc"[Journal]) AND ("1995/01/01"[Date - Publication] : "2011/12/31"[Date - Publication] NOT pubstatusaheadofprint) AND ("english"[Language]) AND ("journal article"[Publication Type])' --save-as /home/jiba/zip/labo/yearbook/apprentissage/sad_1995-2011.xml

import re
from collections import defaultdict

from nltk.corpus import wordnet

from bibreview.complement_naive_bayes import *


def print_conts(conts):
  print
  print conts[0][1] + conts[1][0], "erreurs"
  print "\tGOLD 0\tGOLD 1\tTOTAL"
  print "PRED 0\t%s\t%s\t%s" % (conts[0][0], conts[1][0], conts[0][0] + conts[1][0])
  print "PRED 1\t%s\t%s\t%s" % (conts[0][1], conts[1][1], conts[0][1] + conts[1][1])
  print "TOTAL\t%s\t%s\t%s" % (conts[0][0] + conts[0][1], conts[1][0] + conts[1][1], conts[0][0] + conts[0][1] + conts[1][0] + conts[1][1])

def test(classifier, references):
  conts = [[0, 0], [0, 0]]
  for reference in references:
    reference.gold_class = classifier.class_func(reference)
    reference.pred_class = classifier.classify  (reference)
    probas               = classifier.classify_probs(reference)
    conts[reference.gold_class][reference.pred_class] += 1
    print reference.gold_class, reference.pred_class, probas, reference.gold_class == reference.pred_class
  print_conts(conts)
  
  
def leave_one_out(references, key, clazz, biases = None, additional_training = []):
  conts = [[0, 0], [0, 0]]
  for leave in references:
    c = Classifier(key, clazz, [0, 1], biases)
    training_set = list(references) + additional_training
    training_set.remove(leave)
    c.train(training_set)
    
    leave.gold_class = clazz(leave)
    leave.pred_class = c.classify(leave)
    
    conts[leave.gold_class][leave.pred_class] += 1
    
    if leave.gold_class != leave.pred_class:
      probas = c.classify_probs(leave)

      if leave.gold_class == 1:
        print
        print leave.gold_class, leave.pred_class, probas, leave.get_value_for_category(u"review"), leave.title
      
  print_conts(conts)
  
"""

311 erreurs # sans lemmatisation
	GOLD 0	GOLD 1	TOTAL
PRED 0	503	81	584
PRED 1	230	266	496
TOTAL	733	347	1080


317 erreurs # morphy
	GOLD 0	GOLD 1	TOTAL
PRED 0	498	82	580
PRED 1	235	265	500
TOTAL	733	347	1080


263 erreurs # synset
	GOLD 0	GOLD 1	TOTAL
PRED 0	564	94	658
PRED 1	169	253	422
TOTAL	733	347	1080


261 erreurs # sans lemmatisation, avec paire et triplet
	GOLD 0	GOLD 1	TOTAL
PRED 0	560	88	648
PRED 1	173	259	432
TOTAL	733	347	1080


264 erreurs # sans lemmatisation, avec paire
	GOLD 0	GOLD 1	TOTAL
PRED 0	549	80	629
PRED 1	184	267	451
TOTAL	733	347	1080

260 erreurs # morphy, avec paire
	GOLD 0	GOLD 1	TOTAL
PRED 0	554	81	635
PRED 1	179	266	445
TOTAL	733	347	1080

239 erreurs # synset, avec paire               <----------------------------------
	GOLD 0	GOLD 1	TOTAL
PRED 0	573	79	652
PRED 1	160	268	428
TOTAL	733	347	1080

239 erreurs # synset, tous les couples
	GOLD 0	GOLD 1	TOTAL
PRED 0	576	82	658
PRED 1	157	265	422
TOTAL	733	347	1080

"""

class Tokenizer:
  STOP_WORDS = set(u"""a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your""".split(u","))
  WORD_RE    = re.compile(u"\\w+", re.U)
  GROUP_RE   = re.compile(u",|:|\\?|!|\\b" + u"\\b|\\b".join(STOP_WORDS) + u"\\b", re.U)
  
  def __init__(self):
    self.token_limit = None
  
  def _tokenize(self, s):
    for match in self.WORD_RE.finditer(s.lower()):
      word = match.group()
      if (not word in self.STOP_WORDS) and (len(word) >= 3):
        yield word
        
  def _tokenize(self, s):
    for match in self.WORD_RE.finditer(s.lower()):
      word = match.group()
      if (not word in self.STOP_WORDS) and (len(word) >= 3):
        token = wordnet.morphy(word)
        if token: yield token
        else:     yield word
        
  def _tokenize(self, s):
    for match in self.WORD_RE.finditer(s.lower()):
      word = match.group()
      if (not word in self.STOP_WORDS) and (len(word) >= 3):
        synsets = wordnet.synsets(word)
        if synsets:
          for syn in sorted(set(i.name.split(".")[0] for i in synsets)):
            yield syn
            
        else: yield word
        
  def _tokenize(self, s):
    for group in self.GROUP_RE.split(s.lower()):
      words = [word for word in self.WORD_RE.findall(group)]
      for word in words: yield word
      size = 2
      while len(words) >= size:
        for i in range(len(words) - size + 1):
          yield u"_".join(words[i : i + size])
        size += 1
        if size > 2: break
        
  def _tokenize(self, s):
    for group in self.GROUP_RE.split(s.lower()):
      words = [word for word in self.WORD_RE.findall(group)]
      words = [wordnet.morphy(word) or word for word in words]
      for word in words:
        yield word
      size = 2
      while len(words) >= size:
        for i in range(len(words) - size + 1):
          yield u" ".join(words[i : i + size])
        size += 1
        if size > 2: break
        
  def _tokenize(self, s):
    def get_syn(w):
      synsets = wordnet.synsets(w)
      if not synsets: return w
      return sorted(synsets)[0].name.split(".")[0]
    
    for group in self.GROUP_RE.split(s.lower()):
      words = [word for word in self.WORD_RE.findall(group)]
      words = [get_syn(word) or word for word in words]
      for word in words:
        yield word
      size = 2
      while len(words) >= size:
        for i in range(len(words) - size + 1):
          yield u" ".join(words[i : i + size])
        size += 1
        if size > 2: break


        
  def tokenize(self, s):
    def get_syn(w):
      synsets = wordnet.synsets(w)
      if not synsets: return w
      return sorted(synsets)[0].name.split(".")[0]
    
    for group in self.GROUP_RE.split(s.lower()):
      words = [word for word in self.WORD_RE.findall(group)]
      words = [get_syn(word) or word for word in words]
      for word in words:
        yield word
      for w1 in words:
        for w2 in words:
          if w1 != w2:
            yield u"%s %s" %(w1, w2)
            
tokenizer = Tokenizer()
        
if __name__ == "__main__":
  import bibreview, bibreview.command_line
  
  #base          = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/base_2012.xml")
  base          = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/base_2012_w.xml")
  base_negative = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/info_med_2012_hors_sad.xml")
  base_positive = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/sad_1995-2011.xml")
  
  base_abstract = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/base_2012_abstract.xml")
  
  def title_key  (reference):
    return tokenizer.tokenize(reference.title)
  
  def title_class(reference):
    if reference._base is base_negative: return 0
    if reference._base is base_positive: return 1
    
    if reference.get_value_for_category(u"review") == -4: return 0
    else: return 1
    
  def abstract_key  (reference):
    return tokenizer.tokenize(reference.abstract)
  
  def abstract_class(reference):
    if reference.get_value_for_category(u"review") == -3: return 0
    else: return 1
  
  #references += base_negative.references[:266]



  #leave_one_out(base.references, title_key, title_class, biases = { 0 : 1.0, 1 : 0.98 }, additional_training = base_positive.references)
  
  leave_one_out(base.references, title_key, title_class, biases = { 0 : 1.0, 1 : 1.0 })
  
  #leave_one_out(base_abstract.references, abstract_key, abstract_class, biases = { 0 : 1.0, 1 : 1.0 })
  
  #c0 = Classifier(title_key, title_class, [0, 1])
  #for reference in base_negative.references: c0.train(reference, title_key, title_class)
  #for reference in base_positive.references: c0.train(reference, title_key, title_class)
  #c0.train(references)
  #test(c0, references)
  #c0.train_and_test(refs_abstract, abstract_key, abstract_class)
