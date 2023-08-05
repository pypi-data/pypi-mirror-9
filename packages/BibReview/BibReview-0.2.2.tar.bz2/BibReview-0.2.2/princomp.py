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

# Thanks to R. Tagore !

from numpy import array, mean, cov, cumsum, dot, linalg, size, flipud, argsort

def princomp(A, numpc = 1):
  """ performs principal components analysis 
      (PCA) on the n-by-p data matrix A
      Rows of A correspond to observations, columns to variables. 

Returns :  
  coeff :
    is a p-by-p matrix, each column containing coefficients 
    for one principal component.
  score : 
    the principal component scores; that is, the representation 
    of A in the principal component space. Rows of SCORE 
    correspond to observations, columns to components.
  latent : 
    a vector containing the eigenvalues 
    of the covariance matrix of A.
"""
  # computing eigenvalues and eigenvectors of covariance matrix
  M = (A - mean(A.T, axis = 1)).T # subtract the mean (along columns)
  [latent, coeff] = linalg.eig(cov(M))
  p = size(coeff, axis = 1)
  idx = argsort(latent) # sorting the eigenvalues
  idx = idx[::-1]       # in ascending order
  # sorting eigenvectors according to the sorted eigenvalues
  coeff = coeff[:, idx]
  latent = latent[idx] # sorting eigenvalues
  if numpc < p or numpc >= 0: coeff = coeff[:, range(numpc)] # cutting some PCs
  score = dot(coeff.T, M) # projection of the data in the new space
  return coeff, score, latent


# A = array([ [2.4,0.7,2.9,2.2,3.0,2.7,1.6,1.1,1.6,0.9],
#             [2.5,0.5,2.2,1.9,3.1,2.3,2,1,1.5,1.1] ])

# coeff, score, latent = princomp(A.T)

# print coeff
# print score
# print latent

# from pylab import plot,subplot,axis,stem,show,figure
# figure()
# subplot(121)
# # every eigenvector describe the direction
# # of a principal component.
# m = mean(A,axis=1)
# plot([0, -coeff[0,0]*2]+m[0], [0, -coeff[0,1]*2]+m[1],'--k')
# plot([0, coeff[1,0]*2]+m[0], [0, coeff[1,1]*2]+m[1],'--k')
# plot(A[0,:],A[1,:],'ob') # the data
# axis('equal')
# subplot(122)
# # new data
# plot(score[0,:],score[1,:],'*g')
# axis('equal')
# show()

import re
from collections import Counter

#EMPTY_WORDS = set(["of", "the", "a", "an", "to", "from", "we"])

PUNCTUATION_REGEXP = re.compile(u"\\.|,|;|:|-|\\\"|'|\\(|\\)|/|\\*|\\+|%", re.UNICODE)

import os, os.path, bibreview.globdef as globdef

MESH_WORDS = set(open(os.path.join(globdef.DATADIR, "mshd2013.txt")).read().decode("latin").lower().split())
print "%s MeSH words" % len(MESH_WORDS)

def build_references_coords(references, all_words = None):
  wordss  = {}
  if all_words is None:
    compute_all_words = True
    all_words = set()
    all_words = Counter()
  else:
    compute_all_words = False
    
  for reference in references:
    text  = u" ".join([reference.title, reference.title, reference.abstract]).lower()
    text  = PUNCTUATION_REGEXP.sub(u" ", text)
    #words = [word for word in text.split() if (len(word) > 5) and not word in EMPTY_WORDS]
    words = [word for word in text.split() if (len(word) > 4) and (word in MESH_WORDS)]
    #words = [word for word in text.split() if (len(word) > 4)]
    if compute_all_words: all_words.update(set(words))
    wordss[reference] = Counter(words)

  if compute_all_words:
    all_words = [word for (word, nb) in all_words.most_common() if nb > 3]
    print len(all_words)
    #all_words = all_words[ max(0, len(all_words) - 200): ]
    #all_words = all_words[max(0, len(all_words) // 2 - 100) : len(all_words) // 2 + 100]
    all_words = all_words[ max(0, len(all_words) - 100): ] + all_words[max(0, len(all_words) // 2 - 50) : len(all_words) // 2 + 50]
    print all_words
    
    all_words = list(set(all_words))
    print len(all_words)
    
  word_2_coord = {}
  for word in all_words: word_2_coord[word] = len(word_2_coord)
  
  coordss = [ [float(wordss[reference][word]) for word in all_words] for reference in references]
  
  return coordss, all_words


def assign_lexical_proximity(references):
  coordss, all_words = build_references_coords(references)
  coordss = array(coordss)
  
  coeff, score, latent = princomp(coordss, 1)
  
  #print coeff
  #print score
  #print latent
  
  for i in range(len(references)):
    references[i].lexical_coord = score[0][i].real
  
