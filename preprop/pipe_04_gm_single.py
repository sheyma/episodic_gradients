import sys, os
import nipype.interfaces.fsl as fsl
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.ants as ants
import subprocess

### gets regions of interests from freesurfer tissue segmentations,
### normalizes roi's to the template space and grid resolution

#subj_id    = 'sub-17'
#aseg_mgz   = '/sub-17/mri/aseg.mgz'
#reffile    = '/mni_icbm152_t1_tal_nlin_asym_09c.nii'
#masterfile = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii.gz'
#transfile  = '/sub-17/anat/sub-17_T1w_target-MNI152NLin2009cAsym_warp.h5'
#outdir     = '/sub-17/anat/'

subj_id    = sys.argv[1]
aseg_mgz   = sys.argv[2]
reffile    = sys.argv[3]
masterfile = sys.argv[4]
transfile  = sys.argv[5]
outdir     = sys.argv[6]

# convert freesurfer out files (*mgz) to *nifti
aseg_nifti = os.path.join(outdir, subj_id + '_aseg.nii.gz')

mricon     = fs.MRIConvert(in_file  = aparc_aseg_mgz,
                           out_file = aparc_aseg_nifti,
                           out_type = 'niigz').run()
                           
# get only GM regions of interest from *aseg.nifti
aseg_labeled = aseg_nifti[:-7] + '_labeled.nii.gz'
# freesurfer labels (view an *mgz with freeviewer ;) )
gm_labels   = [3, 42, 17, 18, 19, 53, 54, 11, 12, 13, 26, 
               50, 51, 52, 58, 9, 10, 48, 49, 28, 60, 55]

coolBinarize = fs.Binarize()
coolBinarize.inputs.in_file     = aseg_nifti
coolBinarize.inputs.match       = gm_labels
coolBinarize.out_type           = 'nii.gz'
coolBinarize.inputs.binary_file = aseg_labeled
coolBinarize.run()

# normalize GM map to template space
aseg_norm   = aseg_labeled[:-7] + '_norm.nii.gz'

at                               = ants.ApplyTransforms()
at.inputs.input_image            = aseg_labeled
at.inputs.reference_image        = reffile
at.inputs.transforms             = [transfile]
at.inputs.invert_transform_flags = [False]
at.inputs.dimension              = 3
at.inputs.interpolation          = 'BSpline'
at.inputs.output_image           = aseg_norm
print(at.cmdline)
subprocess.call(at.cmdline.split())

#### resampling to 2x2x2mm
gm_infile  = aseg_norm
gm_outfile = gm_infile[:-7] + '_2mm.nii.gz'
flt                     = fsl.FLIRT(bins=640, cost_func='mutualinfo')
flt.inputs.apply_isoxfm = 2.0
flt.inputs.in_file      = gm_infile
flt.inputs.output_type  = "NIFTI_GZ"
flt.inputs.out_file     = gm_outfile
flt.inputs.reference    = masterfile
flt.run()
