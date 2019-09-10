import sys
from nipype.interfaces import afni
from nipype.interfaces.fsl import maths

### band-pass filtering on denoised&detrended timeseries, smoothing,
### and masking back (since smoothing causes slight dilations)

#img_func = 'sub-01_ses-01_task-past_denois_detrend.nii.gz'
#img_mask = 'sub-01_ses-01_task-past_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz'

img_func = sys.argv[1]
img_mask = sys.argv[2]

# filtering
img_filt = img_func[:-7] + '_filt.nii.gz'
print(img_filt)

bandpass                   = afni.Bandpass()
bandpass.inputs.in_file    = img_func
bandpass.inputs.highpass   = 0.01
bandpass.inputs.lowpass    = 0.1
bandpass.inputs.mask       = img_mask
bandpass.inputs.outputtype = 'NIFTI_GZ'
bandpass.inputs.no_detrend = True
bandpass.inputs.out_file   = img_filt
bandpass.run()

# smoothing
img_smoo = img_filt[:-7] + '_smoo.nii.gz'
print(img_smoo)

smooth                 = maths.IsotropicSmooth()
smooth.inputs.in_file  = img_filt
smooth.inputs.fwhm     = 4
smooth.inputs.out_file = img_smoo
smooth.run()

# mask the smoothed image
img_smoo_masked = img_smoo[:-32] + '_preprocessed.nii.gz'
print(img_smoo_masked)

maskApp = maths.ApplyMask()
maskApp.inputs.in_file     = img_smoo
maskApp.inputs.mask_file   = img_mask
maskApp.inputs.out_file    = img_smoo_masked
maskApp.inputs.output_type = 'NIFTI_GZ'
maskApp.run()
