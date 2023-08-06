
Exploring the Data
==================

The following section requires that the tutorial has been completed and
the data present in the same directory

Imports
-------

.. code:: python

    #Python Standard Library
    import glob
    import pickle
    
    #External Dependencies (install via pip or anaconda)
    import numpy
    import pandas
    import seaborn
    import matplotlib.pyplot as plt
    
    #MGKit Import
    from mgkit.io import gff, fasta
    from mgkit.mappings import eggnog
    import mgkit.counts, mgkit.taxon, mgkit.snps, mgkit.plots
    import mgkit.snps
Read Necessary Data
-------------------

.. code:: python

    counts = glob.glob('*-counts.txt')
.. code:: python

    snp_data = pickle.load(open('snp_data.pickle', 'r'))
.. code:: python

    taxonomy = mgkit.taxon.UniprotTaxonomy('mg_data/taxonomy.pickle')
.. code:: python

    annotations = {x.uid: x for x in gff.parse_gff('assembly.uniprot.gff')}
.. code:: python

    file_name_to_sample = lambda x: x.split('-')[0]
.. code:: python

    sample_names = {
        'SRR001326': '50m',
        'SRR001325': '01m',
        'SRR001323': '32m',
        'SRR001322': '16m'
    }
Explore Count Data
------------------

Load Taxa Table
~~~~~~~~~~~~~~~

.. code:: python

    taxa_counts = pandas.DataFrame({
        file_name_to_sample(file_name): mgkit.counts.load_sample_counts_to_taxon(
            lambda x: (annotations[x].gene_id, annotations[x].taxon_id),
            mgkit.counts.load_htseq_counts(file_name),
            taxonomy,
            rank='order',
            include_higher=False
        )
        for file_name in counts
    })
Scaling (DESeq method) and Rename Rows/Columns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    taxa_counts = mgkit.counts.scale_deseq(taxa_counts)
.. code:: python

    #The columns are sorted by name, while the rows are sorted in descending order by the first colum (1 meter)
    taxa_counts = taxa_counts.rename(
        index=lambda x: taxonomy[x].s_name,
        columns=sample_names
    ).sort(axis='columns').sort(['01m'], ascending=False)
.. code:: python

    taxa_counts.describe()



.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>01m</th>
          <th>16m</th>
          <th>32m</th>
          <th>50m</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>count</th>
          <td>175.000000</td>
          <td>175.000000</td>
          <td>175.000000</td>
          <td>175.000000</td>
        </tr>
        <tr>
          <th>mean</th>
          <td>20.929504</td>
          <td>24.904741</td>
          <td>22.795858</td>
          <td>26.164316</td>
        </tr>
        <tr>
          <th>std</th>
          <td>49.058657</td>
          <td>66.180170</td>
          <td>60.469850</td>
          <td>67.460110</td>
        </tr>
        <tr>
          <th>min</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>25%</th>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>50%</th>
          <td>3.551386</td>
          <td>3.412944</td>
          <td>3.942751</td>
          <td>3.331821</td>
        </tr>
        <tr>
          <th>75%</th>
          <td>15.981239</td>
          <td>15.927073</td>
          <td>14.193903</td>
          <td>17.492061</td>
        </tr>
        <tr>
          <th>max</th>
          <td>353.954841</td>
          <td>482.362776</td>
          <td>464.456038</td>
          <td>530.592519</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    #Save a CSV to disk
    taxa_counts.to_csv('taxa_counts.csv')
Plots for Top40 Taxa
~~~~~~~~~~~~~~~~~~~~

Distribution of Each Taxon Over Depth
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(15, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        taxa_counts, 
        taxa_counts.index[:40], 
        ax, 
        fonts=dict(fontsize=14),
        data_colours={
            x: color
            for x, color in zip(taxa_counts.index[:40], seaborn.color_palette('hls', 40))
        }
    )
    fig.tight_layout()
    fig.savefig('taxa_counts-boxplot_top40_taxa.pdf')


