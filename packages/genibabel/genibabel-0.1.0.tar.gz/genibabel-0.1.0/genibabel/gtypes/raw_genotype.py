#! /usr/bin/env python
##########################################################################
# genibabel - Copyright (C) CEA, 2014
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
#
# authors: vfrouin , code from B daMota (shared python module genim-stat)
#
##########################################################################

# System import
import numpy as np
import csv
import os


class RawGenotype(object):
    """ Class to store genotypes (snp variations) for a bunch of subjects.

        It can be seen as a table of the form:

                  ------------------------------------------
                  | <snp id>  | <snp id>  | <snp id>  |  ...
     -------------------------------------------------------
     |<subject id>|   0|1|2   |   0|1|2   |   0|1|2   |  ...
      ------------------------------------------------------
     |<subject id>|   0|1|2   |   0|1|2   |   0|1|2   |  ...
      ------------------------------------------------------
     |     .      |     .     |     .     |     .     |
           :            :           :           :

    The table values (0[1|2) are stored as a 2D-array and the labels 
    (snp ids and subject ids) are stored as 1D-arrays: snpid and iid.

    The class also stores meta-informations for snps and subjects
    (related genes, chromosomes and families).

    Methods
    -------
    csv_export
    get_snp_meta
    get_meta
    

    Attributes
    ----------
    genodata: array
        the genotype data.
    snpid: array
        the snps identifiers (the columns of the 'genodata' array).
    iid: array
        the subject identifiers (the rows of the 'genodata' array).
    fid: list of str
        the family identifiers (the rows of the 'genodata' array).
    """
    def __init__(self, genodata, iid, snpid, fid, cid, gid, pws=None):
        """ Initialize the RawGenotype class.

        Parameters
        ----------
        genodata: array
            the genotype data.
        iid: list of str
            the individual identifiers (the rows of the 'genodata' array).
        snpid: list of str
            the snps identifiers (the columns of the 'genodata' array).
        fid: list of str
            the family identifiers.
        cid: dict
            the chromosomes associated with the snps.
        gid: dict
            the genes associated with the snps.
        """
        self.data = genodata
        self.iid = np.asarray(iid)
        self.snpid = np.asarray(snpid)
        self.fid = np.asarray(fid)
        self._cid = cid
        self._gid = gid
        self._pws = pws

    def __getitem__(self, index):
        """ Definition of the get attribute method of RawGenotype object.

        Parameters
        ----------
        index: str (mandatory)
            an index supporting the numpy synthax.

        Returns
        -------
        array_data: array
            the genotype data at the desired index.
        array_iids: array
            the column labels.
        array_snps: array
            the row labels.
        """
        # Convert index to generic matrix index
        if not isinstance(index, tuple):
            index = (index, slice(None))

        # Check that we have a valid matrix index
        if len(index) != 2:
            raise ValueError("Expect a matrix index.")

        # Convert string index to access element by there names
        index = (
            self._convert_literal_index(index[0], self.iid.tolist()),
            self._convert_literal_index(index[1], self.snpid.tolist())
        )

        # Access the genodata and associated meta information
        array_data = self.data[index]
        array_iids = self.iid[index[0]]
        array_snps = self.snpid[index[1]]
        # > deal with unique element access
        if not isinstance(array_iids, np.ndarray):
            array_iids = np.array([array_iids])
        if not isinstance(array_snps, np.ndarray):
            array_snps = np.array([array_snps])
        # > deal with multpile elements access
        if isinstance(index[0], list) and isinstance(index[1], list):
            indices = ["{0}-{1}".format(x, y)
                       for x, y in zip(array_iids, array_snps)]
            array_iids, array_snps = indices
        else:
            array_data.shape = (len(array_iids), len(array_snps))

        return array_data, array_iids, array_snps

    ###########################################################################
    # Private Members
    ###########################################################################

    def _convert_literal_index(self, index, mapping):
        """ Convert literal index to array index.
    
        Parameters
        ----------
        index: object (mandatory)
            an index to convert.
        mapping: list (mandatory)
            the list of litteral items.

        Returns
        -------
        array_index: object
            a converted array index.
        """
        # Recursive case
        if isinstance(index, list) or isinstance(index, tuple):
            array_index = []
            for sub_index in index:
                array_index.append(self._convert_literal_index(sub_index, mapping))
            if isinstance(index, tuple):
                array_index = tuple(array_index)
            return array_index

        # Start conversion
        if isinstance(index, basestring):
            return mapping.index(index)
        else:
            return index       

    ###########################################################################
    # Public Members
    ###########################################################################

    def get_snp_meta(self, snp_name):
        """ Return a snp associated gene(s) and chromosome(s).

        Parameters
        ----------
        snp_name: str (mandatory)
            a snp name.

        Returns
        -------
        chrs: list
            the snp associated chromosomes.
        genes: list
            the snp associated genes.
        """
        return self._cid.get(snp_name, []), self._gid.get(snp_name, [])

    def get_meta(self):
        """ Return 3 lists snpid, chr and gene

        Return:
        -------
        snpl: list
        chrl: list
        genel: list
        """
        gene_list = []
        chr_list = []
        for rs_id in self.snpid:
            gene_list.append("/".join(list(self._gid.get(rs_id, []))))
            chr_list.append("/".join(list(self._cid.get(rs_id, []))))

        return self.snpid, chr_list, gene_list
        
    def get_meta_pws(self):
        """Return meta information about pathways
        
        Return:
        -------
        meta_pws: dict() key names and value corresponging snp's index list
        """
        if self._pws == None:
            return None
        else:
            meta_pws = dict()
            for pw in self._pws:
                w = []
                for g in pw['genes']:
                    w.extend(np.where(np.asarray(self.get_meta()[2])
                                                           == unicode(g))[0])
                if len(w) != 0:
                    meta_pws[pw['name']] = np.sort(w)

        return meta_pws





    def csv_export(self, fname):
        """ Export the genotype data in .csv format.

        The .csv delimiter is ";" while the single quote will be used for
        characters.

        Parameters
        ----------
        fname: str (mandatory)
            the path where the table will be saved.
        """
        # Check the directory exists
        if not os.path.isdir(os.path.dirname(fname)):
            raise ValueError("'{0}' is not a valid directory.".foramt(
                os.path.dirname(fname)))

        # Dump the structure in a file
        with open(fname, "wb") as csvfile:
            gwriter = csv.writer(csvfile, delimiter=";",
                                 quotechar="'", quoting=csv.QUOTE_MINIMAL)
            gene_list = ["GENES", ""]
            chr_list = ["CHRS", ""]
            for rs_id in self.snpid:
                gene_list.append("/".join(list(self._gid.get(rs_id, []))))
                chr_list.append("/".join(list(self._cid.get(rs_id, []))))
            gwriter.writerow(chr_list)
            gwriter.writerow(gene_list)
            gwriter.writerow(["FID", "IID"] + self.snpid.tolist())
            for iid, fid, values in zip(self.iid, self.fid, self.data):
                gwriter.writerow([fid, iid] + values.tolist())

