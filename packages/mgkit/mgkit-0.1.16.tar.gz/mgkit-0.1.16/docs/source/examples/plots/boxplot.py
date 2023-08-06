
# coding: utf-8

# # Boxplots

# In[1]:

import mgkit.plots.boxplot
import numpy 
import pandas
import seaborn as sns


# In[2]:

nrows = 9
ncols = 30
data = pandas.DataFrame({
    x: numpy.random.negative_binomial(1000, 0.05, size=nrows)
    for x in xrange(ncols)
})


# ## Simple boxplot

# In[3]:

fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
_ = mgkit.plots.boxplot.boxplot_dataframe(data, data.index, ax)


# ## Change order of boxplots

# In[4]:

fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
_ = mgkit.plots.boxplot.boxplot_dataframe(data, data.index[::-1], ax)


# ## Change labels

# In[5]:

fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
_ = mgkit.plots.boxplot.boxplot_dataframe(data, data.index, ax, label_map={x: 'label {}'.format(x) for x in data.index})


# ## Change font parameters

# In[6]:

fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
_ = mgkit.plots.boxplot.boxplot_dataframe(
    data, 
    data.index, 
    ax, 
    label_map={x: 'label {}'.format(x) for x in data.index}, 
    fonts=dict(fontsize=22, rotation=45)
)


# ## Empty boxplots

# In[7]:

fig, ax = mgkit.plots.get_single_figure(figsize=(30, 10))
_ = mgkit.plots.boxplot.boxplot_dataframe(
    data, 
    data.index, 
    ax, 
    label_map={x: 'label {}'.format(x) for x in data.index}, 
    fonts=dict(fontsize=22, rotation=45),
    fill_box=False
)


# ## Vertical boxplot

# In[8]:

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


# ## Change boxplot colors

# In[9]:

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


# ## Change data colors and the median color

# In[10]:

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


# ## Adding data points

# In[11]:

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


# ## Adding Significance annotations

# In[68]:

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


# ### Changed direction, different palette and marker

# In[12]:

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

