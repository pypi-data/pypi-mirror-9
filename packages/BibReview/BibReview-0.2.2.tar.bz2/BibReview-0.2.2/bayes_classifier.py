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

wordnet = None
def import_wordnet():
  global wordnet
  if not wordnet:
    try:
      from nltk.corpus import wordnet
    except ImportError:
      print "WARNING: NLTK Python module not found. This can reduce the performance of the Bayes classifier!"
      wordnet = None
      
import bibreview, bibreview.model
from bibreview.complement_naive_bayes import *

class Tokenizer:
  STOP_WORDS = set(u"""a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your""".split(u","))
  WORD_RE    = re.compile(u"\\w+", re.U)
  GROUP_RE   = re.compile(u",|:|\\?|!|\\b" + u"\\b|\\b".join(STOP_WORDS) + u"\\b", re.U)

  if wordnet:
    def tokenize(self, s):
      for match in self.WORD_RE.finditer(s.lower()):
        word = match.group()
        if (not word in self.STOP_WORDS) and (len(word) >= 3):
          token = wordnet.morphy(word)
          if token: yield token
          else:     yield word
          
  else:
    def tokenize(self, s):
      for match in self.WORD_RE.finditer(s.lower()):
        word = match.group()
        if (not word in self.STOP_WORDS) and (len(word) >= 3):
          yield word
        
tokenizer = Tokenizer()        



CLASSIFIER = None
def title_words(reference):
  return tokenizer.tokenize(reference.title)
  
def title_class(reference):
  if reference.get_value_for_category(u"review") == -4: return 0
  else: return 1
  
def bayes_train_on_title(base):
  global CLASSIFIER
  import_wordnet()
  CLASSIFIER = Classifier(title_words, title_class, [0, 1])
  CLASSIFIER.train(base.references)
  CLASSIFIER.class_2_category = { 0 : -4, 1 : 0 }
  return CLASSIFIER
  
  
def classify(base):
  global CLASSIFIER
  import_wordnet()
  for reference in base.references:
    clazz = CLASSIFIER.classify(reference)
    reference.set_value_for_category(u"review", CLASSIFIER.class_2_category[clazz], track = _("Bayes classifier"))
    
    
def print_conts(conts):
  print
  print conts[0][1] + conts[1][0], "erreurs"
  print "\tGOLD 0\tGOLD 1\tTOTAL"
  print "PRED 0\t%s\t%s\t%s" % (conts[0][0], conts[1][0], conts[0][0] + conts[1][0])
  print "PRED 1\t%s\t%s\t%s" % (conts[0][1], conts[1][1], conts[0][1] + conts[1][1])
  print "TOTAL\t%s\t%s\t%s" % (conts[0][0] + conts[0][1], conts[1][0] + conts[1][1], conts[0][0] + conts[0][1] + conts[1][0] + conts[1][1])

def bayes_leave_one_out(base, get_words, get_class):
  conts = [[0, 0], [0, 0]]
  for leave in base.references:
    classifier = Classifier(get_words, get_class, [0, 1])
    training_set = list(base.references)
    training_set.remove(leave)
    classifier.train(training_set)
    
    leave.gold_class = get_class(leave)
    leave.pred_class = classifier.classify(leave)
    
    conts[leave.gold_class][leave.pred_class] += 1
    
    if leave.gold_class != leave.pred_class:
      probas = classifier.classify_probs(leave)
      
      print leave.gold_class, leave.pred_class, probas, leave.get_value_for_category(u"review"), leave.title
      
  print_conts(conts)

def bayes_leave_one_out_on_title(base):
  import_wordnet()
  return bayes_leave_one_out(base, title_words, title_class)

bibreview.model.COMMAND_LINE_FUNCS["--bayes-train-on-titles"]         = bayes_train_on_title
bibreview.model.COMMAND_LINE_FUNCS["--bayes-leave-one-out-on-titles"] = bayes_leave_one_out_on_title
bibreview.model.COMMAND_LINE_FUNCS["--classify"]                      = classify
