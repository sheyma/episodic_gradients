import os, sys
from nipype.interfaces.fsl import MultiImageMaths
from nipype.interfaces import afni as afni
import nibabel as nb
import numpy as np

subj = sys.argv[1]        # subj = 'sub-01'

# addressing individual tms files...
indir    = '/data/pt_neuam005/simnibs_TMS/subjects/'
subdir   = 'simnibs_simulation_mPFC/mni_volumes'
suffix   = '_TMS_1-0001_MagVenture_MC_B70_nii_scalar_MNI_normE.nii.gz'

# to be used for resampling...
masterdi = '/data/pt_neuam005/sheyma/mni_icbm152_nlin_asym_09c/'
masterte = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii'
masterfi = os.path.join(masterdi, masterte)

# get brain mask of subject
prepdir   = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/fmriprep/'
T1mask    = os.path.join(prepdir, subj, 'anat',
                         '%s_T1w_space-MNI152NLin2009cAsym_brainmask.nii.gz' % (subj))

# resample nifti average to 2mm asym
resample                   = afni.Resample()
resample.inputs.in_file    = os.path.join(indir, subj, subdir, subj + suffix)
resample.inputs.voxel_size = (2.0, 2.0, 2.0)
resample.inputs.master     = masterfi
resample.inputs.outputtype = 'NIFTI'
resample.inputs.out_file   = os.path.join(indir, subj, subdir, subj + '_mni_asym_2mm.nii.gz')
#resample.run()

# resample subject T1 to 2mm asym
resample                   = afni.Resample()
resample.inputs.in_file    = T1mask
resample.inputs.voxel_size = (2.0, 2.0, 2.0)
resample.inputs.master     = masterfi
resample.inputs.outputtype = 'NIFTI'
resample.inputs.out_file   = os.path.join(indir, subj, subdir, subj + '_T1mask_asym_2mm.nii.gz')
#resample.run()

# remove skull etc..
maths = MultiImageMaths()
maths.inputs.in_file       = os.path.join(indir, subj, subdir, subj + '_mni_asym_2mm.nii.gz')
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = os.path.join(indir, subj, subdir, subj + '_T1mask_asym_2mm.nii.gz')
maths.inputs.out_file      = os.path.join(indir, subj, subdir, subj + '_mni_asym_2mm_brain.nii.gz')
#maths.run()

thrlist = [92, 94, 98]
for thr in thrlist:
    # get given percentile !
    Afile = os.path.join(indir, subj, subdir, subj + '_mni_asym_2mm_brain.nii.gz')
    A     = nb.load(Afile).get_data()
    perc  = np.percentile(A, thr)
    print('threshold is: ', perc)

    # threshold ...
    A[A<perc]   = 0
    A[A>=perc]  = 1

    # saving tms-mask as nifti
    mni_affine = nb.load(masterfi).get_affine()
    tmp_img    = nb.Nifti1Image(A, mni_affine)
    thrname    = os.path.join(indir, subj, subdir, subj +
                             '_mni_asym_2mm_brain_thr%i_OLE.nii.gz' % (thr))
    nb.save(tmp_img, thrname)
