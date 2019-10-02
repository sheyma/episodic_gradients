import os, sys, glob
from nilearn import masking
import numpy as np
import h5py
import numexpr as ne
import nibabel as nb
import argparse
from mapalign import embed

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

def mask_check(rest, mask):
    """
    rest: 4D nifti-filename
    mask: 3D nifti-filename
    """
    matrix = masking.apply_mask(rest, mask)
    matrix = matrix.T
    cnt_zeros = 0 
    for i in range(0, matrix.shape[0]):
        if np.count_nonzero(matrix[i, :]) == 0:
            cnt_zeros += 1
    return cnt_zeros, matrix

i 	 = 0
N 	 = len(imlist)

for img_rest in imlist:
  
    [voxel_zeros, t_series] = mask_check(img_rest, img_mask)

    # get correlation coefficients and Fisher r2z transform
    corr_matrix = np.corrcoef(t_series)
    print(img_rest)
    print(corr_matrix.shape)

    # sum across corr matrices
    if i == 0:
        SUM = corr_matrix
    else:
        SUM = ne.evaluate('SUM + corr_matrix')
    i += 1

# get the mean
indiv_matrix = ne.evaluate('SUM / N')
print('average matrix: ', indiv_matrix.shape, indiv_matrix.min(), indiv_matrix.max())

indiv_matrix[np.where(indiv_matrix < -0.99)] = -0.99
indiv_matrix[np.where(indiv_matrix > 0.99)] = 0.99

print("Fisher r2z transform...")
indiv_matrix = np.arctanh(indiv_matrix)
print('fisher matrix: ', indiv_matrix.shape, indiv_matrix.min(), indiv_matrix.max())

#### Step 2 #### threshold at 90th percentile
print('thresholding each row at its 90th percentile...')
perc = np.array([np.percentile(x, 90) for x in indiv_matrix])
N    = indiv_matrix.shape[0]

for i in range(N):
    indiv_matrix[i, indiv_matrix[i,:] < perc[i]] = 0

#neg_values = np.array([sum(indiv_matrix[i,:] < 0) for i in range(N)])
#print('Negative values occur in %d rows' % sum(neg_values > 0))
indiv_matrix[indiv_matrix < 0] = 0

#### Step 3 #### compute the affinity matrix
print('calculating affinity matrix with numpy linalg ...')
NORM         = (1.0 / np.linalg.norm(indiv_matrix, axis=0).reshape([N,1]))
indiv_matrix = np.dot(indiv_matrix,indiv_matrix) * NORM * NORM.T
print('affinity shape ', np.shape(indiv_matrix))

#### Step 4 #### get gradients
print('computing gradients...')
# NOTE this is fast but uses a lot of memory. So if we would save the matrix
# here, then we could run everything above more parallel above all subjects
emb, res = embed.compute_diffusion_map(indiv_matrix, alpha = 0.5,
                                       n_components = 10,
                                       return_result=True)

out_name_emb = out_file + '_dense_emb.npy'
out_name_res = out_file + '_dense_res.npy'
print(out_name_emb)
np.save(out_name_emb, emb)
np.save(out_name_res, res['lambdas'])