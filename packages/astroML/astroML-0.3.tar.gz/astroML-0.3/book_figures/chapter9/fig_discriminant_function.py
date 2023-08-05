"""
Example of a Discriminant Function
----------------------------------
This plot shows a simple example of a discriminant function between
two sets of points
"""
# Author: Jake VanderPlas
# License: BSD
#   The figure produced by this code is published in the textbook
#   "Statistics, Data Mining, and Machine Learning in Astronomy" (2013)
#   For more information, see http://astroML.github.com
#   To report a bug or issue, use the following forum:
#    https://groups.google.com/forum/#!forum/astroml-general
import numpy as np
from matplotlib import pyplot as plt

#----------------------------------------------------------------------
# This function adjusts matplotlib settings for a uniform feel in the textbook.
# Note that with usetex=True, fonts are rendered with LaTeX.  This may
# result in an error if LaTeX is not installed on your system.  In that case,
# you can set usetex to False.
from astroML.plotting import setup_text_plots
setup_text_plots(fontsize=8, usetex=True)

#------------------------------------------------------------
# create some toy data
np.random.seed(0)
cluster_1 = np.random.normal([1, 0.5], 0.5, size=(10, 2))
cluster_2 = np.random.normal([-1, -0.5], 0.5, size=(10, 2))

#------------------------------------------------------------
# plot the data and boundary
fig = plt.figure(figsize=(5, 3.75))
ax = fig.add_subplot(111, xticks=[], yticks=[])
ax.scatter(cluster_1[:, 0], cluster_1[:, 1], c='k', s=30)
ax.scatter(cluster_2[:, 0], cluster_2[:, 1], c='w', s=30)
ax.plot([0, 1], [1.5, -1.5], '-k', lw=2)

ax.set_xlim(-2, 2.5)
ax.set_ylim(-2, 2)

plt.show()
