"""
This module deals with count data, from loading HTSeq-count output to
manipulation and testing.
"""

from __future__ import division

import logging
import itertools
import pandas
import numpy
import pickle
import scipy.stats

LOG = logging.getLogger(__name__)


def load_htseq_counts(f_handle):
    """
    Loads an HTSeq-count result file

    :param (file or str) f_handle: file handle or string with file name

    :return dict: a dictionary with the counts
    """
    if isinstance(f_handle, str):
        f_handle = open(f_handle, 'r')

    LOG.info("Loading HTSeq-count file %s", f_handle.name)
    skip = ['no_feature', 'ambiguous', 'too_low_aQual', 'not_aligned',
            'alignment_not_unique']

    counts = {}

    for line in f_handle:
        gene, count = line.split('\t')
        if gene.startswith('__') or (gene in skip):
            continue
        cnt = int(count.strip())

        try:
            counts[gene] += cnt
        except KeyError:
            counts[gene] = cnt

    return counts


def scale_data(dataset, d_sum, mean):
    s_data = {}
    for ko_id, counts in dataset.iteritems():

        s_counts = {}
        for taxon, count in counts.iteritems():
            s_counts[taxon] = float(count) / (d_sum / mean)

        s_data[ko_id] = s_counts

    return s_data


def group_by_category(counts, mapping):
    log = logging.getLogger(__name__)

    new_cnt = dict(
        (x, {}) for x in set(itertools.chain(*mapping.values()))
    )

    log.info("Grouping %d counts in %d categories", len(counts), len(new_cnt))

    for ko_id, ctable in counts.iteritems():
        if not ko_id in mapping:
            # logging.debug("%s not mapped", ko_id)
            continue
        for taxon, value in ctable.iteritems():
            for cat in mapping[ko_id]:
                try:
                    new_cnt[cat][taxon] += value
                except KeyError:
                    new_cnt[cat][taxon] = value
    return new_cnt


def group_dataframe_by_root_taxon(counts, tmap):
    """
    Takes a DataFrame instance (IDxTAXA) and sum the values of all rows (ids)
    of the columns (taxa) belonging to each root taxon in tmap.

    * counts: a DataFrame instance with counts in the form (IDxTAXA)
    * tmap: a root taxon map created with taxon.group_by_root(only_names=True)

    returns a new instance of DataFrame with the same number of rows as counts
    and the number of keys in the tmap dictionary
    """
    columns = counts.columns

    root_counts = pandas.DataFrame(index=counts.index,
                                   columns=sorted(tmap.keys()))

    for root, taxa in tmap.items():
        #only take the columns that belong to a lineage
        root_cols = columns & ([root] + taxa)
        root_counts[root] = counts.ix[:, root_cols].sum(1)

    return root_counts


def group_dataframe_by_category(counts, mapping):
    """
    Takes a DataFrame instance in the form (IDxTAXA) and a mapping dictionary
    for the categories. All elements of counts will be mapped to the mapping
    values, summing values belonging to the same (MAPID, TAXON) element.

    * counts: a DataFrame instance with counts in the form (IDxTAXA)
    * mapping: a dictionary whose keys are the same, or a subset of counts
      rows, and the values are iterables of ids to which the key belong to.

    returns a DataFrame instance with the same number of rows as mapping
    values and the same number of rows as *counts*
    """

    mapped_categories = set(itertools.chain(*mapping.values()))

    mapped = pandas.DataFrame(index=sorted(mapped_categories),
                              columns=counts.columns)
    mapped.fillna(0, inplace=True)

    for column, series in counts.iterkv():
        #no reason to do a lookup over genes with no counts
        for idx, value in series[series > 0].iterkv():
            try:
                mappings = mapping[idx]
            except KeyError:
                continue
            for mapped_id in mappings:
                # print mapped.ix[mapped_id, column]
                mapped.ix[mapped_id, column] += value
                # print value
                # print mapped.ix[mapped_id, column]

    return mapped


def filter_counts_by_root(counts, tgroup, root):
    """
    Return only counts belonging to a taxon root (root), mapped from
    taxon.group_by_root (tgroup)
    """
    new_cnt = {}
    new_taxons = set()
    for gene, ctable in counts.items():
        new_cnt[gene] = {}
        for t1, v1 in ctable.items():
            if (not t1 in tgroup) and (t1 != root):
                continue
            new_cnt[gene][t1] = v1
            new_taxons.add(t1)
    return new_cnt, new_taxons


