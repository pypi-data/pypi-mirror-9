from mgkit.io import gff
import pandas as pd
import math
from shapely import geometry
import numpy as np
import seaborn as sns
import mgkit.counts as mcounts
import itertools

bac_id = 2
arc_id = 2157
fun_id = 4751

load_htseq = mcounts.load_htseq_counts


def add_counts(infos, iterator, tx, anc_id=None, rank=None, gene_map=None, ex_anc_id=None):
    newcounts = {}
    for uid, count in iterator:
        try:
            gene_id, taxon_id = infos[uid]
        except KeyError:
            continue

        if gene_map is not None:
            try:
                gene_ids = gene_map[gene_id]
            except KeyError:
                continue
        else:
            gene_ids = [gene_id]

        if ex_anc_id is not None:
            if tx.is_ancestor(taxon_id, ex_anc_id):
                continue
        if anc_id is not None:
            if not tx.is_ancestor(taxon_id, anc_id):
                continue
        if rank is not None:
            taxon_id = tx.get_ranked_taxon(taxon_id, rank).taxon_id

        for map_id in gene_ids:
            key = (map_id, taxon_id)

            try:
                newcounts[key] += count
            except KeyError:
                newcounts[key] = count

    return pd.Series(newcounts)


def project_point(p):
    """Maps (x,y,z) coordinates to planar-simplex."""
    a = p[0]
    b = p[1]
    c = p[2]
    x = b + (c / 2.)
    y = math.sqrt(3) / 2. * c
    return (x, y)


def draw_circles_ternary(ax, sdata, tx, csize=200, alpha=.5, sizescale=None,
                         order=None):

    sdata = sdata.div(sdata.sum(axis=1), axis=0)

    if order is None:
        order = sdata.index

    for taxon_id in order:
        coord = sdata.loc[taxon_id]
        if tx.is_ancestor(taxon_id, arc_id):
            c = '#4daf4a'
        elif tx.is_ancestor(taxon_id, bac_id):
            c = '#e41a1c'
        else:
            'black'
        x, y = project_point(coord)
        ax.scatter(
            x,
            y,
            c=c,
            alpha=alpha,
            linewidths=0.,
            s=csize * (sizescale[taxon_id] if sizescale is not None else 1)
        )


def draw_triangle_grid(ax, labels=['LAB', 'SAB', 'EAB'], styles=['-.', ':', '--'], linewidth=1.):

    lines = geometry.LineString(
        [(0, 0), (0.5, math.sqrt(3) / 2), (1, 0), (0, 0)]
    )

    if styles is None:
        ax.plot(*lines.xy, linewidth=linewidth, color='k')
    else:
        for index, style in zip(range(3), styles):
            ax.plot(lines.xy[0][index:index+2], lines.xy[1][index:index+2], linewidth=linewidth, color='k', linestyle=style)

    ax.set_ylim((-0.1, 1.0))
    ax.set_xlim((-0.1, 1.1))
    ax.set_axis_off()

    fontdict = {'fontsize': 15}

    ax.text(-0.05, -0.05, labels[0], fontdict=fontdict)
    ax.text(1.0, -0.05, labels[1], fontdict=fontdict)
    ax.text(0.5 - 0.025, math.sqrt(3) / 2 + 0.05, labels[2], fontdict=fontdict)

    fontdict = {'fontsize': 12}

    for x, y in zip(np.arange(0.1, math.sqrt(3) / 2, math.sqrt(3) / 2 / 10), np.arange(0.1, 1., 0.1)):
        line = geometry.LineString([(0, x), (1, x)])
        points = line.intersection(lines)
        line = geometry.LineString(points)
        ax.plot(*line.xy, color='k', linestyle=':' if styles is None else styles[0], linewidth=linewidth * 0.75)
        ax.text(
            points.geoms[0].x - 0.05,
            points.geoms[0].y,
            "{0:.0f}".format(y * 100),
            fontdict=fontdict
        )

        line = geometry.LineString([points.geoms[0], (y, 0)])
        ax.plot(*line.xy, color='k', linestyle=':' if styles is None else styles[2], linewidth=linewidth * 0.75)
        ax.text(y, - 0.05, "{0:.0f}".format((1 - y) * 100), fontdict=fontdict)

        line = geometry.LineString([points.geoms[1], (1.-y, 0)])
        ax.plot(*line.xy, color='k', linestyle='-' if styles is None else styles[1], linewidth=linewidth * 0.75)
        ax.text(
            points.geoms[1].x + 0.025,
            points.geoms[1].y,
            "{0:.0f}".format((1 - y) * 100),
            fontdict=fontdict
        )


