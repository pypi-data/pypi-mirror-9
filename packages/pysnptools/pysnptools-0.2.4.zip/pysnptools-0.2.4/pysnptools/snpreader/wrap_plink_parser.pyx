import numpy as np 


cimport numpy as np
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool

cdef extern from "./CPlinkBedFile.h":
	
	void _readPlinkBedFilefloatFAAA "readPlinkBedFilefloatFAAA"(string bed_fn, int input_num_ind, int input_num_snps, vector[size_t] iid_idx_list, vector[int] sid_idx_list, float* out)
	void _readPlinkBedFiledoubleFAAA "readPlinkBedFiledoubleFAAA"(string bed_fn, int input_num_ind, int input_num_snps, vector[size_t] iid_idx_list, vector[int] sid_idx_list, double* out)
	void _readPlinkBedFilefloatCAAA "readPlinkBedFilefloatCAAA"(string bed_fn, int input_num_ind, int input_num_snps, vector[size_t] iid_idx_list, vector[int] sid_idx_list, float* out)
	void _readPlinkBedFiledoubleCAAA "readPlinkBedFiledoubleCAAA"(string bed_fn, int input_num_ind, int input_num_snps, vector[size_t] iid_idx_list, vector[int] sid_idx_list, double* out)

	void _writePlinkBedFilefloatFAAA "writePlinkBedFilefloatFAAA"(string bed_fn, int input_num_ind, int input_num_snps, float* inx)
	void _writePlinkBedFiledoubleFAAA "writePlinkBedFiledoubleFAAA"(string bed_fn, int input_num_ind, int input_num_snps, double* inx)
	void _writePlinkBedFilefloatCAAA "writePlinkBedFilefloatCAAA"(string bed_fn, int input_num_ind, int input_num_snps, float* inx)
	void _writePlinkBedFiledoubleCAAA "writePlinkBedFiledoubleCAAA"(string bed_fn, int input_num_ind, int input_num_snps, double* inx)


	void _ImputeAndZeroMeanSNPsfloatFAAA "ImputeAndZeroMeanSNPsfloatFAAA"( 
		float *SNPs,
		size_t nIndividuals,
		size_t nSNPs,
		const bool betaNotUnitVariance,
		const float betaA,
		const float betaB
		)
	void _ImputeAndZeroMeanSNPsdoubleFAAA "ImputeAndZeroMeanSNPsdoubleFAAA"( 
		double *SNPs,
		size_t nIndividuals,
		size_t nSNPs,
		const bool betaNotUnitVariance,
		const double betaA,
		const double betaB
		)
	void _ImputeAndZeroMeanSNPsfloatCAAA "ImputeAndZeroMeanSNPsfloatCAAA"( 
		float *SNPs,
		size_t nIndividuals,
		size_t nSNPs,
		bool betaNotUnitVariance,
		float betaA,
		float betaB
		)

	void _ImputeAndZeroMeanSNPsdoubleCAAA "ImputeAndZeroMeanSNPsdoubleCAAA"( 
		double *SNPs,
		size_t nIndividuals,
		size_t nSNPs,
		const bool betaNotUnitVariance,
		const double betaA,
		const double betaB
		)


def standardizefloatFAAA(np.ndarray[np.float32_t, ndim=2] out, bool betaNotUnitVariance, float betaA, float betaB):
	
	num_ind = out.shape[0]
	num_snps = out.shape[1]

	#http://wiki.cython.org/tutorials/NumpyPointerToC
	_ImputeAndZeroMeanSNPsfloatFAAA(<float*> out.data, num_ind, num_snps, betaNotUnitVariance, betaA, betaB)

	return out



def standardizedoubleFAAA(np.ndarray[np.float64_t, ndim=2] out, bool betaNotUnitVariance, double betaA, double betaB):
	
	num_ind = out.shape[0]
	num_snps = out.shape[1]

	#http://wiki.cython.org/tutorials/NumpyPointerToC
	_ImputeAndZeroMeanSNPsdoubleFAAA(<double*> out.data, num_ind, num_snps, betaNotUnitVariance, betaA, betaB)

	return out



