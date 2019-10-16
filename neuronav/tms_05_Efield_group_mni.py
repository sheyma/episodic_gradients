import os
from nipype.interfaces.fsl import MultiImageMaths
from nipype.interfaces.fsl.maths import MathsCommand
from nipype.interfaces import afni as afni

# addressing individual tms files...
indir    = '/data/pt_neuam005/simnibs_TMS/subjects/'
outdir   = '/data/pt_neuam005/simnibs_TMS/subjects_group/'
subdir   = 'simnibs_simulation_vertex/mni_volumes'
suffix   = '_TMS_1-0001_MagVenture_MC_B70_nii_scalar_MNI_normE.nii.gz'
lisfname = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/subject_list_tms.txt'

# to be used for resampling...
masterdi = '/data/pt_neuam005/sheyma/mni_icbm152_nlin_asym_09c/'
masterte = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm.nii'
masterfi = os.path.join(masterdi, masterte)

# to be used to get the intersection of tms mask on connectivity mask...
groupdi = '/data/pt_neuam005/sheyma/grouplevel/'
groupte = 'rest_intra_mask_mni_gm_055.nii.gz'
groupfi = os.path.join(groupdi, groupte)

# get subject id's as a list
with open(lisfname) as f:
    content = f.readlines()
subjects = [x.strip('\n') for x in content]
###subjects = ['sub-01', 'sub-05', ...]

# initialize parameters for nifti averaging
img_list = []
img_oper = []
i = 0
for sub in subjects:

    img_subj = os.path.join(indir, sub, subdir, sub + suffix)
    img_list.append(img_subj)

    i += 1
    if i!= 1:
        img_oper.append('-add %s ')

img_oper.append(('-div %s' % len(img_list)))
operation = " ".join((img_oper))

# get nifti average
maths = MultiImageMaths()
maths.inputs.in_file       = img_list[0]
maths.inputs.op_string     = operation
maths.inputs.operand_files = img_list[1:]
maths.inputs.out_file      = outdir + 'tms_vertex_mni_1mm.nii.gz'
maths.run()
print(maths.cmdline)

# resample nifti average to 2mm
resample                   = afni.Resample()
resample.inputs.in_file    = outdir + 'tms_vertex_mni_1mm.nii.gz'
resample.inputs.voxel_size = (2.0, 2.0, 2.0)
resample.inputs.master     = masterfi
resample.inputs.outputtype = 'NIFTI'
resample.inputs.out_file   = outdir + 'tms_vertex_mni_2mm.nii.gz'
resample.run()
print(resample.cmdline)

# max obtained from fsaverage E-field, now threshold it at top XX %
mymaximum = 58.765
threshol  = mymaximum * 0.70
print('THRESHOLD', threshol)

# binarize at the given threshold...
binar                    = MathsCommand()
binar.inputs.in_file     = outdir + 'tms_vertex_mni_2mm.nii.gz'
binar.inputs.out_file    = outdir + 'tms_vertex_mni_2mm_thr_%i.nii.gz' % (threshol)
binar.inputs.args   = '-thr %f -bin' % (threshol)
binar.run()
print(binar.cmdline)

# get the intersection of two masks
maths = MultiImageMaths()
maths.inputs.in_file       = outdir + 'tms_vertex_mni_2mm_thr_%i.nii.gz' % (threshol)
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = groupfi
maths.inputs.out_file      = outdir + 'tms_vertex_mni_2mm_thr_%i_on_gradient_055.nii.gz' % (threshol)
maths.run()
print(maths.cmdline)
