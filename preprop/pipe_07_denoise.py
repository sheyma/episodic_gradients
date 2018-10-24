import sys
import numpy as np
import pandas as pd
import nibabel as nb
import nipype.interfaces.fsl as fsl
from nipype.interfaces import afni as afni

### denoising fmri timeseries (the fmriprep output images are inputs here!)

#img_func = 'sub-01_ses-01_task-past_bold_space-MNI152NLin2009cAsym_preproc.nii.gz'
#img_mask = 'sub-01_ses-01_task-past_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz'
#conf_fil = 'sub-01_ses-01_task-past_bold_confounds.tsv'

img_func = sys.argv[1]
img_mask = sys.argv[2]
conf_fil = sys.argv[3]

# removal of the first five volumes
def strip_rois_func(in_file, t_min):

    nii     = nb.load(in_file)
    new_nii = nb.Nifti1Image(nii.get_data()[:,:,:,t_min:], 
                             nii.get_affine(), nii.get_header())
    new_nii.set_data_dtype(np.float32)   
    out_file = in_file[:-46] + '.nii.gz' 
    nb.save(new_nii, out_file)   
    print(out_file)
    return out_file

n_vol_remove = 5 
img_removed  = strip_rois_func(img_func, n_vol_remove)

dread = pd.read_csv(conf_fil,
                    sep = '\t')
dread = dread.loc[n_vol_remove:,]

# prepare the nuisance factors
df = pd.concat([dread['X'], 
                dread['Y'],
                dread['Z'],
                dread['RotX'],
                dread['RotY'],
                dread['RotZ'],
                dread['FramewiseDisplacement'],
                dread['aCompCor00'],
                dread['aCompCor01'],
                dread['aCompCor02'],
                dread['aCompCor03'],
                dread['aCompCor04'],
                dread['aCompCor05']],
                axis=1)

design_out = conf_fil[:-4] + '_small.csv'
print(design_out)

df.to_csv(design_out, 
          sep='\t',
          index=False,
          header=False)

# regress out nuisance factors using fls_glm
glm = fsl.GLM(in_file = img_removed, 
              mask    = img_mask, 
              design  = design_out,
              demean  = True,
              out_res_name = img_removed[:-7] + '_denois.nii.gz',
              output_type ='NIFTI_GZ')
glm.run()

# detrend timeseries using afni-3dDetrend
detrend = afni.Detrend()
detrend.inputs.in_file    = img_removed[:-7] + '_denois.nii.gz'
detrend.inputs.args       = '-polort 2'
detrend.inputs.outputtype = 'NIFTI_GZ'
detrend.inputs.out_file   = img_removed[:-7] + '_denois_detrend.nii.gz'
print(detrend.cmdline)
detrend.run()