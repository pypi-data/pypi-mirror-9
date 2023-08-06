#! /usr/bin/env python
##########################################################################
# Brainomics - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import print_function
import numpy as np
import os
import zipfile
import tempfile
import shutil
import logging
import numpy

# PLINKIO import
import plinkio

# CWBROWSER import
from cwbrowser.cw_connection import CWInstanceConnection

# GENIBABEL import
from genibabel.gtypes import RawGenotype


# Set the logger
logger = logging.getLogger(__file__)


def imagen_genotype_measure(login, password, patients_ids=None,
                                chr_name=None,
                                gene_names=None,
                                snp_ids=None,
                                pws=None,
                                gwide=False,
                                status="qc", wave=2,
                                download_local_path=None,
                                postload_op='frc_imput'):
    """ Method that returns the genotyped mesures from imagen2 database and
    metagen database.

    The address of the servers are hardcoded:
        * "https://imagen2.cea.fr/database/"
        * "http://mart.intra.cea.fr/metagen_hg19_snp138/"

    As you can see we use the 'hg19_snp138' template.

    In order to querie those database, the rql_download package must be installed.
        * pip install --user cwbrowser

    The plinkio package must be installed too.
        * pip install --user python-plinkio

    Parameters
    ----------
    login (mandatory)
        your login on the imagen2 database.
    password (mandatory)
        your password on the imagen2 database.
    patients_ids: list of str (optional default None)
        a list of patient from which we want to access the genotype measures.
    chr_name: str (optional default None)
        a chromosome name from which we want to access the genotype measures.
    gene_names: list of str (optional default None)
        a list of genes from which we want to access the genotype measures.
    snp_ids: list of str (optional default None)
        a list of snps from which we want to access the genotype measures.
    pws: Pathways object. (see Pathways from genotype.pathways) default is None.
    gwide:boolean (default False). If True the whole genotyping data are
        requested and in that case snp_ids and gene_names are ignored.
    wave: int (optional default 2)
        the genotype wave we are interested in.
    status: str (optional default 'QC')
        the type of dataset we want to access.
    download_local_path: string; path where to download plink file from the
        imagen server. If None a path from the local fs is returned; None is
        only available from internal NeuroSpin only
    postload_op: str (optional, default 'frc_imput')
        could be 'frc_imput' (replace nan by median), None (nop).

    Return
    ------
    genodata: RawGenotype
        a structure that contains the genotype data and associated
        metainformation.

    Raises
    ------
    ValueError: if more than one dataset is found raise this exception.
    """

    imagen_url = "https://imagen2.cea.fr/database/"
    meta_url = "http://mart.intra.cea.fr/metagen_hg19_snp138/"
    # Query the following imagen CW server to get the genotyping data file
    logger.info("The imagen server url is '%s'.", imagen_url)
    logger.info("The metagen server url is '%s'.", meta_url)

    # Create a connection to the imagen server
    logger.debug("Contact the imagen server to get the required dataset.")
    connection = CWInstanceConnection(imagen_url, login, password,
                                      realm="Imagen")
    logger.debug("Connected...")

    # Get the genotype data
    if download_local_path is not None:
        raise NotImplementedError
        #logger.debug("Use the CWSearch and sftp to get the dataset.")
        #rql = "Any G Where G is GenomicMeasure, G type '{0}'".format(status)
        #logger.debug("RQL:: '%s'.", rql)
        #logger.debug("DEST:: '%s'.", download_local_path)
        #datasets = connection.execute_with_fuse(rql2, download_local_path,
        #                                        timer=1)
    else:
        logger.debug("Assume you have a direct access to the data.")
        rql = ("Any P Where G is GenomicMeasure, G type '{0}', "
               "G identifier 'qc_subjects_all_snps_wave{1}', "
               "G chromset 'all', G filepath P".format(status, wave))
        logger.debug("RQL:: '%s'.", rql)
        datasets = connection.execute(rql)

    # We expect only one dataset
    if len(datasets) != 1:
        raise ValueError(
            "Found '{0}' datasets while expecting only one.".format(
                len(datasets)))
    logger.info("The genotype dataset is '%s'.", datasets[0])

    # Unpack the zip content
    logging.info("Unzip the genotype dataset.")
    temp_folder = tempfile.mkdtemp()
    logging.debug("TEMP:: '%s'.", temp_folder)
    file_open = open(datasets[0][0], "rb")
    zip_open = zipfile.ZipFile(file_open)
    zip_content = zip_open.namelist()
    bed_fnames = [x for x in zip_content if x.endswith(".bed")]
    bim_fnames = [x for x in zip_content if x.endswith(".bim")]
    fam_fnames = [x for x in zip_content if x.endswith(".fam")]
    if len(bed_fnames) != 1 or len(bim_fnames) != 1 or len(fam_fnames) != 1:
        file_open.close()
        raise ValueError(
            "The '{0}' genotype file is corrupted.".format(datasets[0][0]))
    zip_open.extract(bed_fnames[0], temp_folder)
    zip_open.extract(bim_fnames[0], temp_folder)
    zip_open.extract(fam_fnames[0], temp_folder)
    prefix_file = os.path.join(temp_folder, os.path.splitext(bed_fnames[0])[0])
    bed_file = os.path.join(temp_folder, bed_fnames[0])
    bim_file = os.path.join(temp_folder, bim_fnames[0])
    fam_file = os.path.join(temp_folder, fam_fnames[0])
    logging.debug("BED:: '%s'.", bed_file)
    logging.debug("BIM:: '%s'.", bim_file)
    logging.debug("FAM:: '%s'.", fam_file)

    # Create a connection to the metagen server
    logger.debug("Contact the metagen server to get the required dataset.")
    connection = CWInstanceConnection(meta_url, "anon", "anon")
    logger.debug("Connected...")

    # Get the snps of interest
    if not gwide:   # case whole dataset is requested
        logger.debug("Get the snps of interest.")
        snps_of_interest = dict()
        for k in ['rs', 'pos', 'chr', 'gene']:
            snps_of_interest[k] = []
        # case whene pws is not None infer gene list (duplicated code after)
        if pws:
            geneset = []
            for pw in pws:
                geneset.extend(pw['genes'].tolist())
            geneset = list(set(geneset))
            for name in geneset:
                logging.info("   Request meta for gene: %s",name)
                rset = connection.execute(
                    "Any I,C,P Where G is Gene, G name '{0}', G snps S, "
                    "S rs_id I, S chromosomes CI, CI name C, "
                    "S start_position P".format(name))
                for x in rset:
                    #print(x)
                    snps_of_interest['rs'].append(x[0])
                    snps_of_interest['chr'].append(x[1])
                    snps_of_interest['pos'].append(x[2])
                    snps_of_interest['gene'].append(name)

        if snp_ids:
            for s in snp_ids:
                snps_of_interest['rs'].append(s)
                snps_of_interest['chr'].append('')
                snps_of_interest['pos'].append(-1)
                snps_of_interest['gene'].append('')

        if gene_names:
            gene_names = list(set(gene_names)) # kill redundancy
            for name in gene_names:
                logging.info("   Request meta for gene: %s",name)
                rset = connection.execute(
                    "Any I,C,P Where G is Gene, G name '{0}', G snps S, "
                    "S rs_id I, S chromosomes CI, CI name C, "
                    "S start_position P".format(name))
                for x in rset:
                    #print(x)
                    snps_of_interest['rs'].append(x[0])
                    snps_of_interest['chr'].append(x[1])
                    snps_of_interest['pos'].append(x[2])
                    snps_of_interest['gene'].append(name)

        if chr_name:
            # Check validity of input chromosome names against this set
            valid_cnames = set(["chr"+str(n) for n in range(1,23)]+["chrX","chrY"])
            if chr_name not in valid_cnames:
                raise ValueError("Bad chromosome name: {}\n"
                                "Valid names: {}".format(chr_name, valid_cnames))
            
            rset = connection.execute(
                    'Any SID, CN WHERE C is Chromosome, C name "{}", '
                    'C name CN, C snps S, S rs_id SID'.format(chr_name))
            for x in rset:
                snps_of_interest['rs'].append(x[0])
                snps_of_interest['chr'].append(x[1])
                snps_of_interest['pos'].append(-1)
                snps_of_interest['gene'].append('')

        if len(snps_of_interest['rs']) != len(set(snps_of_interest['rs'])):
            print('Specific code to manage rsID with multiple chrom locus')
            raise NotImplementedError
        #logger.debug("The required snps of interest are '%s'.",
        #                                            repr(snps_of_interest))
    else:
        logger.debug("Get the whole snps available from the genotype file.")
        snps_of_interest = None  # genotype_measure will understand all snps
        logger.info("Get the whole snps available. GenomeWide mode")

    # Now get the measures with plinkio package
    # snps_of_interest will be a valid list of snps or None(for gwide)
    genodata, snpid, iid, fid, cid, gid = genotype_measure(
                                              prefix_file, snps_of_interest)

    # Remove temp folder
    shutil.rmtree(temp_folder)

    # Store the result in a genibabel structure
    genodata = RawGenotype(genodata, iid, snpid, fid, cid, gid, pws)

    return genodata


