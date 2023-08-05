import scipy as sp

def loadOnePhen(filename,  i_pheno = 0, missing ='-9', vectorize = False):
    '''
    Load one column of a phenotype file. Remove any rows with missing data

    :param filename: name of the file
    :type filename: string
    :param i_pheno: column to return (default '0', the first column)
    :type i_pheno: int
    :param missing: value to threat as missing
    :type missing: string
    :param vectorize: if true, return a 1-D vector rather than a 2-D array
    :type vectorize: bool

    :rtype: An output dictionary

    The output dictionary looks like:

    * 'header' : [1] array phenotype namesv (only if header line is specified in file),
    * 'vals'   : [N*1] array of phenotype-data,
    * 'iid'    : [N*2] array of family IDs and individual IDs
    '''

    allColumns = loadPhen(filename, missing)
    i_present=allColumns['vals'][:,i_pheno]==allColumns['vals'][:,i_pheno]
    valsvector = allColumns['vals'][i_present,i_pheno]
    vals = sp.reshape(valsvector,(-1,1))
    iid = allColumns['iid'][i_present,:]
    #iid = iid.reshape(iid.shape[1], iid.shape[2])
    header = allColumns['header']
    if header is not None:
        header = [header[i_pheno]]

    if vectorize:
        vals = vals[:,0]

    ret = {
            'header':header,
            'vals':vals,
            'iid':iid
            }
    return ret


def loadPhen(filename, missing ='-9', pheno = None):
    '''
    Load a phenotype or covariate file. Covariates have the same file format.

    :param filename: name of the file
    :type filename: string
    :param missing: value to threat as missing
    :type missing: string
    :param vectorize: if true, return a 1-D vector rather than a 2-D array
    :type vectorize: bool

    :rtype: An output dictionary

    The output dictionary looks like:

    * 'header' : [1] array phenotype namesv (only if header line is specified in file),
    * 'vals'   : [N*1] array of phenotype-data,
    * 'iid'    : [N*2] array of family IDs and individual IDs
    '''
    data = sp.loadtxt(filename,dtype = 'str',comments=None)
    if data[0,0] == 'FID':
        header = data[0,2::]
        data = data[1::]
    else:
        header = [None] * (data.shape[1]-2) # create a header containing a list of None's
    iid = data[:,0:2]
    data = data[:,2::]
    imissing = data==missing
    vals = sp.array(data,dtype = 'float')
    vals[imissing] = sp.nan


    if pheno is not None:
        #TODO: sort and filter SNPs according to pheno.
        pass
    ret = {
            'header':header,
            'vals':vals,
            'iid':iid
            }
    return ret
