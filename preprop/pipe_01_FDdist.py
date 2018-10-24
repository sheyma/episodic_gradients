import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import seaborn as sns

### gets the distribution of mean framewise displacement (FD)

# define two mandatory arguments
parser = argparse.ArgumentParser()

# list of confounds files as 'sub-X/confounds.txt sub-Y/confounds.txt ...'
parser.add_argument('--list_filenames', dest='filenames', nargs='+',
                    help='<Required> Set flag', required=True)

# a string to label the figure
parser.add_argument('--fig_xlabel', dest='xlabel',
                    type=str, required=True)

results = parser.parse_args()
files   = results.filenames
xlabel  = results.xlabel

# the first five volumes will be ignored in later scripts
n_vol_remove = 5
fd_dist      = []

for file_i in files:
    print(file_i)

    dread   = pd.read_csv(file_i, sep='\t')
    dread   = dread.loc[n_vol_remove:, ]
    mean_fd = dread['FramewiseDisplacement'].mean()
    fd_dist.append(mean_fd)

print(fd_dist)

# plotting the mean FD distribution
sns.set_context('poster', font_scale=1.2)
sns.set_style("ticks")

fig = plt.figure(figsize=(8,6))
ax  = fig.add_subplot(111)

sns.distplot(fd_dist, ax=ax)

MeanFD   = np.mean(fd_dist)

ylim   = ax.get_ylim()
vloc   = (ylim[0] + ylim[1]) / 2.0
xlim   = ax.get_xlim()
pad    = (xlim[0] + xlim[1]) / 100.0
legend = "mean = %g" % MeanFD

ax.axvline(x=MeanFD, color='k')
ax.text(MeanFD - pad, vloc, legend, color="blue", rotation=90,
        verticalalignment='center', horizontalalignment='right')
ax.set_xlabel("mean FD (mm) across %s" %(xlabel))

plt.tight_layout()
plt.show()