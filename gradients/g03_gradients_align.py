import os
import argparse
import numpy as np
import nibabel as nb
from mapalign import align
from brainspace.gradient import alignment

# list = ['sub-XX_ses-01_task-future_dense_emb.npy', ...]
# mask = 'rest_intra_mask_mni_gm_thr_YY.nii.gz'
# mnit = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii.gz' 
# out  = '/data/pt_neuam005/sheyma/aligned_YY/'
# targ = 'ave_group_gradients.npy'

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--list', dest='file_list',
                    nargs='+', help='<Required> Set flag', required=True)
parser.add_argument('-m', '--mask', dest='mask_name')
parser.add_argument('-mni', '--mnit', dest='mni_name')
parser.add_argument('-o', '--out', dest='out_path')
parser.add_argument('-t', '--target', dest='target')

results = parser.parse_args()
im_list = results.file_list
gm_mask = results.mask_name
mni_tmp = results.mni_name
outdir  = results.out_path
targ_fi = results.target

# upload mni template
mni_affine = nb.load(mni_tmp).get_affine()
# get voxel indices (x,y,z) from gray matter mask
mask_array = nb.load(gm_mask).get_data()
x, y, z    = np.where(mask_array==1)
print("%s voxels are in GM..." % len(x))

# define function to save numpy arrays as nifti
def save_niis(bname, k, A):
    aname        = 'align_' + str(k + 1) + '_' + bname + '.nii.gz'
    fname        = os.path.join(outdir, aname)
    tmp          = np.zeros(nb.load(mni_tmp).get_data().shape)
    tmp[x, y, z] = A
    tmp_img      = nb.Nifti1Image(tmp, mni_affine)
    nb.save(tmp_img, fname)
    return fname

# get the target embedding as numpy array
reference = np.load(targ_fi)

# get the embeddings as a numpy array or a list
if len(im_list) == 1:
    embeddings = np.load(im_list[0]) ### (73472, 5)
    realigned  = alignment.procrustes(source=embeddings,
                                      target=reference) ### (73472, 5)

    for i in range(0, np.shape(realigned)[1]):
        fname = save_niis(os.path.basename(im_list[0])[:-4], i, realigned[:, i])
        print(i,  realigned[:, i].min(), realigned[:, i].max(), '\n', fname)

else:
    alist = []
    for im in im_list:
        im_load = np.load(im)
        alist.append(im_load.T)
    embeddings = list(np.dstack(alist).T) ### (2, 73472, 5)
    realigned, M = alignment.procrustes_alignment(data=embeddings,
                                                  reference=reference,
                                                  n_iter=10) ### (2, 73472, 5)

    #reference = list(np.dstack(reference.T).T.T)
    #ALL = np.concatenate((reference, embeddings), axis=0) ### (3, 73472, 5)
    #realigned, xfsm = align.iterative_alignment(ALL, n_iters=10) ### SATRA

    for im, realign in zip(im_list, realigned):
        for i in range(0, np.shape(realign)[1]):
            fname = save_niis(os.path.basename(im)[:-4], i, realign[:, i])
            print(i, realign[:,i].shape, realign[:, i].min(), realign[:, i].max(), '\n', fname)