def draw_1d_grid(ax, labels=['LAB', 'SAB']):

    ax.set_ylim((-1.1, 1.1))
    ax.set_xlim((-0.1, 1.1))
    ax.set_axis_off()

    fontdict = {'fontsize': 15}

    ax.text(-0.075, -.05, labels[0], fontdict=fontdict)
    ax.text(1.025, -.05, labels[1], fontdict=fontdict)

    fontdict = {'fontsize': 12}

    ty = 1.0
    by = -1.0

    lines = geometry.LineString([(0, 0), (1, 0)])
    ax.plot(*lines.xy, linewidth=1, color='k')

    for x in np.arange(0.1, 1., 0.1):
        line = geometry.LineString([(x, by), (x, ty)])
        ax.plot(*line.xy, color='k', linestyle=':')
        ax.text(
            x - 0.01,
            by - .75,
            "{0:.0f}".format(x * 100),
            fontdict=fontdict
        )
        ax.text(
            x - 0.01,
            ty + .25,
            "{0:.0f}".format((1 - x) * 100),
            fontdict=fontdict
        )


def draw_circles(ax, sdata, tx, csize=200, alpha=.5, sizescale=None,
                 order=None):

    sdata = sdata.div(sdata.sum(axis=1), axis=0)

    if order is None:
        order = sdata.index

    for taxon_id in order:
        coord = sdata.loc[taxon_id]
        if tx.is_ancestor(taxon_id, arc_id):
            c = '#4daf4a'
        elif tx.is_ancestor(taxon_id, bac_id):
            c = '#e41a1c'
        else:
            'black'
        a, b = coord
        if a > b:
            x = 1 - a
        else:
            x = b
        ax.scatter(
            x,
            0,
            c=c,
            alpha=alpha,
            linewidths=0.,
            s=csize * (sizescale[taxon_id] if sizescale is not None else 1)
        )


def col_func_firstel(key, colors=None):
    if colors is None:
        return 'black'

    return colors[key[0]]


def col_func_name(key, func=None, colors=None):
    if (colors is None):
        return 'black'

    if func is not None:
        key = func(key)

    return colors[key]


def col_func_taxon(taxon_id, taxonomy=None, anc_ids=(arc_id, bac_id, fun_id), colpal=sns.color_palette('hls', 3)):
    for anc_id, color in zip(anc_ids, colpal):
        if taxonomy.is_ancestor(taxon_id, anc_id):
            return color
    return 'black'


def draw_circles_general(ax, sdata, col_func=col_func_firstel, csize=200, alpha=.5, sizescale=None,
                         order=None, linewidths=0., edgecolor='none'):

    #normalize data (ternary plots requires that the sum of a row is 1)
    sdata = sdata.div(sdata.sum(axis=1), axis=0)

    if order is None:
        order = sdata.index

    for key in order:
        coord = sdata.loc[key]
        c = col_func(key)
        #ternary plot
        if len(coord) == 3:
            x, y = project_point(coord)
        #1D plot
        else:
            a, b = coord
            if a > b:
                x = 1 - a
            else:
                x = b
            y = 0.
        ax.scatter(
            x,
            y,
            c=c,
            alpha=alpha,
            linewidths=linewidths,
            edgecolor=edgecolor,
            s=csize * (sizescale[key] if sizescale is not None else 1)
        )