def standardizefloatCAAA(np.ndarray[np.float32_t, ndim=2] out, bool betaNotUnitVariance, float betaA, float betaB):
	
	num_ind = out.shape[0]
	num_snps = out.shape[1]

	#http://wiki.cython.org/tutorials/NumpyPointerToC
	_ImputeAndZeroMeanSNPsfloatCAAA(<float*> out.data, num_ind, num_snps, betaNotUnitVariance, betaA, betaB)

	return out

def standardizedoubleCAAA(np.ndarray[np.float64_t, ndim=2] out, bool betaNotUnitVariance, double betaA, double betaB):
	
	num_ind = out.shape[0]
	num_snps = out.shape[1]

	#http://wiki.cython.org/tutorials/NumpyPointerToC
	_ImputeAndZeroMeanSNPsdoubleCAAA(<double*> out.data, num_ind, num_snps, betaNotUnitVariance, betaA, betaB)

	return out


def readPlinkBedFilefloatFAAA(bed_fn, input_num_ind, input_num_snps, iidIdxList, snpIdxList, np.ndarray[np.float32_t, ndim=2] out):
	
	cdef vector[size_t] iid_idx_list = iidIdxList
	cdef vector[int] sid_idx_list = snpIdxList
	#http://wiki.cython.org/tutorials/NumpyPointerToC

	_readPlinkBedFilefloatFAAA(bed_fn, input_num_ind, input_num_snps, iid_idx_list, sid_idx_list, <float*> out.data)
	return out

def readPlinkBedFilefloatCAAA(bed_fn, input_num_ind, input_num_snps, iidIdxList, snpIdxList, np.ndarray[np.float32_t, ndim=2] out):
	
	cdef vector[size_t] iid_idx_list = iidIdxList
	cdef vector[int] sid_idx_list = snpIdxList
	#http://wiki.cython.org/tutorials/NumpyPointerToC

	_readPlinkBedFilefloatCAAA(bed_fn, input_num_ind, input_num_snps, iid_idx_list, sid_idx_list, <float*> out.data)
	return out


def readPlinkBedFiledoubleFAAA(bed_fn, input_num_ind, input_num_snps, iidIdxList, snpIdxList, np.ndarray[np.float64_t, ndim=2] out):
	
	cdef vector[size_t] iid_idx_list = iidIdxList
	cdef vector[int] sid_idx_list = snpIdxList
	#http://wiki.cython.org/tutorials/NumpyPointerToC

	_readPlinkBedFiledoubleFAAA(bed_fn, input_num_ind, input_num_snps, iid_idx_list, sid_idx_list, <double*> out.data)
	return out

def readPlinkBedFiledoubleCAAA(bed_fn, input_num_ind, input_num_snps, iidIdxList, snpIdxList, np.ndarray[np.float64_t, ndim=2] out):
	
	cdef vector[size_t] iid_idx_list = iidIdxList
	cdef vector[int] sid_idx_list = snpIdxList
	#http://wiki.cython.org/tutorials/NumpyPointerToC

	_readPlinkBedFiledoubleCAAA(bed_fn, input_num_ind, input_num_snps, iid_idx_list, sid_idx_list, <double*> out.data)
	return out


def writePlinkBedFilefloatFAAA(bed_fn, input_num_ind, input_num_snps, np.ndarray[np.float32_t, ndim=2] inx):
	_writePlinkBedFilefloatFAAA(bed_fn, input_num_ind, input_num_snps, <float*> inx.data)

def writePlinkBedFilefloatCAAA(bed_fn, input_num_ind, input_num_snps, np.ndarray[np.float32_t, ndim=2] inx):
	_writePlinkBedFilefloatCAAA(bed_fn, input_num_ind, input_num_snps, <float*> inx.data)

def writePlinkBedFiledoubleFAAA(bed_fn, input_num_ind, input_num_snps, np.ndarray[np.float64_t, ndim=2] inx):
	_writePlinkBedFiledoubleFAAA(bed_fn, input_num_ind, input_num_snps, <double*> inx.data)

def writePlinkBedFiledoubleCAAA(bed_fn, input_num_ind, input_num_snps, np.ndarray[np.float64_t, ndim=2] inx):
	_writePlinkBedFiledoubleCAAA(bed_fn, input_num_ind, input_num_snps, <double*> inx.data)
