
Heatmaps
========

.. code:: python

    import mgkit.plots
    import numpy
    import pandas
    import seaborn as sns
    import matplotlib.colors
Random matrix and color map init
--------------------------------

.. code:: python

    nrow = 50
    ncol = nrow
    
    data = pandas.DataFrame(
    {
        x: numpy.random.negative_binomial(500, 0.5, nrow)
        for x in xrange(ncol)
    }
    )
.. code:: python

    sns.palplot(sns.color_palette('Blues', 9))


.. image:: heatmap_files/heatmap_4_0.png


.. code:: python

    cmap = matplotlib.colors.ListedColormap(sns.color_palette('Blues', 9))
Basic plot
----------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap)



.. parsed-literal::

    <matplotlib.collections.QuadMesh at 0x10c2cfa90>




.. image:: heatmap_files/heatmap_7_1.png


Using Boundaries for the colors
-------------------------------

.. code:: python

    norm = matplotlib.colors.BoundaryNorm([0, 300, 500, 700, 900, 1000], cmap.N)
    
    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap, norm=norm)



.. parsed-literal::

    <matplotlib.collections.QuadMesh at 0x10c722250>




.. image:: heatmap_files/heatmap_9_1.png


Normalising the colors
----------------------

.. code:: python

    norm = matplotlib.colors.Normalize(vmin=400, vmax=700, clip=True)
    
    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap, norm=norm)



.. parsed-literal::

    <matplotlib.collections.QuadMesh at 0x10c82ef10>




.. image:: heatmap_files/heatmap_11_1.png


Grouping labels
~~~~~~~~~~~~~~~

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap)
    mgkit.plots.grouped_spine(
        [range(10), range(10, 20), range(20, 30), range(30, 40), range(40, 50)], 
        ['first', 'second', 'third', 'fourth', 'fifth'],
        ax
    )


.. image:: heatmap_files/heatmap_13_0.png


Reversing the order of the rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data.loc[data.index[::-1]], ax, cmap=cmap)
    mgkit.plots.grouped_spine(
        [range(10), range(10, 20), range(20, 30), range(30, 40), range(40, 50)][::-1], 
        ['first', 'second', 'third', 'fourth', 'fifth'][::-1],
        ax
    )


.. image:: heatmap_files/heatmap_15_0.png


A dendrogram from clustering the data
-------------------------------------

Clustering rows
~~~~~~~~~~~~~~~

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(20, 5))
    _ = mgkit.plots.heatmap.dendrogram(data, ax)


.. image:: heatmap_files/heatmap_18_0.png


Clustering colums (You need the transposed matrix)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(20, 5))
    _ = mgkit.plots.heatmap.dendrogram(data.T, ax)


.. image:: heatmap_files/heatmap_20_0.png


A simple clustered heatmap, look at the code for customisation
--------------------------------------------------------------

.. code:: python

    mgkit.plots.heatmap.heatmap_clustered(data, figsize=(20, 15), cmap=cmap)


.. image:: heatmap_files/heatmap_22_0.png

