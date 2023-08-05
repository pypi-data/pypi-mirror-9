#!/usr/bin/env python
import copy
import tables
from .Sparse3DMatrix import Sparse3DMatrix
import numpy as np
from scipy.sparse import lil_matrix, coo_matrix, csc_matrix, csr_matrix

__author__ = 'Kwangbom "KB" Choi, Ph. D.'

def enum(**enums):
    return type('Enum', (), enums)


class AlignmentPropertyMatrix(Sparse3DMatrix):

    Axis = enum(LOCUS=0, HAPLOTYPE=1, READ=2, GROUP=3)

    def __init__(self, other=None, \
                 h5file=None, datanode='/', metanode='/', shallow=False, \
                 shape=None, dtype=float, haplotype_names=None, locus_names=None, read_names=None, \
                 grpfile=None):

        Sparse3DMatrix.__init__(self, other=other, h5file=h5file, datanode=datanode, shape=shape, dtype=dtype)

        self.num_loci, self.num_haplotypes, self.num_reads = self.shape
        self.num_groups = 0
        self.hname  = None
        self.lname  = None   # locus name
        self.rname  = None   # read name
        self.lid    = None   # locus ID
        self.rid    = None   # read ID
        self.gname  = None   # group name
        self.groups = None   # groups in terms of locus IDs

        if other is not None: # Use for copying from other existing AlignmentPropertyMatrix object
            if not shallow:
                self.__copy_names(other)
                self.__copy_group_info(other)

        elif h5file is not None:  # Use for loading from a pytables file
            if not shallow:
                h5fh = tables.open_file(h5file, 'r')
                self.hname = h5fh.get_node_attr(datanode, 'hname')
                self.lname = h5fh.get_node(metanode, 'lname').read()
                self.rname = h5fh.get_node(metanode, 'rname').read()
                self.lid = dict(zip(self.lname, np.arange(self.num_loci)))
                self.rid = dict(zip(self.rname, np.arange(self.num_reads)))
                h5fh.close()

        elif shape is not None: # Use for initializing an empty matrix
            if haplotype_names is not None:
                if len(haplotype_names) == self.num_haplotypes:
                    self.hname = haplotype_names
                else:
                    raise RuntimeError('The number of names does not match to the matrix shape.')
            if locus_names is not None:
                if len(locus_names) == self.num_loci:
                    self.lname = np.array(locus_names)
                    self.lid   = dict(zip(self.lname, np.arange(self.num_loci)))
                else:
                    raise RuntimeError('The number of names does not match to the matrix shape.')
            if read_names is not None:
                if len(read_names) == self.num_reads:
                    self.rname = np.array(read_names)
                    self.rid   = dict(zip(self.rname, np.arange(self.num_reads)))
                else:
                    raise RuntimeError('The number of names does not match to the matrix shape.')

        if grpfile is not None:
            self.__load_groups(grpfile)

    def __load_groups(self, grpfile): # A group is a set of isoforms within a gene
        if self.lid is not None:
            self.gname  = list()
            self.groups = list()
            with open(grpfile) as fh:
                for curline in fh:
                    item = curline.rstrip().split("\t")
                    self.gname.append(item[0])
                    tid_list = [ self.lid[t] for t in item[1:] ]
                    self.groups.append(tid_list)
            self.gname = np.array(self.gname)
            self.num_groups = len(self.gname)
        else:
            raise RuntimeError('Locus IDs are not availalbe.')

    load_groups = __load_groups

    def __copy_names(self, other):
        self.hname = other.hname
        self.lname = copy.copy(other.lname)
        self.rname = copy.copy(other.rname)
        self.lid   = copy.copy(other.lid)
        self.rid   = copy.copy(other.rid)

    def __copy_group_info(self, other):
        # if other.num_groups > 0:
        if other.groups is not None and other.gname is not None:
            self.groups = copy.deepcopy(other.groups)
            self.gname  = copy.copy(other.gname)
            self.num_groups = other.num_groups

    def copy(self, shallow=False):
        dmat = Sparse3DMatrix.copy(self)
        dmat.num_loci, dmat.num_haplotypes, dmat.num_reads = dmat.shape
        if not shallow:
            dmat.__copy_names(self)
            dmat.__copy_group_info(self)
        return dmat

    def _bundle_inline(self, reset=False): # Inline bundling method
        if self.finalized:
            if self.num_groups > 0 and self.groups is not None and self.gname is not None:
                grp_conv_mat = lil_matrix((self.num_loci, self.num_groups))
                for i in xrange(self.num_groups):
                    grp_conv_mat[self.groups[i], i] = 1.0
                grp_conv_mat = grp_conv_mat.tocsc()
                for hid in xrange(self.num_haplotypes):
                    self.data[hid] = self.data[hid] * grp_conv_mat # TODO: Is there any better way to save memory?
                self.num_loci = self.num_groups
                self.shape = (self.num_groups, self.num_haplotypes, self.num_reads)
                self.lname = copy.copy(self.gname)
                self.lid   = dict(zip(self.gname, np.arange(self.num_groups)))
                self.num_groups = 0
                self.groups = None
                self.gname = None
                if reset:
                    self.reset()
            else:
                raise RuntimeError('No group information is available for bundling.')
        else:
            raise RuntimeError('The matrix is not finalized.')

    def bundle(self, reset=False, shallow=False): # Copies the original matrix (Use lots of memory)
        """
        Returns ``AlignmentPropertyMatrix`` object in which loci are bundled using grouping information.

        :param reset: whether to reset the values at the loci
        :param shallow: whether to copy all the meta data

        """
        if self.finalized:
            # if self.num_groups > 0:
            if self.groups is not None and self.gname is not None:
                grp_conv_mat = lil_matrix((self.num_loci, self.num_groups))
                for i in xrange(self.num_groups):
                    grp_conv_mat[self.groups[i], i] = 1.0
                grp_align = Sparse3DMatrix.__mul__(self, grp_conv_mat) # The core of the bundling
                grp_align.num_loci = self.num_groups
                grp_align.num_haplotypes = self.num_haplotypes
                grp_align.num_reads = self.num_reads
                grp_align.shape = (grp_align.num_loci, grp_align.num_haplotypes, grp_align.num_reads)
                if not shallow:
                    grp_align.lname = copy.copy(self.gname)
                    grp_align.hname = self.hname
                    grp_align.rname = copy.copy(self.rname)
                    grp_align.lid   = dict(zip(grp_align.lname, np.arange(grp_align.num_loci)))
                    grp_align.rid   = copy.copy(self.rid)
                if reset:
                    grp_align.reset()
                return grp_align
            else:
                raise RuntimeError('No group information is available for bundling.')
        else:
            raise RuntimeError('The matrix is not finalized.')

    #
    # Binary Operators
    #

    def __add__(self, other):
        dmat = Sparse3DMatrix.__add__(self, other)
        dmat.num_loci, dmat.num_haplotypes, dmat.num_reads = self.shape
        dmat.__copy_names(self)
        dmat.__copy_group_info(self)
        return dmat

    def __sub__(self, other):
        dmat = Sparse3DMatrix.__sub__(self, other)
        dmat.num_loci, dmat.num_haplotypes, dmat.num_reads = self.shape
        dmat.__copy_names(self)
        dmat.__copy_group_info(self)
        return dmat

    def __mul__(self, other):
        dmat = Sparse3DMatrix.__mul__(self, other)
        dmat.num_loci, dmat.num_haplotypes, dmat.num_reads = dmat.shape
        if isinstance(other, (np.ndarray, csc_matrix, csr_matrix, coo_matrix, lil_matrix)):
            dmat.hname = self.hname
            dmat.rname = copy.copy(self.rname)
            dmat.rid   = copy.copy(self.rid)
            dmat.num_groups = 0
        else:
            dmat.__copy_names(self)
            dmat.__copy_group_info(self)
        return dmat

    #
    # Helper functions
    #

    def initialize(self): # Inline initialization
        if self.finalized:
            self.normalize_reads(axis=self.Axis.LOCUS)
            # When there are nested groups (like a gene as a group of isoforms),
            # we should run load_groups(grpfile) first before running this method.
            if self.groups is not None and self.gname is not None: # Each group should have equal weight initially.
                self.normalize_reads(axis=self.Axis.GROUP, groups=self.groups)
            self.normalize_reads(axis=self.Axis.READ)
        else:
            raise RuntimeError('The matrix is not finalized.')

    def get_initial_probability(self, shallow=False): # Copies the original matrix (Use lots of memory)
        if self.finalized:
            align_prob = self.copy(shallow=shallow)
            align_prob.normalize_reads(axis=self.Axis.LOCUS)
            # if self.num_groups > 0:
            # When there are nested groups (like a gene as a group of isoforms),
            # we should run load_groups(grpfile) first before running this method.
            if self.groups is not None and self.gname is not None: # Each group should have equal weight initially.
                align_prob.normalize_reads(axis=self.Axis.GROUP, groups=self.groups)
            align_prob.normalize_reads(axis=self.Axis.READ)
            return align_prob
        else:
            raise RuntimeError('The matrix is not finalized.')

    def get_unique_reads(self, shallow=False):
        if self.finalized:
            unique_reads = AlignmentPropertyMatrix()
            unique_reads.shape = self.shape
            unique_reads.num_loci, unique_reads.num_haplotypes, unique_reads.num_reads = self.shape
            if not shallow:
                unique_reads.__copy_names(self)
                unique_reads.__copy_group_info(self)
            factor = self.sum(axis=self.Axis.LOCUS).sum(axis=self.Axis.HAPLOTYPE) # Read-level number of alignments
            for hid in xrange(self.num_haplotypes):
                hdata = self.data[hid].copy()
                hdata.data *= factor[hdata.indices] # Only unique reads will remain to be 1
                hdata = hdata.tocoo()
                uloc = np.where(abs(hdata.data - 1.0) < 0.000001)[0].ravel()
                hdata.row = hdata.row[uloc]
                hdata.col = hdata.col[uloc]
                hdata.data = hdata.data[uloc]
                unique_reads.data.append(hdata)
            unique_reads.finalize()
            return unique_reads
        else:
            raise RuntimeError('The matrix is not finalized.')

    def count_unique_reads(self, ignore_haplotype=False):
        if self.finalized:
            if ignore_haplotype:
                summat = self.sum(axis=self.Axis.HAPLOTYPE)
                #nnz_readwise = summat.getnnz(axis=1)
                nnz_readwise = np.diff(summat.tocsr().indptr)
                unique_reads = summat[nnz_readwise < 2]
                unique_reads.data = np.ones(unique_reads.nnz)
                return unique_reads.sum(axis=0).A.ravel()
            else:
                unique_reads = self.get_unique_reads()
                return unique_reads.sum(axis=self.Axis.READ)
        else:
            raise RuntimeError('The matrix is not finalized.')

    def count_alignments(self):
        if self.finalized:
            summat = self.sum(axis=self.Axis.READ)
            return summat
        else:
            raise RuntimeError('The matrix is not finalized.')

    def combine(self, other, shallow=False):
        if self.finalized and other.finalized:
            dmat = Sparse3DMatrix.combine(self, other)
            dmat.num_loci, dmat.num_haplotypes, dmat.num_reads = dmat.shape
            if not shallow:
                dmat.hname = self.hname
                dmat.lname = copy.copy(self.lname)
                dmat.rname = np.concatenate((self.rname, other.rname))
                dmat.lid   = copy.copy(self.lid)
                dmat.rid   = dict(zip(dmat.rname, np.arange(dmat.num_reads)))
                dmat.__copy_group_info(self)
            return dmat
        else:
            raise RuntimeError('Both matrices must be finalized.')

    def save(self, h5file, title=None, index_dtype='uint32', data_dtype=float, incidence_only=True, complib='zlib', shallow=False):
        Sparse3DMatrix.save(self, h5file=h5file, title=title, index_dtype=index_dtype, data_dtype=data_dtype, incidence_only=incidence_only, complib=complib)
        if not shallow:
            h5fh = tables.open_file(h5file, 'a')
            fil  = tables.Filters(complevel=1, complib=complib)
            h5fh.set_node_attr(h5fh.root, 'hname', self.hname)
            h5fh.create_carray(h5fh.root, 'lname', obj=self.lname, title='Locus Names', filters=fil)
            h5fh.create_carray(h5fh.root, 'rname', obj=self.rname, title='Read Names', filters=fil)
            h5fh.flush()
            h5fh.close()

    def get_read_data(self, rid):
        return self.get_cross_section(index=rid, axis=self.Axis.READ)

    def print_read(self, rid):
        """
        Function: Prints nonzero rows of the read wanted

        """
        if self.rname is not None:
            print self.rname[rid]
        r = self.get_read_data(rid)
        #nzcol = r.nonzero()[1]
        #if len(nzcol) > 0:
            #print r[:, np.unique(nzcol)].todense().transpose()
        aligned_loci = np.unique(r.nonzero()[1])
        for locus in aligned_loci:
            print locus + "\t" + r[:, locus].todense().transpose()[0]
        else:
            print

    #
    # For future use
    #
    def get_reads_aligned_to_locus(self, locus_name, use_read_name=False):
        rset  = self.l2rset[self.lid[locus_name]]
        reads = dict()
        for r in rset:
            rdata = self.get_read_data(r)
            if use_read_name:
                r = self.rname[r]
            reads[r] = rdata
        return reads


if __name__=="__main__":
    pass # TODO: Put a simple usage example here

