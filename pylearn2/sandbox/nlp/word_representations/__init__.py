from pylearn2.space import VectorSpace

class WordVectorSpace(VectorSpace):

    def __init__(self, vocabulary, vectors):
        assert vectors.ndim == 2
        self.vocabulary = vocabulary
        self.vectors = vectors
        super(self, WordVectorSpace).__init__(vectors.ndim)

