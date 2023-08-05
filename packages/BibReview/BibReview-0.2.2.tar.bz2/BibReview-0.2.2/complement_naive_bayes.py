# -*- coding: utf-8 -*-

# Weight-normalized Complement Naive Bayes classifier

# Copyright (C) 2013 Jean-Baptiste LAMY (jibalamy at free . fr)
# BibReview is developped by Jean-Baptiste LAMY, at LIM&BIO,
# UFR SMBH, Université Paris 13, Sorbonne Paris Cité.

# This algorithm is a Python translation of Weka's ComplementNaiveBayes :
# ComplementNaiveBayes.java
# Copyright (C) 2003 University of Waikato, Hamilton, New Zealand

# See also :
# Jason D. Rennie, Lawrence Shih, Jaime Teevan, David R. Karger:
# Tackling the Poor Assumptions of Naive Bayes Text Classifiers.
# In: ICML, 616-623, 2003.

 
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

import math
from collections import defaultdict

class Instance(object):
  def __init__(self, o, words, clazz):
    self.o      = o
    self.words  = set(words)
    self.clazz  = clazz
    
class Classifier(object):
  def __init__(self, words_func, class_func, classes = [0, 1], biases = None):
    self.words_func = words_func
    self.class_func = class_func
    self.classes    = classes
    self.biases     = biases
    
    # Weight of words for each class. The weight is actually the
    # log of the probability of a word (w) given a class (c) 
    # (i.e. log(Pr[w|c])). The format of the matrix is: 
    # word_weights[class][wordAttribute]
    self.word_weights = { clazz: defaultdict(lambda : 0.0) for clazz in self.classes }
    
    # Holds the smoothing value to avoid word probabilities of zero.
    # P.S.: According to the paper this is the Alpha i parameter
    self.smoothing_parameter = 1.0
    
    # True if the words weights are to be normalized
    self.normalize_word_weights = 0
    
  def train(self, objects):
    instances = [Instance(o, self.words_func(o), self.class_func(o)) for o in objects]
    self.all_words = set(word for instance in instances for word in instance.words)
    
    ocrnce_of_word_in_class  = { clazz: defaultdict(lambda : 0) for clazz in self.classes }
    num_words_per_class      = { clazz: 0                       for clazz in self.classes }
    num_words                = defaultdict(lambda : 0)
    total_word_occurrences   = 0
    sum_of_smoothing_params  = (len(self.all_words) - 1) * self.smoothing_parameter
    
    for instance in instances:
      for word in instance.words:
        num_words_per_class[instance.clazz]           += 1
        ocrnce_of_word_in_class[instance.clazz][word] += 1
        num_words[word]                               += 1
    total_word_occurrences = sum(num_words_per_class.values())
    
	  # Compute the complement class probability for all classes
    for clazz in self.classes:
      # total occurrence of words in classes other than c
      total_word_ocrnces = total_word_occurrences - num_words_per_class[clazz]
      
      for word in self.all_words:
        # occurrence of word in classes other that c
        ocrnces_of_word = num_words[word] - ocrnce_of_word_in_class[clazz][word]
        self.word_weights[clazz][word] = math.log(float(ocrnces_of_word + self.smoothing_parameter) / (total_word_ocrnces + sum_of_smoothing_params))
        
    # Normalize weights
    if self.normalize_word_weights:
      for clazz in self.classes:
        total = 0.0
        for word in self.all_words: total += abs(self.word_weights[clazz][word])
        for word in self.all_words: self.word_weights[clazz][word] /= total
        
  def classify_probs(self, object):
    words = set(self.words_func(object))
    values_for_class     = {}
    
    for clazz in self.classes:
      sum_of_word_values = 0
      for word in words: sum_of_word_values += self.word_weights[clazz][word]
      if self.biases: values_for_class[clazz] = sum_of_word_values * self.biases[clazz]
      else:           values_for_class[clazz] = sum_of_word_values
      
    return values_for_class
  
  def classify(self, object):
    value_for_class = self.classify_probs(object)
    
    best_value = float("+inf")
    best_class = None
    for clazz in value_for_class:
      if value_for_class[clazz] < best_value:
        best_value = value_for_class[clazz]
        best_class = clazz
        
    return best_class

        
