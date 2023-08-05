"""
This module deals with count data, from loading HTSeq-count output to
manipulation and testing.
"""

from __future__ import division

import logging
import itertools
import pandas

LOG = logging.getLogger(__name__)


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


def scale_by_min_value(data):
    """
    Scale by the minimun sample sum.

    data / (data.sum(axis=0).min() / data.sum(axis=0).sum())
    """

    return data / (data.sum(axis=0).min() / data.sum(axis=0).sum())


def map_counts_to_category(counts, gene_map):
    newcounts = {}
    for gene_id, count in counts.iteritems():
        try:
            map_ids = gene_map[gene_id]
        except KeyError:
            continue

        for map_id in map_ids:
            try:
                newcounts[map_id] += 1
            except KeyError:
                newcounts[map_id] = 1

    return pandas.Series(newcounts)