def _wrapup_meta(snpid, meta):
    """ Method to organize meta data to feed the rawGenotype instances
    snpid: list of rs_id
    meta: dict of list. keys rs_id, chr pos, gene
    Parameters:
    -----------
    snpid : nd.array (unordered list of snps)
    snp_list: info on snps obtained from meta

    Return
    ------
    snpid : nd.array ordered by genomic position
    snp_list: filtered information with respect to snp_id ordered w/ snpid
    """
    #
    logging.info("Wrapping up meta information in the rawgenotype object")
    if snpid != []:
        # filter the only available snps
        # snpid snps have to exist in meta['rs']
        meta_index = []
        for i in snpid:
            meta_index.append(meta['rs'].index(i))
        #now subset the different lists
        meta['rs'] = [str(meta['rs'][i]) for i in meta_index]
        meta['chr'] = [unicode(meta['chr'][i]) for i in meta_index]
        meta['pos'] = [meta['pos'][i] for i in meta_index]
        meta['gene'] = [unicode(meta['gene'][i]) for i in meta_index]
        # sort along with two keys
        ind = numpy.lexsort((meta['pos'], meta['chr']))
        #fix every lists
        for k in meta.keys():
            meta[k] = [meta[k][j] for j in ind]
        snpid = meta['rs']

    return snpid, meta


