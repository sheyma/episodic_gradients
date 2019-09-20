# $ simnibs_python tms_04_Efield_group.py

import os
import numpy as np
import simnibs

indir    = '/data/pt_neuam005/simnibs_TMS/subjects/'
outdir   = '/data/pt_neuam005/simnibs_TMS/subjects_group/'
subdir   = 'simnibs_simulation/fsavg_overlays'
suffix   = '_TMS_1-0001_MagVenture_MC_B70_nii_scalar_fsavg.msh'
lisfname = '/data/pt_neuam005/FSTIM_1_Think_preprocessed/subject_list.txt'

# get subject id's as a list
with open(lisfname) as f:
    content = f.readlines()
subjects = [x.strip('\n') for x in content]

#subjects = ['sub-01', 'sub-05']

# Go though each subject and extract E_normal
normals = []
for sub in subjects:
    print(sub)
    # read the msh file
    submeshfile   = os.path.join(indir, sub, subdir, sub + suffix)
    results_fsavg = simnibs.msh.read_msh(submeshfile)
    normals.append(results_fsavg.field['E_norm'].value)

# calculate the average and std
normals = np.vstack(normals)
avg = np.mean(normals, axis=0)
std = np.std(normals, axis=0)

# Visualize Mean and Std
## cleanup the last model by removing the fields
results_fsavg.nodedata = []

## add the average and standard deviations as nodal data
results_fsavg.add_node_field(avg, 'E_normal_avg')
results_fsavg.add_node_field(std, 'E_normal_std')

print('MAX AVERAGED VALUE: ', results_fsavg.field['E_normal_avg'].value.max())

view = results_fsavg.view(visible_fields='E_normal_std')
view.show()

## write out results as a .msh and the .opt file for visualization later
results_fsavg.write(outdir + 'average_tmp.msh')
view.write_opt(outdir + 'average_tmp.msh')
