from ..plots import *
from matplotlib import patches as mpatches
import numpy as np
import seaborn as sns


def prop_to_coordinates(proportions, start, end):
    "for barchart (tested on polar coordinates)"
    widths = proportions * (end - start)
    starts = numpy.insert((widths.cumsum() + start)[:-1], 0, start)
    return starts, widths


def plot_bars(ax, start, end, values, bottom, size=None, height=1., alpha=.5, color=None, linewidth=0.1):
    if size is None:
        size = sum(values)

    if color is None:
        color = sns.color_palette("hls", len(values))

    proportions = numpy.array(values) / size

    lefts, widths = prop_to_coordinates(proportions, start, end)

    ax.bar(lefts, [height] * len(proportions), width=widths, bottom=bottom, alpha=alpha, color=color, linewidth=linewidth)

    #returns the coordinates
    return zip(lefts, widths.cumsum())


def draw_module(module, ax, scoord=(0., 0.), rsize=(5., 2.), xpad=2.,
                gstyle=None, cstyle=None, tstyle=None, astyle=None):

    base_box_style = dict(
        alpha=.5,
        color='green'
    )

    base_text_style = dict(
        size=20,
        ha='center',
        va='center'
    )

    base_arrow_style = dict(
        fc='red',
        ec=None
    )

    if tstyle is None:
        tstyle = base_text_style.copy()
    else:
        tstyle = dict(base_text_style, **tstyle)
    if astyle is None:
        astyle = base_arrow_style.copy()
    else:
        astyle = dict(base_arrow_style, **astyle)
    if gstyle is None:
        gstyle = base_box_style.copy()
    else:
        gstyle = dict(base_box_style, **gstyle)
    if cstyle is None:
        cstyle = base_box_style.copy()
    else:
        cstyle = dict(base_box_style, **cstyle)

    curr_x, curr_y = scoord
    rect_w, rect_h = rsize

    arrow_y = rect_h / 2.

    ax.set_ylim(0, rect_h)

    box_x = []

    text_list = {}

    for idx, (ko_ids, (comp1, comp2)) in enumerate(module):
        if idx == 0:
            r = mpatches.Rectangle([curr_x, curr_y], rect_w, rect_h, **cstyle)
            t = ax.text(curr_x + (rect_w / 2.), arrow_y, comp1, **tstyle)
            text_list[comp1] = t
            ax.add_patch(r)
            curr_x += rect_w
            a = mpatches.Arrow(curr_x, arrow_y, xpad, 0, **astyle)
            ax.add_patch(a)
            curr_x += xpad

        box_x.append(curr_x)

        r = mpatches.Rectangle([curr_x, curr_y], rect_w, rect_h, **gstyle)
        t = ax.text(curr_x + (rect_w / 2.), arrow_y, ko_ids[0], **tstyle)
        text_list[ko_ids] = t
        ax.add_patch(r)
        curr_x += rect_w
        a = mpatches.Arrow(curr_x, arrow_y, xpad, 0,  **astyle)
        ax.add_patch(a)
        curr_x += xpad

        r = mpatches.Rectangle([curr_x, curr_y], rect_w, rect_h, **cstyle)
        t = ax.text(curr_x + (rect_w / 2.), arrow_y, comp2, **tstyle)
        text_list[comp2] = t
        ax.add_patch(r)
        curr_x += rect_w
        if idx < (len(module) - 1):
            a = mpatches.Arrow(curr_x, arrow_y, xpad, 0,  **astyle)
            ax.add_patch(a)
            curr_x += xpad

    ax.set_xlim(scoord[0], curr_x)

    return box_x, text_list


def draw_barchart(values, ax, startx, endx, starty, endy, width=None, err=None,
                  ecolor='k', colors=sns.color_palette('hls', 4)):
    step = (endx - startx) / float(len(values))
    if width is None:
        width = step
    lefts = np.arange(startx, endx, step)

    yscale = (endy - starty)

    svalues = (values / values.max()) * yscale
    #print values
    #print len(lefts), svalues
    err = err / values * yscale
    ax.bar(lefts, svalues, bottom=starty, width=width, yerr=err, ecolor=ecolor, color=colors)


