from pysnptools.util.intrangeset import IntRangeSet

import scipy as sp
import logging
import numpy as np



def _testtest(data, iididx):
    return (data[0][iididx],data[1][iididx])

def intersect_apply(data_list, sort_by_dataset=True):
    """Intersects and sorts the iids from a list of datasets, returning new version of the datasets with all the same iids in the same order.

    :param data_list: list of datasets
    :type data_list: list
    :param sort_by_dataset: optional, If True (default), the iids are ordered according to the first non-None dataset.
        If False, the order is arbitrary, but consistent.
    :type sort_by_dataset: bool

    :rtype: list of datasets

    Here are the dataset formats understood and what is returned for each.

    ============================================== ================================================================
    Dataset Format                                 What is Returned
    ============================================== ================================================================
    None                                           None
    A :class:`.SnpReader`                          A new subsetting :class:`.SnpReader` with adjusted iid
    A dictionary with ['iid'] and ['vals'] keys    The same dictionary but with the iid and vals values adjusted
    Tuple of the form (val ndarray, iid list)      A new tuple with the val ndarray and iid list adjusted
    ============================================== ================================================================
    
    If the iids in all the datasets are already the same and in the same order, then the datasets are returned without change.

    Notice that only dictionaries are processed in-place. Inputting a :class:`.SnpReader` returns a new :class:`.SnpReader` (unless its iids
    are already ok). Inputting a tuple returns a new tuple (unless its iids are already ok).

    :Example:

    >>> from pysnptools.snpreader import Bed
    >>> from pysnptools.util.pheno import loadOnePhen,loadPhen
    >>>
    >>> #Create five datasets in different formats
    >>> ignore_in = None
    >>> snpreader_in = Bed('../../tests/datasets/all_chr.maf0.001.N300') # Specify SNP data on disk
    >>> pheno_dict = loadOnePhen('../../tests/datasets/phenSynthFrom22.23.N300.randcidorder.txt')
    >>> cov = loadPhen('../../tests/datasets/all_chr.maf0.001.covariates.N300.txt')
    >>> cov_as_tuple_in = (cov['vals'],cov['iid']) #We could do cov directly, but as an example we make it a tuple.
    >>>
    >>> # Create five new datasets with consistent iids
    >>> ignore_out, snpreader_out, pheno_dict, cov_as_tuple_out = intersect_apply([ignore_in, snpreader_in, pheno_dict, cov_as_tuple_in])
    >>> # Print the first five iids from each dataset
    >>> print ignore_out, snpreader_out.iid[:5], pheno_dict['iid'][:5], cov_as_tuple_out[1][:5]
    None [['POP1' '0']
     ['POP1' '12']
     ['POP1' '44']
     ['POP1' '58']
     ['POP1' '65']] [['POP1' '0']
     ['POP1' '12']
     ['POP1' '44']
     ['POP1' '58']
     ['POP1' '65']] [['POP1' '0']
     ['POP1' '12']
     ['POP1' '44']
     ['POP1' '58']
     ['POP1' '65']]
    """

    iid_list = []
    reindex_list = []

    for data in data_list:
        if data is None:
            iid = None
            reindex = lambda data, iididx : None
        else:
            try: #pheno dictionary
                iid = data['iid'] 
                reindex = lambda data, iididx : _reindex_phen_dict(data, iididx)
            except:
                try: #snpreader
                    iid = data.iid
                    reindex = lambda data, iididx : data[iididx,:]
                except AttributeError: #tuple of (val,iid)
                    iid = data[1]
                    reindex = lambda data, iididx : _testtest(data,iididx)

        iid_list.append(iid)
        reindex_list.append(reindex)

    if len(iid_list) == 0: raise Exception("Expect a least one input item")

    if _all_same(iid_list):
        logging.info("iids match up across {0} data sets".format(len(iid_list)))
        return data_list
    else:
        logging.info("iids do not match up, so intersecting the data over individuals")            
        indarr = intersect_ids(iid_list)
        assert indarr.shape[0] > 0, "no individuals remain after intersection, check that ids match in files"

        if sort_by_dataset:
            #Look for first non-None iid
            for i, iid in enumerate(iid_list):
                if iid is not None:
                    #sort the indexes so that SNPs ids in their original order (and 
                    #therefore we have to move things around in memory the least amount)
                    sortind=sp.argsort(indarr[:,i])
                    indarr=indarr[sortind]
                    break

        data_out_list = []
        for i in xrange(indarr.shape[1]):
            data = data_list[i]
            iididx = indarr[:,i]
            reindex = reindex_list[i]
            new_data = reindex(data, iididx)
            data_out_list.append(new_data)

        return data_out_list

