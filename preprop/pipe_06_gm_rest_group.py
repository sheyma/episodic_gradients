import os, sys, glob
from nipype.interfaces.fsl import MultiImageMaths

### multiplies all EPI masks -> this would yield another binary mask
### multiply GM mask with that binary mask

#datadir      = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/fmriprep'
#subj_list_fi = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/subject_list.txt'
#outdir       = '/data/pt_neuam005/sheyma/grouplevel/'

datadir      = sys.argv[1]
subj_list_fi = sys.argv[2]
outdir       = sys.argv[3]

content      = open(subj_list_fi).readlines()
sbj_list     = [x.strip('\n') for x in content]

mask_file_list = []
rest_str       = []
i = 0

for sbj_id in sbj_list:
    tmp_dir = os.path.join(datadir, sbj_id) 

    for name in glob.glob(tmp_dir + '/ses*/func/' +
                         '*bold_space-MNI152NLin2009cAsym_brainmask.nii.gz'):
        mask_file_list.append(name)

        i += 1
        if i != 1:
            rest_str.append('-mul %s')
print('...%s EPI masks are being averaged' %(str(len(mask_file_list))))
op_string_rest = " ".join((rest_str))

os.chdir(outdir)

maths = MultiImageMaths()
maths.inputs.in_file       = mask_file_list[0]
maths.inputs.op_string     = op_string_rest
maths.inputs.operand_files = mask_file_list[1:]
maths.inputs.out_file      = 'rest_intra_mask.nii.gz'
maths.run()

maths = MultiImageMaths()
maths.inputs.in_file       = 'rest_intra_mask.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = 'mni_icbm152_t1_tal_nlin_asym_09c_2mm_mask.nii.gz'
maths.inputs.out_file      = 'rest_intra_mask_mni.nii.gz'
maths.run()

maths = MultiImageMaths()
maths.inputs.in_file       = 'rest_intra_mask_mni.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = 'gm_prob_merged_mean_mask_060.nii.gz'
maths.inputs.out_file      = 'rest_intra_mask_mni_gm_060.nii.gz'
maths.run()
