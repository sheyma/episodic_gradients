import os
import argparse
import numpy as np
import nibabel as nb
from mapalign import align

# im_list = ['sub-XX_ses-01_task-future_dense_emb.npy', ...]
# gm_mask = 'rest_intra_mask_mni_gm_thr_YY.nii.gz'
# mni_tmp = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii.gz'
# out_pat = '/data/pt_neuam005/sheyma/gradientsYY_individual/'

parser = argparse.ArgumentParser()
parser.add_argument('-l','--list', dest='file_list',
                    nargs='+', help='<Required> Set flag', required=True)
parser.add_argument('-m', '--mask', dest='mask_name')
parser.add_argument('-t', '--mnit', dest='mni_name')
parser.add_argument('-o', '--out', dest='out_path')

results = parser.parse_args()
im_list = results.file_list
gm_mask = results.mask_name
mni_tmp = results.mni_name
out_pat = results.out_path

# load each embedding as numpy array and concatenate all 
alist = []
for im in im_list:
    im_load = np.load(im)
    alist.append(im_load.T)

# stack embedding arrays 
embeddings = list(np.dstack(alist).T)
print("list of all embeddings: ", np.shape(embeddings)) #### (216, 61891, 10)

# run the alignment
realigned, xfsm = align.iterative_alignment(embeddings, n_iters=1000)

# upload mni template 
mni_affine = nb.load(mni_tmp).get_affine()

# get voxel indices (x,y,z) of gray matter mask = 1
mask_array = nb.load(gm_mask).get_data()
voxel_x = np.where(mask_array==1)[0]
voxel_y = np.where(mask_array==1)[1]
voxel_z = np.where(mask_array==1)[2]
print("%s voxels are in GM..." % len(voxel_x))

# project aligned arrays back to the mni template space and save as nifti
for im, realign in zip(im_list, realigned):

    print(im, np.shape(realign))

    for i in range(0, 5):

        aname = 'grad_alig_'+str(i+1)+'_'+os.path.basename(im)[:-4]+'.nii.gz'
        fname = os.path.join(out_pat, aname)
        print(fname)

        tmp = np.zeros(nb.load(mni_tmp).get_data().shape)
        tmp[voxel_x, voxel_y, voxel_z] = realign[:,i]
        tmp_img = nb.Nifti1Image(tmp, mni_affine)

        nb.save(tmp_img, fname)