def genotype_measure(geno_filename, snp_list=None,
                     postload_op='frc_imput'):
    """ Method that returns the genotyped mesures files and snp list.

    Parameters
    ----------
    geno_filename: str (mandatory)
        the plink prefix filename (no extension bed bim fam).
    snp_list: list of str (optional, default None)
        default is None meaning all available snps.
    postload_op: str (optional, default 'frc_imput')
        could be 'frc_imput' (replace nan by median), None (nop).

    Return
    ------
    genodata: array
        the genotype data.
    snpid: list of str
        the snps identifiers (the columns of the 'genodata' array).
    iid: list of str
        the subject identifiers (the rows of the 'genodata' array).
    fid: list of str
        the family identifiers.
    cid: dict
        the chromosomes associated with the snps.
    gid: dict
        the genes associated with the snps.
    """
    # Get the genotype data associated to the desired snps
    logging.info("Starting grep snps from genotyping file %s",
                 os.path.basename(geno_filename))
    plinkgenotype = plinkio.Genotype(geno_filename)
    if snp_list:
        # Hack plinkio since it does not support unicode
        # Hack plinkio since it crash when asking a non existing snps
        # Hack plinkio since it do not deal with empty snps request
        splinkio_snp_list = plinkgenotype.snpList().tolist()
        snpid = list(set(splinkio_snp_list) & set(snp_list['rs']))
        snpid = [str(x) for x in snpid]
        if snpid == []:
            return np.empty((0,)), [], [], [], {}, {}
        # adjust/align the meta info from snp_list and snpid
        snpid, snp_list = _wrapup_meta(snpid, snp_list)
        genodata = plinkgenotype.snpGenotypeByName(snpid)
    else:
        genodata = plinkgenotype.snpGenotypeAll()
        snpid = plinkgenotype.snpList()

    if postload_op == 'frc_imput':
        genodata = impute_by_med(genodata, nan_symbol=128)

    # Get metadata associated with the measures
    iid = plinkgenotype.getOrderedSubsetIndiv()
    fid = plinkgenotype.getOrderedSubsetFamily()
    #hack to fix a bug in plinkio
    fid = ["%012d" % (int(i)) for i in fid]
    logging.info("Finished grep snps from genotyping file %s",
                 os.path.basename(geno_filename))
    
    if snpid == [] or not snp_list:
        cid = {}
        gid = {}
    else:
        cid = {}
        for sname, cname in zip(snp_list['rs'], snp_list['chr']):
            cid.setdefault(sname, []).append(cname)

        gid = {}
        for sname, gname in zip(snp_list['rs'], snp_list['gene']):
            gid.setdefault(sname, []).append(gname)

    return genodata, snpid, iid, fid, cid, gid


def impute_by_med(data, verbose=0, nan_symbol=128):
    """ This function to impute genotype data read from plink file.
    See plink web site for bed/bim/fam format.
    This function perform an imputation of the poor. Mising data are taken as
    the mean acccros the subject for a give rsname. Usual imputation considers
    the genotype context accross the neighbor rsname and HapMap or 1kG
    resources (see Abecassis MaCH code and others).
    """
    
    # replace nan_symbol values by median of non-nan_symbol values of the column
    for i in range(data.shape[1]):
        non_nan_values = data[:, i][data[:,i] != nan_symbol]
        if len(non_nan_values) == 0:
            non_nan_values = 0
        rounded_median = int(round(np.median(non_nan_values)))
        data[:, i][data[:,i] == nan_symbol] = rounded_median

    return data
