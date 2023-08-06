
# coding: utf-8

# # Heatmaps

# In[1]:

import mgkit.plots
import numpy
import pandas
import seaborn as sns
import matplotlib.colors


# ## Random matrix and color map init

# In[2]:

nrow = 50
ncol = nrow

data = pandas.DataFrame(
{
    x: numpy.random.negative_binomial(500, 0.5, nrow)
    for x in xrange(ncol)
}
)


# In[3]:

sns.palplot(sns.color_palette('Blues', 9))


# In[4]:

cmap = matplotlib.colors.ListedColormap(sns.color_palette('Blues', 9))


# ## Basic plot

# In[5]:

fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap)


# ## Using Boundaries for the colors

# In[6]:

norm = matplotlib.colors.BoundaryNorm([0, 300, 500, 700, 900, 1000], cmap.N)

fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap, norm=norm)


# ## Normalising the colors

# In[7]:

norm = matplotlib.colors.Normalize(vmin=400, vmax=700, clip=True)

fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap, norm=norm)


# ### Grouping labels

# In[8]:

fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
mgkit.plots.heatmap.baseheatmap(data, ax, cmap=cmap)
mgkit.plots.grouped_spine(
    [range(10), range(10, 20), range(20, 30), range(30, 40), range(40, 50)], 
    ['first', 'second', 'third', 'fourth', 'fifth'],
    ax
)


# ### Reversing the order of the rows

# In[9]:

fig, ax = mgkit.plots.get_single_figure(figsize=(10,10), aspect='equal')
mgkit.plots.heatmap.baseheatmap(data.loc[data.index[::-1]], ax, cmap=cmap)
mgkit.plots.grouped_spine(
    [range(10), range(10, 20), range(20, 30), range(30, 40), range(40, 50)][::-1], 
    ['first', 'second', 'third', 'fourth', 'fifth'][::-1],
    ax
)


# ## A dendrogram from clustering the data 

# ### Clustering rows

# In[10]:

fig, ax = mgkit.plots.get_single_figure(figsize=(20, 5))
_ = mgkit.plots.heatmap.dendrogram(data, ax)


# ### Clustering colums (You need the transposed matrix)

# In[11]:

fig, ax = mgkit.plots.get_single_figure(figsize=(20, 5))
_ = mgkit.plots.heatmap.dendrogram(data.T, ax)


# ## A simple clustered heatmap, look at the code for customisation

# In[12]:

mgkit.plots.heatmap.heatmap_clustered(data, figsize=(20, 15), cmap=cmap)

