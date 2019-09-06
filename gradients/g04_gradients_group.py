import os, sys, glob
import numpy as np
import h5py
import numexpr as ne
import argparse
from scipy import spatial
from mapalign import embed

#in_file  = '/data/pt_neuam005/sheyma/gradients_group/corr_mean_ses-01-future.h5'
#out_file = '/data/pt_neuam005/sheyma/gradients_group/ses-01-future'

parser = argparse.ArgumentParser()
parser.add_argument('-l','--infile', dest='in_file')
parser.add_argument('-o', '--out', dest='out_prefix', type=str)

results  = parser.parse_args()
in_file  = results.in_file
out_prfx = results.out_prefix

def fisher_z2r(Z):
    X = ne.evaluate('exp(2*Z)')
    return ne.evaluate('(X - 1) / (X + 1)')

h            = h5py.File(in_file, 'r')
indiv_matrix = np.array(h.get("data"))
print(indiv_matrix.shape)

print("Fisher z2r transform...")
indiv_matrix = fisher_z2r(indiv_matrix)

#### threshold at 90th percentile
print('thresholding each row at its 90th percentile...')
perc = np.array([np.percentile(x, 90) for x in indiv_matrix])
N    = indiv_matrix.shape[0]

for i in range(N):
    indiv_matrix[i, indiv_matrix[i,:] < perc[i]] = 0

indiv_matrix[indiv_matrix < 0] = 0

####  compute the affinity matrix
print('calculating affinity matrix with scipy...')
indiv_matrix = spatial.distance.pdist(indiv_matrix, metric = 'cosine')
indiv_matrix = spatial.distance.squareform(indiv_matrix)
indiv_matrix = 1.0 - indiv_matrix

print('affinity shape ', np.shape(indiv_matrix))

####  get gradients
print('computing gradients...')
emb, res = embed.compute_diffusion_map(indiv_matrix, alpha = 0.5,
                                       n_components = 10,
                                       return_result=True)

#### save
out_name_emb = os.path.join(out_prfx + '_dense_emb.npy')
out_name_res = os.path.join(out_prfx + '_dense_res.npy')
print(out_name_emb)
np.save(out_name_emb, emb)
np.save(out_name_res, res['lambdas'])
