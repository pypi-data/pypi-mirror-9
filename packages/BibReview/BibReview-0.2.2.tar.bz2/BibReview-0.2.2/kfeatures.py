# -*- coding: utf-8 -*-

# BibReview
# Copyright (C) 2013 Jean-Baptiste LAMY (jibalamy at free . fr)
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

import re
from collections import defaultdict

from nltk.corpus import wordnet


class Classifier(object):
  def __init__(self):
    self.class_nb = defaultdict(lambda : 0)
    self.nb       = 0
    
  def train   (self, reference, key, clazz): pass
  def classify(self, reference, key, adjusted = 1): pass
  
  def classify_accept_reject(self, reference, key, clazz, adjusted = 1, min_prob_for_rejection = 0.6):
    probas = self.classify(reference, key, adjusted)
    if not probas: probas = [[1, 0.0]]
    if probas[-1][0] == 0:
      pass
      #if probas[-1][1] < min_prob_for_rejection: probas = [[1, 0.0]]
      #if (len(probas) == 2) and (abs(probas[0][1] - probas[1][1]) < 0.1):
      #  print "delta faible", probas
      #  probas = [[1, 0.0]]
    reference.gold_class = clazz(reference)
    reference.pred_class = probas[-1][0]
    reference.pred_proba = probas[-1][1]
    return probas
  
  def train_and_test(self, references, key, clazz):
    self.prepare(references, key)
    conts = [[0, 0], [0, 0]]
    for reference in references:
      self.train(reference, key, clazz)
    for reference in references:
      probas = self.classify_accept_reject(reference, key, clazz)
      conts[reference.gold_class][reference.pred_class] += 1
      print reference.gold_class, reference.pred_class, probas, reference.gold_class == reference.pred_class
    print_conts(conts)
    
def print_conts(conts):
  print
  print conts[0][1] + conts[1][0], "erreurs"
  print "\tGOLD 0\tGOLD 1\tTOTAL"
  print "PRED 0\t%s\t%s\t%s" % (conts[0][0], conts[1][0], conts[0][0] + conts[1][0])
  print "PRED 1\t%s\t%s\t%s" % (conts[0][1], conts[1][1], conts[0][1] + conts[1][1])
  print "TOTAL\t%s\t%s\t%s" % (conts[0][0] + conts[0][1], conts[1][0] + conts[1][1], conts[0][0] + conts[0][1] + conts[1][0] + conts[1][1])
  
def leave_one_out(Classifier, references, key, clazz):
  classifier = Classifier()
  classifier.prepare(references, key)
  for reference in references:
    classifier.train(reference, key, clazz)
  conts = [[0, 0], [0, 0]]
  for leave in references:
    classifier.untrain(leave, key, clazz)
    probas = classifier.classify_accept_reject(leave, key, clazz)
    
    conts[leave.gold_class][leave.pred_class] += 1
    classifier.train(leave, key, clazz)
    
    if leave.gold_class != leave.pred_class:
      print
      print leave.gold_class, leave.pred_class, probas, leave.title
        
  print_conts(conts)

def all_subsets(s):
  l = [set()]
  for i in set(s):
    for subset in l[:]:
      if len(subset) < 5: l.append(subset | set([i]))
  return [frozenset(i) for i in l]
  
def _all_subsets(s):
  s = list(s)
  l = []
  for size in range(len(s)):
    size += 1
    for i in range(len(s) - size + 1):
      l.append(frozenset(s[i : i + size]))
  return l

class KFeaturesClassifier(Classifier):
  def __init__(self):
    Classifier.__init__(self)
    self.tokenizer = Tokenizer()
    self.pools     = defaultdict(lambda : defaultdict(lambda : []))
    
  def prepare(self, references, key): pass
  
  def train(self, reference, key, clazz):
    clazz_  = clazz(reference)
    pool    = self.pools[clazz_]
    words   = self.tokenizer.tokenize(key(reference))
    subsets = all_subsets(words)
    for subset in subsets:
      if subset: pool[subset].append(reference)
    self.class_nb[clazz_] += 1
    self.nb += 1
    
  def untrain(self, reference, key, clazz):
    clazz_  = clazz(reference)
    pool    = self.pools[clazz_]
    words   = self.tokenizer.tokenize(key(reference))
    subsets = all_subsets(words)
    for subset in subsets:
      if subset: pool[subset].remove(reference)
    self.class_nb[clazz_] -= 1
    self.nb -= 1
    
  def classify(self, reference, key, adjusted = 1):
    print
    
    words  = set(self.tokenizer.tokenize(key(reference)))
    subsets = all_subsets(words)
    nb_2_subsets = defaultdict(lambda : [])
    for subset in subsets:
      if subset: nb_2_subsets[len(subset)].append(subset)
      
    #nb0 = 0
    #nb1 = 0
    for i in range(len(nb_2_subsets), 0, -1):
      refs0 = set()
      refs1 = set()
      for subset in nb_2_subsets[i]:
        refs0.update(self.pools[0][subset])
        refs1.update(self.pools[1][subset])
      if refs0 or refs1:
        #nb0 += float(len(refs0))
        #nb1 += float(len(refs1))
        nb0 = float(len(refs0))
        nb1 = float(len(refs1))
        break
    #else: return [[0, 0.0, 0], [1, 0.0, 0]]
    print i
    #print subset, self.pools[0][subset], self.pools[1][subset]
    probas = [[0, nb0 / self.class_nb[0] * (self.nb / 2.0), nb0],
              [1, nb1 / self.class_nb[1] * (self.nb / 2.0), nb1]]
    probas.sort(key = lambda a: a[1])
    return probas
  
  
class Tokenizer:
  STOP_WORDS = set(u"""a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your""".split(u","))
  WORD_RE    = re.compile(u"\\w+", re.U)
  GROUP_RE   = re.compile(u",|:|\\?|!|\\b" + u"\\b|\\b".join(STOP_WORDS) + u"\\b", re.U)
  
  def __init__(self): pass
  
  def _tokenize(self, s):
    for match in self.WORD_RE.finditer(s.lower()):
      word = match.group()
      if (not word in self.STOP_WORDS) and (len(word) >= 3):
        yield word
        
  def tokenize(self, s):
    for match in self.WORD_RE.finditer(s.lower()):
      word = match.group()
      if (not word in self.STOP_WORDS) and (len(word) >= 3):
        token = wordnet.morphy(word)
        if token: yield token
        else:     yield word
                
tokenizer = Tokenizer()        
        
        
if __name__ == "__main__":
  import bibreview, bibreview.command_line
  
  base = bibreview.parse_bibreview.parse_bibreview_file("/home/jiba/zip/labo/yearbook/apprentissage/base_2012.xml")
  
  def title_key  (reference): return reference.title
  def title_class(reference):
    if reference.get_value_for_category(u"review") == -4: return 0
    else: return 1
    
  #tokenizer = Tokenizer()
  #f = open("/tmp/yearbook.arff", "w")
  #f.write("@RELATION yearbook\n\n")
  #f.write("@ATTRIBUTE title string\n")
  #f.write("@ATTRIBUTE class {rejected_on_title,accepted}\n\n")
  #f.write("@DATA\n")
  #for reference in base.references:
  #  title = u" ".join(tokenizer.tokenize(reference.title))
  #  f.write('"%s",%s\n' % (title.encode("utf8"), ["rejected_on_title", "accepted"][title_class(reference)]))
  #f.close()
  
  #classifier = c0 = KFeaturesClassifier()
  #classifier.train_and_test(base.references, title_key, title_class)
  leave_one_out(KFeaturesClassifier, base.references, title_key, title_class)
  
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

  
