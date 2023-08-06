
Boxplots
========

.. code:: python

    import mgkit.plots.boxplot
    import numpy 
    import pandas
    import seaborn as sns
.. code:: python

    nrows = 9
    ncols = 30
    data = pandas.DataFrame({
        x: numpy.random.negative_binomial(1000, 0.05, size=nrows)
        for x in xrange(ncols)
    })
Simple boxplot
--------------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(data, data.index, ax)


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_4_0.png


Change order of boxplots
------------------------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(data, data.index[::-1], ax)


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_6_0.png


Change labels
-------------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(data, data.index, ax, label_map={x: 'label {}'.format(x) for x in data.index})


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_8_0.png


Change font parameters
----------------------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation=45)
    )


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_10_0.png


Empty boxplots
--------------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation=45),
        fill_box=False
    )


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_12_0.png


Vertical boxplot
----------------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(10, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation='horizontal'),
        fill_box=True,
        box_vert=False
    )


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_14_0.png


Change boxplot colors
---------------------

.. code:: python

    boxplot_colors = {
        key: col
        for key, col in zip(mgkit.plots.boxplot.DEFAULT_BOXPLOT_COLOURS, sns.color_palette('Dark2', len(mgkit.plots.boxplot.DEFAULT_BOXPLOT_COLOURS)))
    }
    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation=45),
        fill_box=True,
        colours=boxplot_colors
    )


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_16_0.png


Change data colors and the median color
---------------------------------------

.. code:: python

    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
    _ = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation=45),
        fill_box=True,
        colours=dict(medians='k'),
        data_colours={x: y for x, y in zip(data.index, sns.color_palette('hls', len(data.index)))}
    )


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_18_0.png


Adding data points
------------------

.. code:: python

    reload(mgkit.plots.boxplot)
    fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10), dpi=300)
    
    data_colours = {x: y for x, y in zip(data.index, sns.color_palette('Dark2', len(data.index)))}
    
    plot_data = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation=45),
        fill_box=False,
        data_colours=data_colours,
        box_vert=True
    )
    
    #note that box_vert must be the same in both boxplot_dataframe and add_values_to_boxplot. Their default is the opposite, now.
    mgkit.plots.boxplot.add_values_to_boxplot(
        data, 
        ax, 
        plot_data, 
        data.index, 
        data_colours=data_colours, 
        s=600, 
        alpha=0.5, 
        box_vert=True
    )


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_20_0.png


Adding Significance annotations
-------------------------------

.. code:: python

    reload(mgkit.plots.boxplot)
    fig, ax = mgkit.plots.get_single_figure(figsize=(20, 10), dpi=300)
    
    data_colours = {x: y for x, y in zip(data.index, sns.color_palette('Dark2', len(data.index)))}
    
    plot_data = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation=45),
        fill_box=False,
        data_colours=data_colours,
        box_vert=True
    )
    
    #note that box_vert must be the same in both boxplot_dataframe and add_values_to_boxplot. Their default is the opposite, now.
    mgkit.plots.boxplot.add_values_to_boxplot(
        data, 
        ax, 
        plot_data, 
        data.index, 
        data_colours=data_colours, 
        s=600, 
        alpha=0.5, 
        box_vert=True
    )
    mgkit.plots.boxplot.add_significance_to_boxplot(
        [
            (0, 1),
            (1, 3),
            (2, 3),
            (7, 8),
            (4, 6)
        ], 
        ax, 
        (21850, 21750),
        box_vert=True,
        fontsize=32
    )
    _ = ax.set_ylim(top=22500)


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_22_0.png


Changed direction, different palette and marker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    reload(mgkit.plots.boxplot)
    fig, ax = mgkit.plots.get_single_figure(figsize=(20, 15), dpi=300)
    
    data_colours = {x: y for x, y in zip(data.index, sns.color_palette('Set1', len(data.index)))}
    
    plot_data = mgkit.plots.boxplot.boxplot_dataframe(
        data, 
        data.index, 
        ax, 
        label_map={x: 'label {}'.format(x) for x in data.index}, 
        fonts=dict(fontsize=22, rotation=45),
        fill_box=False,
        data_colours=data_colours,
        box_vert=False
    )
    
    #note that box_vert must be the same in both boxplot_dataframe and add_values_to_boxplot. Their default is the opposite, now.
    mgkit.plots.boxplot.add_values_to_boxplot(
        data, 
        ax, 
        plot_data, 
        data.index, 
        data_colours=data_colours, 
        s=600, 
        alpha=0.5,
        marker='|',
        linewidth=8,
        box_vert=False
    )


.. image:: boxplot-checkpoint_files/boxplot-checkpoint_24_0.png