.. image:: Exploring-Metagenomic-Data_files/Exploring-Metagenomic-Data_21_0.png


Distribution of Taxa by Depth
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(10, 10))
    for column, color in zip(taxa_counts.columns, seaborn.color_palette('Set1', len(taxa_counts.columns))):
        seaborn.kdeplot(
            numpy.sqrt(taxa_counts[column].iloc[:40]),
            color=color,
            label=column,
            shade=True
        )
    ax.legend()
    fig.tight_layout()
    fig.savefig('taxa_counts-distribution_top40_taxa.pdf')


.. image:: Exploring-Metagenomic-Data_files/Exploring-Metagenomic-Data_23_0.png


Heatmap of the Table
^^^^^^^^^^^^^^^^^^^^

.. code:: python

    seaborn.clustermap(taxa_counts.iloc[:40], cbar=True, cmap='Blues')
    fig = plt.gcf()
    fig.savefig('taxa_counts-heatmap-top40.pdf')


.. image:: Exploring-Metagenomic-Data_files/Exploring-Metagenomic-Data_25_0.png


Functional Categories
~~~~~~~~~~~~~~~~~~~~~

Load Necessary Data
^^^^^^^^^^^^^^^^^^^

.. code:: python

    eg = eggnog.NOGInfo()
.. code:: python

    #Just a few to speed up the analysis
    #Should have been downloaded by the full tutorial script
    eg.load_members('COG.members.txt.gz')
    eg.load_members('NOG.members.txt.gz')
    eg.load_funccat('COG.funccat.txt.gz')
    eg.load_funccat('NOG.funccat.txt.gz')
.. code:: python

    #Build mapping Uniprot IDs -> eggNOG functional categories
    fc_map = {
        annotation.gene_id: eg.get_nogs_funccat(annotation.get_mapping('eggnog'))
        for annotation in annotations.itervalues()
    }
Build FC Table
^^^^^^^^^^^^^^

.. code:: python

    fc_counts = pandas.DataFrame({
        file_name_to_sample(file_name): mgkit.counts.load_sample_counts_to_genes(
            lambda x: (annotations[x].gene_id, annotations[x].taxon_id),
            mgkit.counts.load_htseq_counts(file_name),
            taxonomy,
            gene_map=fc_map
        )
        for file_name in counts
    })
Scale the Table and Rename Rows/Columns
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    fc_counts = mgkit.counts.scale_deseq(fc_counts).rename(
        columns=sample_names,
        index=eggnog.EGGNOG_CAT
    )
.. code:: python

    #Save table to disk
    fc_counts.to_csv('fc_counts.csv')
Heatmap to Explore Functional Categories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    seaborn.clustermap(fc_counts, cbar=True, cmap='Greens')
    fig = plt.gcf()
    fig.savefig('fc_counts-heatmap.pdf')


.. image:: Exploring-Metagenomic-Data_files/Exploring-Metagenomic-Data_37_0.png


Explore Diversity
-----------------

Taxa
~~~~

.. code:: python

    pnps = mgkit.snps.get_rank_dataframe(snp_data, taxonomy, min_num=3, rank='order', index_type='taxon')
.. code:: python

    pnps = pnps.rename(
        columns=sample_names,
        index=lambda x: taxonomy[x].s_name
    )
.. code:: python

    pnps.describe()



