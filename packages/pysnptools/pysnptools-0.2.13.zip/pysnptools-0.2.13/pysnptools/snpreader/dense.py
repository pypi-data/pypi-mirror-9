import numpy as np
import logging
from snpreader import SnpReader

class Dense(SnpReader):
    '''!!!cmk add test cases and source example and .write method
    This is a class that reads into memory from DenseAnsi files. This format looks like:

    var	4006	9570    22899	37676	41236	41978	55159	66828...
    1-10004-rs12354060	22222222...
    1-707348-rs12184279	222222?2...
    1-724325-rs12564807	00000000...
    ...

    where rows are SNPs and columns are observations.
    !!!cmk add example
    '''

    _ran_once = False

    def __init__(self, filename, extract_iid_function=lambda s:("0",s), extract_bim_function=lambda s:("0",s,0,0)):
        '''
        filename    : string of the name of the Dat file.
        '''
        self.filename = filename
        self.extract_iid_function = extract_iid_function
        self.extract_bim_function = extract_bim_function

    def __repr__(self): 
        return "{0}('{1}')".format(self.__class__.__name__,self.filename)


    @property
    def iid(self):
        self.run_once()
        return self._original_iid

    @property
    def sid(self):
        self.run_once()
        return self._sid

    @property
    def pos(self):
        self.run_once()
        return self._pos

    def run_once(self):
        if (self._ran_once):
            return
        self._ran_once = True

        bim_list = []
        with open(self.filename,"r") as fp:
            header = fp.readline()
            iid_string_list = header.strip().split()[1:]
            self._original_iid = np.array([self.extract_iid_function(iid_string) for iid_string in iid_string_list],dtype="string")
            val_list = []
            for line_index,line in enumerate(fp):
                if line_index % 1000 == 0:
                    logging.info("reading sid and iid info from line {0} of file '{1}'".format(line_index, self.filename))
                sid_string, rest = line.strip().split()
                bim_list.append(self.extract_bim_function(sid_string))
                assert len(rest) == len(self._original_iid)

        self._sid = np.array([bim[1] for bim in bim_list],dtype='str')
        self._pos = np.array([[bim[0],bim[2],bim[3]] for bim in bim_list],dtype='int')

        return self

    #def __del__(self):
    #    if self._filepointer is not None:  # we need to test this because Python doesn't guarantee that __init__ was fully run
    #        self._filepointer.close()

    def copyinputs(self, copier):
        # doesn't need to self.run_once() because creates name of all files itself
        copier.input(self.filename)

    def _read(self, iid_index_or_none, sid_index_or_none, order, dtype, force_python_only, view_ok):
        assert not hasattr(self, 'ind_used'), "A SnpReader should not have a 'ind_used' attribute"
        if order is None:
            order = "F"
        if dtype is None:
            dtype = np.float64
        if force_python_only is None:
            force_python_only = False

        #This could be re-factored to not use so many names
        iid_count_in = self.iid_count
        sid_count_in = self.sid_count

        if iid_index_or_none is not None:
            iid_count_out = len(iid_index_or_none)
            iid_index_out = iid_index_or_none
        else:
            iid_count_out = iid_count_in
            iid_index_out = range(iid_count_in)

        if sid_index_or_none is not None:
            sid_count_out = len(sid_index_or_none)
            sid_index_out = sid_index_or_none
        else:
            sid_count_out = sid_count_in
            sid_index_out = range(sid_count_in)

        if not hasattr(self,"val_list_list"):
            val_list_list = []
            with open(self.filename,"r") as fp:
                header = fp.readline()
                for line_index,line in enumerate(fp):
                    if line_index % 1000 == 0:
                        logging.info("reading values from line {0} of file '{1}'".format(line_index, self.filename))
                    sid_string, rest = line.strip().split()
                    assert len(rest) == len(self._original_iid)
                    val_list = [int(val) if val!="?" else np.NaN for val in rest]
                    val_list_list.append(val_list)
            self.val_list_list = val_list_list


        val = np.zeros((iid_count_out,sid_count_out),order=order, dtype=dtype)
        for SNPsIndex, sid_index in enumerate(sid_index_out):
            row = np.array(self.val_list_list[sid_index])
            val[:,SNPsIndex] = row[iid_index_out]
        return val

    @staticmethod
    def write(snpdata, filename, join_iid_function=lambda iid_pair:iid_pair[1]):
        snpsarray = snpdata.val
        with open(filename,"w") as filepointer:
            filepointer.write("var"+"\t")
            filepointer.write("\t".join((join_iid_function(iid_pair) for iid_pair in snpdata.iid)) + "\n")

            for sid_index, sid in enumerate(snpdata.sid):
                if sid_index % 1000 == 0:
                    logging.info("Writing snp # {0} to file '{1}'".format(sid_index, filename))
                filepointer.write("{0}\t".format(sid))
                row = snpsarray[:,sid_index]
                filepointer.write("".join((str(int(i)) if i==i else "?" for i in row)) + "\n")
        logging.info("Done writing " + basefilename)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    #!!!cmk
    import os
    from pysnptools.snpreader import Dense
    from pysnptools.snpreader import Bed

    os.chdir(r"h:\deldir\x")
    snpreader = Dense("del1.dense.txt")
    snpdata=snpreader.read()
    #Dense.write(snpdata,"del1.test.dense.txt")
    Bed.write(snpdata,"del1.test")

    #!!!cmkimport doctest
    #!!!cmkdoctest.testmod()