def scale_data_frames(data1, data2):
    data1_sum = data1.sum().sum()
    data2_sum = data2.sum().sum()
    data_mean = numpy.mean([data1_sum, data2_sum])

    data1 = data1 / (data1_sum / data_mean)
    data2 = data2 / (data2_sum / data_mean)

    return data1, data2


def scale_data_frame(data, data_mean):
    """
    Scale DataFrame, given the mean of the sums of all datasets
    """

    data_sum = data.sum().sum()

    return data / (data_sum / data_mean)


def scale_fpkm_data_frame(data, data_tot, gene_len, data_mean=None, scale=True):
    """
    Scale DataFrame using FPKM (formula from cufflink)
    counts are first scaled to make them comparable

    data: DataFrame
    data_tot: sum of all counts in the data sets
    gene_len: DataFrame containing gene lengths (same columns and rows as data)
    data_mean: mean of all data sets sums
    scale: if the the data needs to be scaled with scale_data_frame first
    """
    if scale and data_mean:
        data = scale_data_frame(data, data_mean)

    data_sum = data.sum().sum()

    const = 10**9

    data = const * data / (gene_len * data_tot)

    return data.fillna(0)


def scale_fpkm_data_frames(data1, data2, gene_len, scale_first=True):
    """
    Scale DataFrames using FPKM (formula from cufflink)
    counts are first scaled to make them comparable
    """
    if scale_first:
        data1, data2 = scale_data_frames(data1, data2)
    data1_sum = data1.sum().sum()
    data2_sum = data2.sum().sum()
    total_sum = data1_sum + data2_sum

    const = 10**9

    data1 = const * data1 / (gene_len * total_sum)
    data2 = const * data2 / (gene_len * total_sum)
    data1.fillna(0, inplace=True)
    data2.fillna(0, inplace=True)

    return data1, data2


def get_gene_len(len_dict, data):
    LOG.info("Making gene length matrix from %d profiles", len(len_dict))
    gl = pandas.DataFrame(index=data.index, columns=data.columns)
    for name, length in len_dict.iteritems():
        name = name.replace('-nr', '')
        try:
            #old format: KO_taxon(-nr)
            ko_id, taxon = name.split('_')
        except ValueError:
            #new format: KO_taxonid_taxon(-nr)
            ko_id, taxon_id, taxon = name.split('_')
        if (not taxon in data.columns) or (not ko_id in data.index):
            continue
        gl.set_value(ko_id, taxon, length)
    return gl


def batch_load_htseq_counts(count_files, cut_name='-all_data-htseq-count-ko_idx.txt'):
    """
    Loads a list of htseq count result files and returns a DataFrame (IDxSAMPLE)
    """
    counts = {}

    for fname in count_files:
        counts[fname.replace(cut_name, '')] = load_htseq_counts(fname)

    return pandas.DataFrame.from_dict(counts)


def batch_load_gene_length(gene_len_files):
    """
    Loads a list of dictionary pickle files and return the merged dictionary
    """
    len_dict = {}

    for fname in gene_len_files:
        len_dict.update(pickle.load(open(fname, 'r')))

    return len_dict


def batch_scale_dataframe(counts):

    df_denom = counts.sum() / counts.sum().mean()

    return counts / df_denom


def batch_scale_fpkm(data, gene_len):
    """
    gene_len is a Series instance that is the result of combine_dicts run on
    a ko_idx->name (profile name) and batch_load_gene_length
    """

    gene_len = gene_len[data.index]

    const = 10**9

    data = (const * data).div(gene_len * data.sum().sum(), axis=0)

    return data.fillna(0)


def scale_factor_deseq(dataframe):
    """
    """
    #calc the genes geometric mean over all sample
    gmean = dataframe.apply(scipy.stats.gmean, axis=1)
    #keeps only the genes whose geometric mean is > 0
    gmean = gmean[gmean > 0]

    sample_factors = {}

    #calc the scaling factor for each sample
    for sample, genes in dataframe.iterkv():

        scale_factor = numpy.median(genes.loc[gmean.index] / gmean)

        sample_factors[sample] = scale_factor

    return pandas.Series(sample_factors)


def scale_deseq(dataframe):

    scale_factors = scale_factor_deseq(dataframe)

    return dataframe / scale_factors
