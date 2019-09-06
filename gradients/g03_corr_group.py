import os, sys, glob
from nilearn import masking
import numpy as np
import h5py
import numexpr as ne
import nibabel as nb
import argparse

#img_mask  = '/data/pt_neuam005/sheyma/grouplevel/rest_intra_mask_mni_gm_060.nii.gz'
#subj_list = ['x_preprocessed.nii.gz', 'y_preprocessed.nii.gz', ...]
#out_file  = '/data/pt_neuam005/sheyma/gradients_group/corr_mean_ses-XX-YYYY.h5'

parser = argparse.ArgumentParser()
parser.add_argument('-l','--list', dest='subject_list',
		    nargs='+', help='<Required> Set flag', required=True)
parser.add_argument('-m', '--mask', dest='mask_name')
parser.add_argument('-o', '--out', dest='out_name', type=str)

results  = parser.parse_args()
img_mask = results.mask_name
imlist   = results.subject_list
out_file = results.out_name

def fisher_r2z(R):
    return ne.evaluate('arctanh(R)')

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
SUM = ne.evaluate('SUM / N')

print(np.shape(SUM))
print(SUM.min(), SUM.max())

h   = h5py.File(out_file, 'w')
h.create_dataset("data", data=SUM)
h.close()


