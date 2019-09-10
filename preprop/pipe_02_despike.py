import sys
from nipype.interfaces import afni
from nipype.interfaces.fsl.maths import BinaryMaths

### despikes fMRI timeseries for subjects with > 1mm motion peak

# inputname = 'sub-05_ses-03_task-future_bold_space-MNI152NLin2009cAsym_preproc.nii.gz'

inputname  = sys.argv[1]
outputname = inputname[:-7] + '_despiked.nii.gz'

# afni 3dDespike
despike = afni.Despike()
despike.inputs.in_file  = inputname
despike.inputs.out_file = outputname
despike.inputs.args     = '-cut 1.0 4.0'
print(despike.cmdline)
despike.run()

# subtract despiked image from the original to check the diff
subtract = BinaryMaths()
subtract.inputs.in_file      = inputname
subtract.inputs.operand_file = outputname
subtract.inputs.operation    = 'sub'
subtract.inputs.out_file     = outputname[:-7] + '_diff.nii.gz'
print(subtract.cmdline)
subtract.run()