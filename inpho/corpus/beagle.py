'''
Module for running BEAGLE [Jones & Mewhort 2007]
'''
import pickle
import numpy
import sys

class RandomWordGen:
    def __init__(self, d = 1024, seed = None, *args):
        self.d = d
        self.start = numpy.random.randint(sys.maxint)

    def make_rep(self, word):
        numpy.random.seed(self.start ^ abs(hash(word)))
        return normalize(numpy.random.randn(self.d) * (self.d)**-0.5)

def normalize(a):
    '''
    Normalize a vector to length 1.
    '''
    norm2 = numpy.sum(a**2.0)
    if norm2 <= 0.0: return a
    return a / norm2**0.5

def cosine(a,b):
    '''
    Computes the cosine of the angle between the vectors a and b.
    '''
    sumSqA = numpy.sum(a**2.0)
    sumSqB = numpy.sum(b**2.0)
    if sumSqA == 0.0 or sumSqB == 0.0: return 0.0
    return numpy.dot(a,b) * (sumSqA * sumSqB)**-0.5

def read_graph(file):
    with open(file, 'r') as f:
        return pickle.load(f)


def build_env_vectors(words, dim):
    """
    Generate environmental vectors for all words in the corpus. (These
    are used to build the noun space.) Returns an association list of
    (word, environmental vector)
    """
    randvect = RandomWordGen(d=dim)
    
    env_vector = {}
    for word in words:
        env_vector[word] = randvect.make_rep(word)
    
    return env_vector

def build_memory_vectors(env_vectors, corpus):
    memory = env_vectors.copy()
    #initialize memory vector with own environment vector
    for sentence in corpus:
        for word in sentence:
            memory += sum([env[id] for id in sentence if id != word])            
            # add sentence vector

    return memory

