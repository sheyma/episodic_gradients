import os
import numpy as np
import simnibs

indir    = '/data/pt_neuam005/simnibs_TMS/subjects/'
subdir   = 'simnibs_simulation/'
suffix   = '_TMS_1-0001_MagVenture_MC_B70_nii_scalar_fsavg.msh'
subjects = ['sub-01', 'sub-05']


# Go though each subject and extract E_normal
normals = []
for sub in subjects:

    # read the msh file
    submeshfile = os.path.join(indir, sub, subdir, sub + suffix)

    submesh     = simnibs.msh.read_msh(submeshfile)

    print(sub, submesh.field['normE'].value.shape, submesh.field['normE'].value.min(), submesh.field['normE'].value.max())
    # extract the normals
    normals.append(submesh.field['normE'].value)

normals = np.vstack(normals)