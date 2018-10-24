import os, sys, glob, six
from nipype.interfaces.fsl import Merge
from nipype.interfaces.fsl.maths import MeanImage
from nipype.interfaces.fsl.maths import MathsCommand

### gets GM probabilistic maps of all subjects, averages them,
### and finally binarizes to get a GM mask

#datadir      = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/fmriprep'
#subj_list_fi = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/subject_list.txt'
#outdir       = '/data/pt_neuam005/sheyma/grouplevel/'

datadir      = sys.argv[1]
subj_list_fi = sys.argv[2]
outdir       = sys.argv[3]

content      = open(subj_list_fi).readlines()
sbj_list     = [x.strip('\n') for x in content]

gm_file_list = []

for sbj_id in sbj_list:
    tmp_dir = os.path.join(datadir, sbj_id, 'anat')
    tmp_fil = glob.glob(os.path.join(tmp_dir, 
                                     '*aseg_labeled_norm_2mm.nii.gz'))
    gm_file_list.append(tmp_fil[0])

print('... %s GM maps will be merged' % (str(len(gm_file_list))))

# merge all gray matter probability map across subjects
gm_merged = os.path.join(outdir, 'gm_prob_merged.nii.gz')

merger                    = Merge()
merger.inputs.in_files    = gm_file_list
merger.inputs.dimension   = 't'
merger.inputs.output_type = 'NIFTI_GZ'
merger.inputs.merged_file = gm_merged
merger.run()

# get the average of the merged map
gm_merged_ave = gm_merged[:-7] + '_mean.nii.gz'
print('...average GM map: ', gm_merged_ave)

tmean                    = MeanImage()
tmean.inputs.in_file     = gm_merged
tmean.inputs.dimension   = 'T'
tmean.inputs.output_type = 'NIFTI_GZ'
tmean.inputs.out_file    = gm_merged_ave
tmean.run()

# binarize the group level gray matter map
gm_mask = gm_merged_ave[:-7] + '_mask_065.nii.gz'

binarize = MathsCommand()
binarize.inputs.args     = '-thr  0.65 -bin'
binarize.inputs.in_file  = gm_merged_ave
binarize.inputs.out_file = gm_mask
binarize.run()
