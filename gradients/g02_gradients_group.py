import os, gc
from nilearn import masking
import numpy as np
import numexpr as ne
import argparse
from mapalign import embed
from brainspace.gradient import utils

#img_mask  = '/data/pt_neuam005/sheyma/grouplevel/rest_intra_mask_mni_gm_060.nii.gz'
#subj_list = ['x_preprocessed.nii.gz', 'y_preprocessed.nii.gz', ...]
#out_file  = '/data/pt_neuam005/sheyma/gradients_group/ave_ses-01_past'

parser = argparse.ArgumentParser()
parser.add_argument('-l','--list', dest='subject_list',
		    nargs='+', help='<Required> Set flag', required=True)
parser.add_argument('-m', '--mask', dest='mask_name')
parser.add_argument('-o', '--out', dest='out_name', type=str)

results  = parser.parse_args()
img_mask = results.mask_name
imlist   = results.subject_list
out_file = results.out_name

i 	 = 0
N 	 = len(imlist)
for img_rest in imlist:

    t_series    = masking.apply_mask(img_rest, img_mask).T
    corr_matrix = np.corrcoef(t_series)
    print(img_rest, corr_matrix.shape)

    # sum across corr matrices
    if i == 0:
        indiv_matrix = corr_matrix
    else:
        indiv_matrix = ne.evaluate('indiv_matrix + corr_matrix')
    i += 1

del corr_matrix  ### mem save
gc.collect()

# get the mean
indiv_matrix = ne.evaluate('indiv_matrix / N')
print('average matrix: ', indiv_matrix.shape, indiv_matrix.min(), indiv_matrix.max())

print("Fisher r2z transform...")
indiv_matrix[np.where(indiv_matrix < -0.99)] = -0.99
indiv_matrix[np.where(indiv_matrix > 0.99)]  = 0.99
indiv_matrix = np.arctanh(indiv_matrix)

#### Step 2 #### threshold at 90th percentile
print('thresholding each row at its 90th percentile...')
perc = np.array([np.percentile(x, 90) for x in indiv_matrix])
N    = indiv_matrix.shape[0]
for i in range(N):
    indiv_matrix[i, indiv_matrix[i,:] < perc[i]] = 0
indiv_matrix[indiv_matrix < 0] = 0 ### positive

#### Step 3 #### compute the affinity matrix
print('calculating affinity matrix with numpy linalg ...')
NORM         = (1.0 / np.linalg.norm(indiv_matrix, axis=0).reshape([N,1]))
indiv_matrix = np.dot(indiv_matrix,indiv_matrix) * NORM * NORM.T
indiv_matrix = utils.make_symmetric(indiv_matrix,copy=False) ### symmetric

#### Step 4 #### get gradients
print('computing gradients...')
emb, res = embed.compute_diffusion_map(indiv_matrix, alpha = 0.5,
                                       n_components = 5,
                                       return_result=True)
print(np.shape(emb))
for i in range(0,5):
    print(np.min(emb[:,i]), np.max(emb[:,i]))

out_name_emb = os.path.join(out_file+ '_emb.npy')
np.save(out_name_emb, emb)
