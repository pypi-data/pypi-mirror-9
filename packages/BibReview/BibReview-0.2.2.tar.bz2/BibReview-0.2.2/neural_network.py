
# Back-Propagation Neural Networks (bpnn.py)
# 
# Written in Python.  See http://www.python.org/
# This part was placed in the public domain, and written by
# Neil Schemenauer <nas@arctrix.com>
# Copyright (C) Neil Schemenauer for Back-Propagation Neural Networks implementation

import math
import random
import string

random.seed(0)

# calculate a random number where:  a <= rand < b
def rand(a, b):
  return (b-a)*random.random() + a

# Make a matrix (we could use NumPy to speed this up)
def makeMatrix(I, J, fill=0.0):
  m = []
  for i in range(I):
    m.append([fill]*J)
  return m

# our sigmoid function, tanh is a little nicer than the standard 1/(1+e^-x)
sigmoid = math.tanh

# derivative of our sigmoid function, in terms of the output (i.e. y)
def dsigmoid(y): return 1.0 - (y * y)

class NN:
  def __init__(self, ni, nh, no):
    # number of input, hidden, and output nodes
    self.ni = ni + 1 # +1 for bias node
    self.nh = nh
    self.no = no
    
    # activations for nodes
    self.ai = [1.0]*self.ni
    self.ah = [1.0]*self.nh
    self.ao = [1.0]*self.no
    
    # create weights
    self.wi = makeMatrix(self.ni, self.nh)
    self.wo = makeMatrix(self.nh, self.no)
    # set them to random values
    for i in range(self.ni):
      for j in range(self.nh):
        self.wi[i][j] = rand(-0.2, 0.2)
    for j in range(self.nh):
      for k in range(self.no):
        self.wo[j][k] = rand(-2.0, 2.0)

    # last change in weights for momentum   
    self.ci = makeMatrix(self.ni, self.nh)
    self.co = makeMatrix(self.nh, self.no)

  def update(self, inputs):
    #if len(inputs) != self.ni-1:
    #  raise ValueError, 'wrong number of inputs'

    #self.ai = inputs
    # input activations
    for i in range(self.ni-1): self.ai[i] = inputs[i]
      
    # hidden activations
      #for j in range(self.nh):
        #sum_ = 0.0
        #for i in range(self.ni):
        #  sum_ = sum_ + self.ai[i] * self.wi[i][j]
        #self.ah[j] = sigmoid(sum_)
        
        #self.ah[j] = sigmoid(sum(self.ai[i] * self.wi[i][j] for i in range(self.ni)))
    self.ah = [sigmoid(sum(self.ai[i] * self.wi[i][j] for i in range(self.ni))) for j in range(self.nh)]
        
    # output activations
    #for k in range(self.no):
      #sum_ = 0.0
      #for j in range(self.nh):
      #  sum_ = sum_ + self.ah[j] * self.wo[j][k]
      #self.ao[k] = sigmoid(sum_)
      
      #self.ao[k] = sigmoid(sum(self.ah[j] * self.wo[j][k] for j in range(self.nh)))
    
    self.ao = [sigmoid(sum(self.ah[j] * self.wo[j][k] for j in range(self.nh))) for k in range(self.no)]
    return self.ao
  
  def backPropagate(self, targets, N, M):
    #if len(targets) != self.no:
    #  raise ValueError, 'wrong number of target values'
    
    # calculate error terms for output
    output_deltas = [0.0] * self.no
    for k in range(self.no):
      error = targets[k]-self.ao[k]
      output_deltas[k] = dsigmoid(self.ao[k]) * error

    # calculate error terms for hidden
    hidden_deltas = [0.0] * self.nh
    for j in range(self.nh):
      error = 0.0
      for k in range(self.no):
        error = error + output_deltas[k]*self.wo[j][k]
      hidden_deltas[j] = dsigmoid(self.ah[j]) * error

    # update output weights
    for j in range(self.nh):
      for k in range(self.no):
        change = output_deltas[k]*self.ah[j]
        self.wo[j][k] = self.wo[j][k] + N*change + M*self.co[j][k]
        self.co[j][k] = change
        #print N*change, M*self.co[j][k]

    # update input weights
    for i in range(self.ni):
      for j in range(self.nh):
        change = hidden_deltas[j]*self.ai[i]
        self.wi[i][j] = self.wi[i][j] + N*change + M*self.ci[i][j]
        self.ci[i][j] = change
        
    # calculate error
    error = 0.0
    for k in range(len(targets)):
      error = error + 0.5*(targets[k]-self.ao[k])**2
    return error

  def test(self, patterns):
    for p in patterns:
      print p[0], '->', self.update(p[0])
      
  def weights(self):
    print 'Input weights:'
    for i in range(self.ni):
      print self.wi[i]
    print
    print 'Output weights:'
    for j in range(self.nh):
      print self.wo[j]

  def train(self, patterns, iterations=1000, N=0.5, M=0.1):
    # N: learning rate
    # M: momentum factor
    for i in xrange(iterations):
      error = 0.0
      for inputs, targets in patterns:
        self.update(inputs)
        error += self.backPropagate(targets, N, M)
      #if i % 100 == 0:
      print 'Iteration %s : error %-14f' % (i, error)
    return error

# End of Back-Propagation Neural Networks (bpnn.py)

NEURAL_NETWORK = None



#from bibreview.princomp import build_references_coords

def train_neural_network(references, nb = 100):
  global NEURAL_NETWORK
  
  coordss, all_words = build_references_coords(references)
  
  NEURAL_NETWORK = NN(len(all_words), 3, 1)
  NEURAL_NETWORK.all_words = all_words
  
  patterns = []
  for i in range(len(references)):
    review_status = float(references[i].get_value_for_category(u"review") or 0.0)
    patterns.append((coordss[i], [review_status]))
    
  NEURAL_NETWORK.train(patterns, iterations = 100)
  
  
def classify_with_neural_network(references):
  global NEURAL_NETWORK
  
  coordss, all_words = build_references_coords(references, all_words = NEURAL_NETWORK.all_words)
  
  for i in range(len(references)):
    references[i].neural_score = NEURAL_NETWORK.update(coordss[i])[0]
    