def plot_module(reactions, fig, gs, gsrow, gstyle=None, cstyle=None, tstyle=None, astyle=None):

    rect_h = 1
    rect_w = rect_h * 2

    base_box_style = dict(
        alpha=.5,
        color='green'
    )

    base_text_style = dict(
        size=20,
        ha='center',
        va='center'
    )

    base_arrow_style = dict(
        fc='red',
        ec=None
    )

    if tstyle is None:
        tstyle = base_text_style.copy()
    else:
        tstyle = dict(base_text_style, **tstyle)
    if astyle is None:
        astyle = base_arrow_style.copy()
    else:
        astyle = dict(base_arrow_style, **astyle)
    if gstyle is None:
        gstyle = base_box_style.copy()
    else:
        gstyle = dict(base_box_style, **gstyle)
    if cstyle is None:
        cstyle = base_box_style.copy()
    else:
        cstyle = dict(base_box_style, **cstyle)

    data = dict(compounds=[], genes=[])

    col_count = 0

    for idx, (ko_ids, (comp1, comp2)) in enumerate(reactions):

        if idx == 0:
            ax = fig.add_subplot(gs[gsrow, col_count])

            r = mpatches.Rectangle([0, 0], rect_w, rect_h, **cstyle)
            t = ax.text(rect_w / 2., rect_h / 2., comp1, **tstyle)
            ax.add_patch(r)
            data['compounds'].append((col_count, comp1, t))
            col_count += 1
            ax.set_xlim(0, rect_w)
            ax.set_ylim(0, rect_h)
            ax.set_axis_off()

        ax = fig.add_subplot(gs[gsrow, col_count])

        r = mpatches.Rectangle([0, 0], rect_w, rect_h, **gstyle)
        t = ax.text(rect_w / 2., rect_h / 2., ko_ids[0], **tstyle)
        ax.add_patch(r)
        data['genes'].append((col_count, ko_ids, t))
        col_count += 1
        ax.set_xlim(0, rect_w)
        ax.set_ylim(0, rect_h)
        ax.set_axis_off()

        ax = fig.add_subplot(gs[gsrow, col_count])

        r = mpatches.Rectangle([0, 0], rect_w, rect_h, **cstyle)
        t = ax.text(rect_w / 2., rect_h / 2., comp2, **tstyle)
        ax.add_patch(r)
        data['compounds'].append((col_count, comp2, t))
        col_count += 1
        ax.set_xlim(0, rect_w)
        ax.set_ylim(0, rect_h)
        ax.set_axis_off()

    return data


def plot_barcharts(genes, data, columns, fig, gs, gsrow, ecolor='k', colors=None, sharey=False,
                   test=None, thres=0.05):

    max_x = 1.
    if colors is None:
        colors = sns.color_palette('Paired', len(columns))

    prev_ax = None

    for idx, gene_ids, textobj in genes:
        gene_ids = list(gene_ids)

        step = max_x / float(len(columns))

        values = [
            data[column[0]][column[1]].ix[gene_ids].sum(axis=0).mean()
            for column in columns
        ]
        err = [
            data[column[0]][column[1]].ix[gene_ids].sum(axis=0).std()
            for column in columns
        ]

        lefts = np.arange(0, max_x, step)

        if all(np.isnan(x) for x in values):
            continue
        # print values

        ax = fig.add_subplot(gs[gsrow, idx], sharey=prev_ax)

        if sharey:
            prev_ax = ax

        ax.bar(lefts, values, bottom=0, width=step, yerr=err, ecolor=ecolor, color=colors)

        ax.grid(axis='x')
        ax.set_xticklabels(['/'.join(column) for column in columns])
        ax.set_xticks(np.arange(step / 2., max_x, step))

        if test is not None:
            labels = []
            pvals = []
            for colidx in xrange(0, len(columns), len(columns) // 2):
                cond1, cond2 = columns[colidx:colidx+2]

                pvalue = test(
                    data[cond1[0]][cond1[1]].ix[gene_ids].sum(axis=0).dropna(),
                    data[cond2[0]][cond2[1]].ix[gene_ids].sum(axis=0).dropna()
                )[1]
                pvals.append(pvalue)
                if pvalue < thres:
                    labels.append('/'.join(cond1) + '\n*')
                    labels.append('/'.join(cond2) + '\n*')
                else:
                    labels.append('/'.join(cond1))
                    labels.append('/'.join(cond2))
            ax.set_xticklabels(labels)
            ax.set_title(' - '.join(str(x) for x in pvals), fontsize=16)


def change_names(boxes, name_map, fontsize=12):

    for idx, map_ids, text in boxes:
        if isinstance(map_ids, str):
            if '+' in map_ids:
                map_ids = [map_id.strip() for map_id in map_ids.split('+')]
            else:
                map_ids = [map_ids]

        names = set()

        for map_id in map_ids:
            map_names = name_map.get(map_id, map_id)
            if isinstance(map_names, str):
                map_names = [map_names]
            for map_name in map_names:
                names.update(x.strip() for x in map_name.split(';'))

        text.set_text('\n'.join(names))
        text.set_size(fontsize)
