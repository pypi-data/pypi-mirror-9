import numpy as np

class DiagKtoN(object):
    """diag(K)=N standardization of the data"""
    def __init__(self, N):
        self._N = N

    def standardize(self, snps, blocksize=None, force_python_only=False):
        flag = snps.flags.writeable
        vec = snps.reshape(-1, order="A")
        
        # make sure no copy was made
        assert vec.base is snps
        squared_sum = vec.dot(vec)
        factor = 1./np.sqrt(squared_sum / float(self._N))
        
        snps.flags.writeable = flag
        
        snps *= factor
        
        return snps

    def __repr__(self): 
            return "{0}()".format(self.__class__.__name__)