def _reindex_phen_dict(phen_dict, iididx):
    if len(phen_dict['vals'].shape)==1:
        phen_dict['vals'] = phen_dict['vals'][iididx]
    else:
        phen_dict['vals'] = phen_dict['vals'][iididx,:]
    phen_dict['iid'] = phen_dict['iid'][iididx]
    return phen_dict

def _all_same(iids_list):
    for i in xrange(len(iids_list)-1):
        iidA = iids_list[i]
        iidB = iids_list[i+1]
        if iidA is not None and iidB is not None:
            if len(iidA) != len(iidB) or not sp.all(iidA == iidB):
                return False
    return True

def intersect_ids(idslist):
    '''Takes a list of 2d string arrays of family and individual ids.
    These are intersected.

    :rtype: indarr, an array of size N x L, where N is the number of
        individuals in the intersection, and L is the number of lists in idslist, and which
        contains the index to use (in order) such that all people will be identical and in order
        across all data sets.

    If one of the lists=None, it is ignored (but still has values reported in indarr, all equal to -1),
    '''
    id2ind={}    
    L=len(idslist)
    observed=sp.zeros(L,dtype='bool')
    first = True
    for l, id_list in enumerate(idslist):
        if id_list is not None:
            observed[l]=1
            if first:
                first = False
                for i in xrange(id_list.shape[0]):
                    id=(id_list[i,0], id_list[i,1])
                    entry=sp.zeros(L)*sp.nan #id_list to contain the index for this id, for all lists provided
                    entry[l]=i                 #index for the first one
                    id2ind[id]=entry
            else:
                for i in xrange(id_list.shape[0]):
                    id=(id_list[i,0], id_list[i,1])
                    if id2ind.has_key(id):
                        id2ind[id][l]=i

    indarr=sp.array(id2ind.values(),dtype='float')  #need float because may contain NaNs
    indarr[:,~observed]=-1                          #replace all Nan's from empty lists to -1
    inan = sp.isnan(indarr).any(1)                  #find any rows that contain at least one Nan
    indarr=indarr[~inan]                            #keep only rows that are not NaN
    indarr=sp.array(indarr,dtype='int')             #convert to int so can slice 
    return indarr   


