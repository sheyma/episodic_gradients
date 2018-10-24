import os 
from nipype.interfaces import afni as afni

### resampling template space to 2mm

# all input/output hard coded (not good...)
myindata = '/data/pt_neuam005/sheyma/mni_icbm152_nlin_asym_09c/'

# choose a subject functional image lying at 2mm to be used as masterfile
masterdi = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/fmriprep/sub-10/ses-01/func/'
masterte = 'sub-10_ses-01_task-future_bold_space-MNI152NLin2009cAsym_preproc.nii.gz'
masterfi = os.path.join(masterdi, masterte)

# afni resample
resample                   = afni.Resample()
resample.inputs.in_file    = os.path.join(myindata,
                                          'mni_icbm152_t1_tal_nlin_asym_09c.nii')
resample.inputs.voxel_size = (2.0, 2.0, 2.0)
resample.inputs.master     = masterfi
resample.inputs.outputtype = "NIFTI"
resample.inputs.out_file   = os.path.join(myindata,
                                          'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii.gz')
print(resample.cmdline)
resample.run()

resample                   = afni.Resample()
resample.inputs.in_file    = os.path.join(myindata,
                                          'mni_icbm152_t2_tal_nlin_asym_09c.nii')
resample.inputs.voxel_size = (2.0, 2.0, 2.0)
resample.inputs.master     = masterfi
resample.inputs.outputtype = "NIFTI"
resample.inputs.out_file   = os.path.join(myindata,
                                          'mni_icbm152_t2_tal_nlin_asym_09c_2mm.nii.gz')
print(resample.cmdline)
resample.run()
