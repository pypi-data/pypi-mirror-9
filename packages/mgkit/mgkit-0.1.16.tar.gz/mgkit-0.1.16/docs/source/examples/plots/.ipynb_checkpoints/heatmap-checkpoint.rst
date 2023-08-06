
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


.. image:: heatmap-checkpoint_files/heatmap-checkpoint_4_0.png


.. code:: python

    cmap = matplotlib.colors.ListedColormap(sns.color_palette('Blues', 9))
Basic plot
----------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap)



.. parsed-literal::

    <matplotlib.collections.QuadMesh at 0x1138a0990>




.. image:: heatmap-checkpoint_files/heatmap-checkpoint_7_1.png


Using Boundaries for the colors
-------------------------------

.. code:: python

    norm = matplotlib.colors.BoundaryNorm([0, 300, 500, 700, 900, 1000], cmap.N)
    
    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap, norm=norm)



.. parsed-literal::

    <matplotlib.collections.QuadMesh at 0x113bb8d90>




.. image:: heatmap-checkpoint_files/heatmap-checkpoint_9_1.png


Normalising the colors
----------------------

.. code:: python

    norm = matplotlib.colors.Normalize(vmin=400, vmax=700, clip=True)
    
    fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
    mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap, norm=norm)



.. parsed-literal::

    <matplotlib.collections.QuadMesh at 0x113e30ad0>




.. image:: heatmap-checkpoint_files/heatmap-checkpoint_11_1.png


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


.. image:: heatmap-checkpoint_files/heatmap-checkpoint_13_0.png


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


.. image:: heatmap-checkpoint_files/heatmap-checkpoint_15_0.png


A dendrogram from clustering the data
-------------------------------------

Clustering rows
~~~~~~~~~~~~~~~

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(20, 5))
    _ = mgkit.plots.heatmap.dendrogram(data, ax)


.. image:: heatmap-checkpoint_files/heatmap-checkpoint_18_0.png


Clustering colums (You need the transposed matrix)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(20, 5))
    _ = mgkit.plots.heatmap.dendrogram(data.T, ax)


.. image:: heatmap-checkpoint_files/heatmap-checkpoint_20_0.png


A simple clustered heatmap, look at the code for customisation
--------------------------------------------------------------

.. code:: python

    mgkit.plots.heatmap.heatmap_clustered(data, figsize=(20, 15), cmap=cmap)


.. image:: heatmap-checkpoint_files/heatmap-checkpoint_22_0.png

