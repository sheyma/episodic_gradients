import os, sys
from nipype.interfaces.fsl import MultiImageMaths
from nipype.interfaces import afni as afni
import nibabel as nb
import numpy as np
from nipype.interfaces.fsl.maths import ErodeImage

# subj = 'sub-01'
subj = sys.argv[1]

# addressing individual tms files...
indir    = '/data/pt_neuam005/simnibs_TMS/subjects/'
subdir   = 'simnibs_simulation_mPFC/mni_volumes'
suffix   = '_TMS_1-0001_MagVenture_MC_B70_nii_scalar_MNI_normE.nii.gz'

# the template to resample nifti's...
masterdi = '/data/pt_neuam005/sheyma/mni_icbm152_nlin_asym_09c/'
masterte = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii'
masterfi = os.path.join(masterdi, masterte)

# get T1 brain mask of subject (fmriprep output)
prepdir   = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/fmriprep/'
T1mask    = os.path.join(prepdir, subj, 'anat',
                         '%s_T1w_space-MNI152NLin2009cAsym_brainmask.nii.gz' % (subj))

# resample subject T1 to asym MNI 2mm
if os.path.exists(os.path.join(indir, subj, subdir, subj + '_T1_asym_mask.nii.gz')) == 0:
    resample = afni.Resample()
    resample.inputs.in_file = T1mask
    resample.inputs.voxel_size = (2.0, 2.0, 2.0)
    resample.inputs.master = masterfi
    resample.inputs.outputtype = 'NIFTI'
    resample.inputs.out_file = os.path.join(indir, subj, subdir, subj + '_T1_asym_mask.nii.gz')
    resample.run()

# resample subject TMS Efield to asym MNI 2mm
if os.path.exists(os.path.join(indir, subj, subdir, subj + '_TMS_asym.nii.gz')) == 0:
    resample = afni.Resample()
    resample.inputs.in_file = os.path.join(indir, subj, subdir, subj + suffix)
    resample.inputs.voxel_size = (2.0, 2.0, 2.0)
    resample.inputs.master = masterfi
    resample.inputs.outputtype = 'NIFTI'
    resample.inputs.out_file = os.path.join(indir, subj, subdir, subj + '_TMS_asym.nii.gz')
    resample.run()

### HERE WE GO...
thrlist = [92, 94, 96, 98]

for thr in thrlist:

    workdir = os.path.join(indir, subj, subdir, 'thr_OLE_' + str(thr))
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    os.chdir(workdir)

    sessions = ['ses_1', 'ses_2', 'ses_3']
    tasks    = ['past', 'future']

    for ses in sessions:
        for task in tasks:

            if task == 'past':
                t = '01'
            elif task == 'future':
                t = '02'

            # get a brain mask from resting-state image (ie. ALFF nifti)
            myalffimage = os.path.join('/data/pt_neuam005/sheyma/alff_whole/'
                                       'alff_%s_%s_temp_%s.nii' % (subj, ses, t))
            automask = afni.Automask()
            automask.inputs.in_file    = myalffimage
            automask.inputs.dilate     = 0
            automask.inputs.outputtype = "NIFTI"
            automask.inputs.out_file   = 'alff_%s_%s_temp_%s_mask.nii.gz' % (subj, ses, t)
            automask.run()

            # resample mask to asymmetric MNI 2mm
            resample = afni.Resample()
            resample.inputs.in_file    = 'alff_%s_%s_temp_%s_mask.nii.gz' % (subj, ses, t)
            resample.inputs.voxel_size = (2.0, 2.0, 2.0)
            resample.inputs.master     = masterfi
            resample.inputs.outputtype = 'NIFTI'
            resample.inputs.out_file   = 'alff_%s_%s_temp_%s_mask_asym.nii.gz' % (subj, ses, t)
            resample.run()

            # be sure that mask is inside T1 brain
            maths = MultiImageMaths()
            maths.inputs.in_file       = 'alff_%s_%s_temp_%s_mask_asym.nii.gz' % (subj, ses, t)
            maths.inputs.op_string     = '-mul %s'
            maths.inputs.operand_files = os.path.join(indir, subj, subdir, subj + '_T1_asym_mask.nii.gz')
            maths.inputs.out_file      = 'alff_' + subj + '_' + ses + '_temp_' + t + '_mask_asym_T1.nii.gz'
            maths.run()

            # HERE WE GO: masking out the TMS Efield map
            maths = MultiImageMaths()
            maths.inputs.in_file       = 'alff_' + subj + '_' + ses + '_temp_' + t + '_mask_asym_T1.nii.gz'
            maths.inputs.op_string     = '-mul %s'
            maths.inputs.operand_files = os.path.join(indir, subj, subdir, subj + '_TMS_asym.nii.gz')
            maths.inputs.out_file      =  'alff_' + subj + '_' + ses + '_temp_' + t + '_mask_asym_T1_TMS.nii.gz'
            maths.run()

            # thresholding TMS Efield map at a given percentile
            Afile = os.path.join(workdir, 'alff_' + subj + '_' + ses + '_temp_' + t + '_mask_asym_T1_TMS.nii.gz')
            A     = nb.load(Afile).get_data()
            perc  = np.percentile(A, thr)
            print('threshold is: ', perc)
            A[A < perc]  = 0
            A[A >= perc] = 1
            mni_affine   = nb.load(masterfi).get_affine()
            tmp_img      = nb.Nifti1Image(A, mni_affine)
            thrname      = os.path.join(workdir, 'alff_'+subj+'_'+ses+'_temp_'+t+'_mask_asym_T1_TMS_thr.nii.gz')
            nb.save(tmp_img, thrname)

            # eroding the final Efield mask
            eroding = ErodeImage()
            eroding.inputs.in_file  = os.path.join(workdir, 'alff_'+subj+'_'+ses+'_temp_'+t+'_mask_asym_T1_TMS_thr.nii.gz')
            eroding.inputs.out_file = os.path.join(workdir, 'alff_'+subj+'_'+ses+'_temp_'+t+'_mask_asym_T1_TMS_thr_eroded.nii.gz')
            eroding.run()

