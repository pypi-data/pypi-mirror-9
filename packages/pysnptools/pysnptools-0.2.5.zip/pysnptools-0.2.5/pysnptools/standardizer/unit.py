import numpy as np
import scipy as sp
import logging

class Unit(object):  #IStandardizer
    """Standardize data so that, for each snp, the mean of the values is zero with standard deviation 1.
    NaN values are then filled with zero, the mean (consequently, if there are NaN values, the final standard deviation will not be zero.
    """
    def __init__(self):
        pass

    def standardize(self, snps, blocksize=None, force_python_only=False):
        l = self._lambda_factory(snps, blocksize=blocksize, force_python_only=force_python_only)
        import pysnptools.standardizer as stdizer
        return stdizer._standardize_with_lambda(snps, l, blocksize)

    def __repr__(self): 
        return "{0}()".format(self.__class__.__name__)

    def _lambda_factory(self, snps, blocksize=None, force_python_only=False):
        from pysnptools.snpreader import wrap_plink_parser

        if not force_python_only:
            if snps.dtype == np.float64:
                if snps.flags['F_CONTIGUOUS'] and (snps.flags["OWNDATA"] or snps.base.nbytes == snps.nbytes):
                    #!!LATER: set snps to np.load(D:\Source\carlk_snpreader\tests\temp.npz.npz) and then run this. It fails without error. Could it be that standardizing twice, sometimes causes this?
                    return lambda s : wrap_plink_parser.standardizedoubleFAAA(s,False,float("NaN"),float("NaN"))
                elif snps.flags['C_CONTIGUOUS'] and (snps.flags["OWNDATA"] or snps.base.nbytes == snps.nbytes) and blocksize is None:
                    return lambda s : wrap_plink_parser.standardizedoubleCAAA(s,False,float("NaN"),float("NaN"))
                else:
                    logging.info("Array is not contiguous, so will standardize with python only instead of C++")
            elif snps.dtype == np.float32:
                if snps.flags['F_CONTIGUOUS'] and (snps.flags["OWNDATA"] or snps.base.nbytes == snps.nbytes):
                    return lambda s: wrap_plink_parser.standardizefloatFAAA(s,False,float("NaN"),float("NaN"))
                elif snps.flags['C_CONTIGUOUS'] and (snps.flags["OWNDATA"] or snps.base.nbytes == snps.nbytes) and blocksize is None:
                    return lambda s: wrap_plink_parser.standardizefloatCAAA(s,False,float("NaN"),float("NaN"))
                else:
                    logging.info("Array is not contiguous, so will standardize with python only instead of C++")
            else:
                logging.info("Array type is not float64 or float32, so will standardize with python only instead of C++")

        import pysnptools.standardizer as stdizer
        return lambda s: stdizer._standardize_unit_python(s)
