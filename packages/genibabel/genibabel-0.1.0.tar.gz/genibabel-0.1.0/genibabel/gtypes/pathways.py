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


class Pathways(object):
    """ Class to describe a Pathway set.

    Methods
    -------
    csv_export
    get_snp_meta
    

    Attributes
    ----------
    name: str (name of the pathways set)
    origin: str (http reference)
    entry: dict() keys name of one patwhay,value HUGO gene list

    """
    def __init__(self, fn=('/neurospin/brainomics/bio_resources/genesets/'
                          'msigdb-v3.1/c7.go-synaptic.symbols.gmt'),
                 origin="msigdb-v3.1",
                 compound_name='c7.go-synaptic'):
        """ Initialize the RawGenotype class.

        Parameters
        ----------
        fn: path to a valid gmt file (Gene Matrix Transposed file format 
            see http://www.broadinstitute.org/cancer/software/gsea/wiki/index.php/Data_formats
        origin: str database name,
        compound_name: str pathways set name.
        """
        self._fn = fn
        self._origin = origin
        self._compound_name = compound_name
        self._entry = []
        gmtDB = open(fn)
        for line in gmtDB:
            vs = line.rstrip().split("\t")
            setgenes = np.array(vs[2:])
            self._entry.append({"name":vs[0],"link":vs[1],"genes":setgenes})
        gmtDB.close()


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
        return self._entry[index]

    ###########################################################################
    # Private Members
    ###########################################################################


    ###########################################################################
    # Public Members
    ###########################################################################
    def filter(self, min_gen=5, max_gen=50, num_pw=99999):
        """ Apply criteria in place for a subpathway

        Parameters
        ----------
        min_gen: int, min number in the gene list
        max_gen: int, max number in the gene list
        num_pw:  int, max number of pathway to keep
        
        Returns
        -------
        nothing: modification in place
        """
        nentry = []
        n = 0
        for pw in self._entry:
            if n >= num_pw:
                break
            if (len(pw['genes'].tolist()) >= min_gen and
                len(pw['genes'].tolist()) <= max_gen):
                    nentry.append(pw)
                    n += 1
        self._entry = nentry