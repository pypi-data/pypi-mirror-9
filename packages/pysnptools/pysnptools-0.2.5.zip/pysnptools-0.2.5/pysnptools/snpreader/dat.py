import numpy as np
import subprocess, sys, os.path
from itertools import *
import pandas as pd
import logging
from snpreader import SnpReader

class Dat(SnpReader):
    '''
    This is a class that reads into memory from DAT/FAM/MAP files.
    '''

    _ran_once = False

    def __init__(self, dat_filename):
        '''
        filename    : string of the name of the Dat file.
        '''
        self.dat_filename = SnpReader._name_of_other_file(dat_filename,remove_suffix="dat", add_suffix="dat")

    def __repr__(self): 
        return "{0}('{1}')".format(self.__class__.__name__,self.dat_filename)


    @property
    def iid(self):
        self.run_once()
        return self._iid

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

        self._iid = SnpReader._read_fam(self.dat_filename,remove_suffix="dat")
        self._sid, self._pos = SnpReader._read_map_or_bim(self.dat_filename,remove_suffix="dat", add_suffix="map")

        self._assert_iid_sid_pos()


        return self

    #def __del__(self):
    #    if self._filepointer != None:  # we need to test this because Python doesn't guarantee that __init__ was fully run
    #        self._filepointer.close()

    def copyinputs(self, copier):
        # doesn't need to self.run_once() because creates name of all files itself
        copier.input(SnpReader._name_of_other_file(self.dat_filename,remove_suffix="dat", add_suffix="dat"))
        copier.input(SnpReader._name_of_other_file(self.dat_filename,remove_suffix="dat", add_suffix="fam"))
        copier.input(SnpReader._name_of_other_file(self.dat_filename,remove_suffix="dat", add_suffix="map"))

    @property
    def datfields(self):
        if not hasattr(self,"_datfields"):
            #!!could change to just create/find an index to the file position of each row. Instead, reading all into memory
            datfields = pd.read_csv(self.dat_filename,delimiter = '\t',header=None,index_col=False)
            if not np.array_equal(np.array(datfields[0],dtype="string"), self.sid) : raise Exception("Expect snp list in map file to exactly match snp list in dat file")
            self.start_column = 3
            if len(self._iid) != datfields.shape[1]-self.start_column : raise Exception("Expect # iids in fam file to match dat file")
            self._datfields = datfields.T
        return self._datfields

    def _read(self, iid_index_or_none, sid_index_or_none, order, dtype, force_python_only, view_ok):
        '''
        Output dictionary:
        'iid' : [N*2] array of family IDs and individual IDs
        'sid' : [S] array rs-numbers or snp identifiers
        'pos' : [S*3] array of positions [chromosome, genetic dist, basepair dist]
        'val' : [N*S] matrix of per iid snp values
        '''
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


        val = np.zeros((iid_count_out,sid_count_out),order=order, dtype=dtype)
        datfields = self.datfields
        for SNPsIndex, sid_index in enumerate(sid_index_out):
            row = np.array(datfields[sid_index])[self.start_column:,]
            val[:,SNPsIndex] = row[iid_index_out]
        return val


    @staticmethod
    def write(snpdata, basefilename):
        SnpReader._write_fam(snpdata, basefilename, remove_suffix="dat")
        SnpReader._write_map_or_bim(snpdata, basefilename, remove_suffix="dat", add_suffix="map")

        snpsarray = snpdata.val
        with open(basefilename,"w") as dat_filepointer:
            for sid_index, sid in enumerate(snpdata.sid):
                if sid_index % 1000 == 0:
                    logging.info("Writing snp # {0} to file '{1}'".format(sid_index, basefilename))
                dat_filepointer.write("{0}\tj\tn\t".format(sid)) #use "j" and "n" as the major and minor allele
                row = snpsarray[:,sid_index]
                dat_filepointer.write("\t".join((str(i) for i in row)) + "\n")
        logging.info("Done writing " + basefilename)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    snpreader = Dat(r'../tests/datasets/all_chr.maf0.001.N300.dat')
    snp_matrix = snpreader.read()
    print len(snp_matrix['sid'])
    snp_matrix = snpreader[:,:].read()
    print len(snp_matrix['sid'])
    sid_index_list = snpreader.sid_to_index(['23_9','23_2'])
    snp_matrix = snpreader[:,sid_index_list].read()
    print ",".join(snp_matrix['sid'])
    snp_matrix = snpreader[:,0:10].read()
    print ",".join(snp_matrix['sid'])

    print snpreader.iid_count
    print snpreader.sid_count
    print len(snpreader.pos)

    snpreader2 = snpreader[::-1,4]
    print snpreader.iid_count
    print snpreader2.sid_count
    print len(snpreader2.pos)

    snp_matrix = snpreader2.read()
    print len(snp_matrix['iid'])
    print len(snp_matrix['sid'])

    snp_matrix = snpreader2[5,:].read()
    print len(snp_matrix['iid'])
    print len(snp_matrix['sid'])

    iid_index_list = snpreader2.iid_to_index(snpreader2.iid[::2])
    snp_matrix = snpreader2[iid_index_list,::3].read()
    print len(snp_matrix['iid'])
    print len(snp_matrix['sid'])

    snp_matrix = snpreader[[4,5],:].read()
    print len(snp_matrix['iid'])
    print len(snp_matrix['sid'])

    print snpreader2
    print snpreader[::-1,4]
    print snpreader2[iid_index_list,::3]
    print snpreader[:,sid_index_list]
    print snpreader2[5,:]
    print snpreader[[4,5],:]