.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>16m</th>
          <th>32m</th>
          <th>01m</th>
          <th>50m</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>count</th>
          <td>23.000000</td>
          <td>20</td>
          <td>26.000000</td>
          <td>25.000000</td>
        </tr>
        <tr>
          <th>mean</th>
          <td>0.157490</td>
          <td>0</td>
          <td>0.269989</td>
          <td>0.383241</td>
        </tr>
        <tr>
          <th>std</th>
          <td>0.358996</td>
          <td>0</td>
          <td>0.464452</td>
          <td>0.492235</td>
        </tr>
        <tr>
          <th>min</th>
          <td>0.000000</td>
          <td>0</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>25%</th>
          <td>0.000000</td>
          <td>0</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>50%</th>
          <td>0.000000</td>
          <td>0</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>75%</th>
          <td>0.000000</td>
          <td>0</td>
          <td>0.587940</td>
          <td>0.875000</td>
        </tr>
        <tr>
          <th>max</th>
          <td>1.117518</td>
          <td>0</td>
          <td>1.415323</td>
          <td>1.402299</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    #sort the DataFrame to plot them by mean value
    plot_order = pnps.mean(axis=1).sort(inplace=False, ascending=False).index
    
    fig, ax = mgkit.plots.get_single_figure(figsize=(15, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        pnps, 
        plot_order, 
        ax, 
        fonts=dict(fontsize=14, rotation='horizontal'),
        data_colours={
            x: color
            for x, color in zip(plot_order, seaborn.color_palette('hls', len(pnps.index)))
        },
        box_vert=False
    )
    fig.tight_layout()
    fig.savefig('pnps-taxa-boxplot.pdf')


.. image:: Exploring-Metagenomic-Data_files/Exploring-Metagenomic-Data_43_0.png


Functional Categories
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fc_pnps = mgkit.snps.get_gene_map_dataframe(snp_data, taxonomy, min_num=3, gene_map=fc_map, index_type='gene')
.. code:: python

    fc_pnps = fc_pnps.rename(
        columns=sample_names,
        index=eggnog.EGGNOG_CAT
    )
.. code:: python

    fc_pnps.describe()



.. raw:: html

    <div style="max-height:1000px;max-width:1500px;overflow:auto;">
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>16m</th>
          <th>32m</th>
          <th>01m</th>
          <th>50m</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>count</th>
          <td>17.000000</td>
          <td>14</td>
          <td>18.000000</td>
          <td>16.000000</td>
        </tr>
        <tr>
          <th>mean</th>
          <td>0.253276</td>
          <td>0</td>
          <td>0.610984</td>
          <td>0.793588</td>
        </tr>
        <tr>
          <th>std</th>
          <td>0.419100</td>
          <td>0</td>
          <td>0.511969</td>
          <td>0.634869</td>
        </tr>
        <tr>
          <th>min</th>
          <td>0.000000</td>
          <td>0</td>
          <td>0.000000</td>
          <td>0.000000</td>
        </tr>
        <tr>
          <th>25%</th>
          <td>0.000000</td>
          <td>0</td>
          <td>0.000000</td>
          <td>0.530885</td>
        </tr>
        <tr>
          <th>50%</th>
          <td>0.000000</td>
          <td>0</td>
          <td>0.875221</td>
          <td>0.838567</td>
        </tr>
        <tr>
          <th>75%</th>
          <td>0.474000</td>
          <td>0</td>
          <td>1.027128</td>
          <td>1.023866</td>
        </tr>
        <tr>
          <th>max</th>
          <td>0.993318</td>
          <td>0</td>
          <td>1.288820</td>
          <td>2.570637</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: python

    #sort the DataFrame to plot them by median value
    plot_order = fc_pnps.median(axis=1).sort(inplace=False, ascending=False).index
    
    fig, ax = mgkit.plots.get_single_figure(figsize=(15, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        fc_pnps, 
        plot_order, 
        ax, 
        fonts=dict(fontsize=14, rotation='horizontal'),
        data_colours={
            x: color
            for x, color in zip(plot_order, seaborn.color_palette('hls', len(fc_pnps.index)))
        },
        box_vert=False
    )
    fig.tight_layout()
    fig.savefig('pnps-fc-boxplot.pdf')


.. image:: Exploring-Metagenomic-Data_files/Exploring-Metagenomic-Data_48_0.png

