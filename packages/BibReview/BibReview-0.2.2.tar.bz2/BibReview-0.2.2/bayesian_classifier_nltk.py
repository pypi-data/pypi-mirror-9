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

import re
from collections import defaultdict

import nltk
from nltk.corpus import wordnet
from nltk.probability import *

class Classifier(object):
  def __init__(self):
    self.class_nb = defaultdict(lambda : 0)
    self.nb       = 0
    
  def train   (self, reference, key, clazz): pass
  def classify(self, reference, key, adjusted = 1): pass
  
  def classify_accept_reject(self, reference, key, clazz, adjusted = 1, min_prob_for_rejection = 0.6):
    clazz_ = self.classify(reference, key, adjusted)
    reference.gold_class = clazz(reference)
    reference.pred_class = clazz_
    return clazz_
  
  def test(self, references, key, clazz):
    conts = [[0, 0], [0, 0]]
    for reference in references:
      probas = self.classify_accept_reject(reference, key, clazz)
      conts[reference.gold_class][reference.pred_class] += 1
      print reference.gold_class, reference.pred_class, reference.gold_class == reference.pred_class
    print_conts(conts)
    
def print_conts(conts):
  print
  print conts[0][1] + conts[1][0], "erreurs"
  print "\tGOLD 0\tGOLD 1\tTOTAL"
  print "PRED 0\t%s\t%s\t%s" % (conts[0][0], conts[1][0], conts[0][0] + conts[1][0])
  print "PRED 1\t%s\t%s\t%s" % (conts[0][1], conts[1][1], conts[0][1] + conts[1][1])
  print "TOTAL\t%s\t%s\t%s" % (conts[0][0] + conts[0][1], conts[1][0] + conts[1][1], conts[0][0] + conts[0][1] + conts[1][0] + conts[1][1])
  
def leave_one_out(Classifier, references, key, clazz, additional_trainings = []):
  conts = [[0, 0], [0, 0]]
  for leave in references:
    rs = list(references)
    rs.remove(leave)
    classifier = Classifier()
    classifier.train(rs + additional_trainings, key, clazz)
    clazz_ = classifier.classify_accept_reject(leave, key, clazz)
    #print leave.gold_class, leave.pred_class, probas, leave.title
    
    conts[leave.gold_class][leave.pred_class] += 1
    
    if leave.gold_class != leave.pred_class:
      print
      print leave.gold_class, leave.pred_class, leave.title
      
        
  print_conts(conts)
    
class BayesClassifier(Classifier):
  def __init__(self, estimator = ELEProbDist):
    Classifier.__init__(self)
    self.estimator = estimator
    
  def train(self, references, key, clazz):
    self.classifier = nltk.NaiveBayesClassifier.train([(key(reference), clazz(reference)) for reference in references], self.estimator)
    
  def classify(self, reference, key, adjusted = 1):
    return self.classifier.classify(key(reference))
  

def calc_proba(proba0, proba1):
  #proba_les_2 = proba0 * proba1
  #proba_aucun = (1 - proba0) * (1 - proba1)
  return proba0 * (1.0 - proba1), proba1 * (1.0 - proba0)

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
      size = 2
      while len(words) >= size:
        for i in range(len(words) - size + 1):
          yield u" ".join(words[i : i + size])
        size += 1
        if size > 3: break
        
tokenizer = Tokenizer()        
        
        
if __name__ == "__main__":
  import bibreview, bibreview.command_line
  
  base          = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/base_2012.xml")
  base_negative = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/info_med_2012_hors_sad.xml")
  base_positive = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/sad_1995-2011.xml")
  
  def title_key  (reference):
    features = defaultdict(lambda : 0)
    #for word in tokenizer.tokenize(reference.title):
    for word in tokenizer.tokenize(reference.abstract):
      features[word] += 1
    return features
  
  def title_class(reference):
    if reference.get_value_for_category(u"review") == -3: return 0
    else: return 1
    
  refs_abstract = [r for r in base.references if r.get_value_for_category(u"review") != -4]
  
  #c0 = BayesClassifier()
  #c0.train(refs_abstract, title_key, title_class)
  #c0.train(base.references + base_negative.references + base_positive.references, title_key, title_class)
  #c0.test (refs_abstract, title_key, title_class)

  #c1 = BayesClassifier()
  #leave_one_out(BayesClassifier, base.references, title_key, title_class, base_negative.references + base_positive.references)
  #leave_one_out(BayesClassifier, refs_abstract, title_key, title_class)
  
  import random
  random.shuffle(refs_abstract)
  c0 = BayesClassifier()
  c0.train(refs_abstract[:500], title_key, title_class)
  c0.test (refs_abstract[500:], title_key, title_class)
  
  
  # classifier = c1 = Bayes()
  # nb  = len(base.references)
  # nb0 = len([reference for reference in base.references if title_class(reference) == 0])
  # nb1 = nb - nb0
  # conts = [[0, 0], [0, 0]]
  # mults = [1.0 / nb0 * (nb / 2.0), 1.0 / nb1 * (nb / 2.0)]
  # print nb, nb0, nb1, mults

  # for reference in base.references:
  #   classifier.train(title_class(reference), title_key(reference).lower())
    
  # for reference in base.references:
  #   probas = classifier.guess(title_key(reference).lower())
  #   probas2 = []
  #   for clazz, proba in probas: probas2.append((clazz, proba * mults[clazz]))
  #   probas2.sort(key = lambda a: a[1])
    
  #   #probas = probas2 = classifier.classify_accept_reject(reference, title_key, title_class)
  #   reference.gold_clazz = title_class(reference)
  #   reference.pred_clazz = probas2[-1][0]
  #   reference.pred_proba = probas2[-1][1]

  #   if (reference.pred_proba < 0.6) and (reference.pred_clazz == 0):
  #     reference.pred_clazz = 1
  #     reference.pred_proba = 0.0
      
    
  #   conts[reference.gold_clazz][reference.pred_clazz] += 1
  #   print probas, probas2, reference.gold_clazz == reference.pred_clazz

  # print
  # print conts[0][1] + conts[1][0], "erreurs"
  # print "\tGOLD 0\tGOLD 1\tTOTAL"
  # print "PRED 0\t%s\t%s\t%s" % (conts[0][0], conts[1][0], conts[0][0] + conts[1][0])
  # print "PRED 1\t%s\t%s\t%s" % (conts[0][1], conts[1][1], conts[0][1] + conts[1][1])
  # print "TOTAL\t%s\t%s\t%s" % (conts[0][0] + conts[0][1], conts[1][0] + conts[1][1], nb)

  
