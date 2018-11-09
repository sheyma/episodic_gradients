import os 
from nipype.interfaces import afni as afni
import nipype.interfaces.fsl as fsl

### resampling template data to 2mm

# all input/output hard coded (not good...)
myindata = '/data/pt_neuam005/sheyma/mni_icbm152_nlin_asym_09c/'

# choose a subject's EPI image with 2mm  resoltuib as 'masterfile'
masterdi = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/fmriprep/sub-10/ses-01/func/'
masterte = 'sub-10_ses-01_task-future_bold_space-MNI152NLin2009cAsym_preproc.nii.gz'
masterfi = os.path.join(masterdi, masterte)

os.chdir(myindata)

# afni resample
resample                   = afni.Resample()
resample.inputs.in_file    = 'mni_icbm152_t1_tal_nlin_asym_09c.nii'
resample.inputs.voxel_size = (2.0, 2.0, 2.0)
resample.inputs.master     = masterfi
resample.inputs.outputtype = 'NIFTI'
resample.inputs.out_file   = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii.gz'
print(resample.cmdline)
resample.run()

# transforming template mask to 2mm (fsl nonlinear transform)
aw = fsl.ApplyWarp()
aw.inputs.in_file         = 'mni_icbm152_t1_tal_nlin_asym_09c_mask.nii'
aw.inputs.ref_file        = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii.gz'
aw.inputs.out_file        = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm_trf.nii.gz'
print(aw.cmdline)
aw.run()

binar                    = fsl.maths.MathsCommand()
binar.inputs.args        = '-thr 0.90 -bin'
binar.inputs.in_file     = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm_trf.nii.gz'
binar.inputs.out_file    = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm_mask.nii.gz'
print(binar.cmdline)
binar.run()