def sub_matrix(val, row_index_list, col_index_list, order='A', dtype=sp.float64):
    """
    Efficiently creates a sub-matrix from a 2-D ndarray.

    :param val: The ndarray from which to copy.
    :type val: ndarray
    :param row_index_list: Tells which rows (and in which order) to copy into the sub-matrix
    :type row_index_list: list of integers
    :param col_index_list: Tells which columns (and in which order) to copy into the sub-matrix
    :type col_index_list: list of integers
    :param order: {'A' (default), 'C', 'F'}, optional -- Specify the order of the sub-matrix to create.
        If order is 'C', then the returned sub-matrix will be in C-contiguous order (first index varies the fastest).
        If order is 'F', then the array will be in F-contiguous order (second index varies the fastest).
        If order is 'A', then sub-matrix may be in any order F or C.
    :type order: string or None
    :param dtype: {scipy.float64 (default), scipy.float32}, optional -- The data-type for sub-matrix created.
    :type dtype: data-type

    :rtype: ndarray

    >>> import numpy as np
    >>> import pysnptools.util as pstutil
    >>> np.random.seed(0) # set seed so that results are deterministic
    >>> matrix = np.random.rand(12,7) # create a 12 x 7 ndarray
    >>> submatrix = pstutil.sub_matrix(matrix,[0,2,11],[6,5,4,3,2,1,0])
    >>> print (int(submatrix.shape[0]),int(submatrix.shape[1]))
    (3, 7)
    >>> print matrix[2,0] == submatrix[1,6] #The row # 2 is now #1, the column #0 is now #6.
    True

    Note: Behind the scenes, for performance, this function selects and then calls one of 16 C++ helper functions.
    """
    from pysnptools.snpreader import wrap_matrix_subset

    if order == 'A':
        if val.flags['F_CONTIGUOUS']:
            effective_order = 'F'
        else:
            effective_order = 'C'
    else:
        effective_order = order

    sub_val = sp.empty((len(row_index_list), len(col_index_list)),dtype=dtype,order=effective_order)

    logging.debug("About to call cython matrixSubset")

    iid_count, sid_count = val.shape

    if val.flags['F_CONTIGUOUS']:
        if val.dtype ==  sp.float64:
            if dtype == sp.float64:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetDoubleFToDoubleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetDoubleFToDoubleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("order '{0}' not known, only 'F' and 'C'".format(effective_order));
            elif dtype == sp.float32:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetDoubleFToSingleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetDoubleFToSingleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("dtype '{0}' not known, only float64 and float32".format(dtype))
        elif val.dtype ==  sp.float32:
            if dtype == sp.float64:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetSingleFToDoubleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetSingleFToDoubleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("order '{0}' not known, only 'F' and 'C'".format(effective_order));
            elif dtype == sp.float32:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetSingleFToSingleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetSingleFToSingleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("dtype '{0}' not known, only float64 and float32".format(dtype))
        else:
            raise Exception("input dtype '{0}' not known, only float64 and float32".format(val.dtype))
    elif val.flags['C_CONTIGUOUS']:
        if val.dtype ==  sp.float64:
            if dtype == sp.float64:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetDoubleCToDoubleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetDoubleCToDoubleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("order '{0}' not known, only 'F' and 'C'".format(effective_order));
            elif dtype == sp.float32:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetDoubleCToSingleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetDoubleCToSingleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("dtype '{0}' not known, only float64 and float32".format(dtype))
        elif val.dtype ==  sp.float32:
            if dtype == sp.float64:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetSingleCToDoubleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetSingleCToDoubleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("order '{0}' not known, only 'F' and 'C'".format(effective_order));
            elif dtype == sp.float32:
                if effective_order=="F":
                    wrap_matrix_subset.matrixSubsetSingleCToSingleFAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                elif effective_order=="C":
                    wrap_matrix_subset.matrixSubsetSingleCToSingleCAAA(val, iid_count, sid_count, row_index_list, col_index_list, sub_val)
                else:
                    raise Exception("dtype '{0}' not known, only float64 and float32".format(dtype))
        else:
            raise Exception("input dtype '{0}' not known, only float64 and float32".format(val.dtype))
    else:
        raise Exception("input order must be 'F' or 'C'");


    logging.debug("Back from cython matrixSubset")
    return sub_val

def create_directory_if_necessary(name, isfile=True):    
    import os
    if isfile:
        directory_name = os.path.dirname(name)
    else:
        directory_name = name

    if directory_name != "":
        try:
            os.makedirs(directory_name)
        except OSError, e:
            if not os.path.isdir(directory_name):
                raise Exception("not valid path: '{0}'. (Working directory is '{1}'".format(directory_name,os.getcwd()))

def weighted_mean(ys, weights):
    '''
    >>> ys = np.array([103.664086,89.80645161,83.86888046,90.54141176])
    >>> weights = np.array([2.340862423,4.982888433,0.17522245,0.098562628])
    >>> round(weighted_mean(ys, weights),5)
    93.9487
    '''
    mean = ys.dot(weights)/weights.sum()
    return mean


def weighted_simple_linear_regression(xs, ys, weights):
    '''
    >>> xs = np.array([53.8329911,57.49486653,60.07392197,60.21081451])
    >>> ys = np.array([103.664086,89.80645161,83.86888046,90.54141176])
    >>> weights = np.array([2.340862423,4.982888433,0.17522245,0.098562628])
    >>> slope, intercept, xmean, ymean = weighted_simple_linear_regression(xs, ys, weights)
    >>> print round(slope,5), round(intercept,5), round(xmean,5), round(ymean,5)
    -3.52643 293.05586 56.46133 93.9487

    '''
    xmean = weighted_mean(xs,weights)
    xs_less_mean = xs - xmean
    ymean = weighted_mean(ys,weights)
    ys_less_mean = ys - ymean
    weighted_xs_less_mean = xs_less_mean * weights
    slope = ys_less_mean.dot(weighted_xs_less_mean)/xs_less_mean.dot(weighted_xs_less_mean)
    intercept = ymean - xmean * slope
    return slope, intercept, xmean, ymean



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)


    # There is also a unit test case in 'pysnptools\test.py' that calls this doc test
    import doctest
    doctest.testmod()
