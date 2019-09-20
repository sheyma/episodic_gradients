# run by using the following python interpreter:
# $ simnibs_python tms_03_Efield.py sub-01
# simnibs_python comes with SimNIBS installation

import os, sys
from simnibs import sim_struct, run_simnibs
from simnibs.msh import mesh_io
import numpy as np

sub  = str(sys.argv[1]) # subject id

# In directory & files --> HARD CODED
sub_dir     = '/data/pt_neuam005/simnibs_TMS/subjects'
coilnifti   = '/data/pt_neuam005/simnibs_TMS/MagVenture_MC_B70.nii.gz'

meshfile  = os.path.join(sub_dir, sub,  sub + '.msh')
m2mfile   = os.path.join(sub_dir, sub, 'm2m_' + sub)
outfile   = os.path.join(sub_dir, sub, 'simnibs_simulation_mPFC')
intFile   = os.path.join(sub_dir, sub, 'tms_int_' + sub + '.txt' )
coordFile = os.path.join(sub_dir, sub, 'coordinates_mPFC_' + sub + '.txt' )
handlFile = os.path.join(sub_dir, sub, 'coil_direction_mPFC_' + sub + '.txt' )

tint  = np.loadtxt(intFile).astype(float)
coord = np.loadtxt(coordFile).astype(float)[1:].tolist()[0]
direc = np.loadtxt(handlFile, dtype='str')

if direc == 'right':
    direction = [1,0,0]
elif direc == 'left':
    direction = [-1,0,0]

print(sub, direc, direction)

# Initalize a session
s = sim_struct.SESSION()
s.fnamehead = meshfile
s.subpath   = m2mfile
s.pathfem   = outfile

mesh = mesh_io.Msh(fn=s.fnamehead)

# Initialize a list of TMS simulations
tmslist                 = s.add_tmslist()
tmslist.fnamecoil       =  coilnifti
tmslist.anisotropy_type = 'scalar'

# Initialize coil params
pos = tmslist.add_position()

pos.centre   = coord	             # entry coordinates
pos.distance = 1.                    # coil distance (mm)
pos.didt     = tint * 1e6            # TMS intensity (A/s)
pos.pos_ydir = (direction)           # coil to the right or left
pos.calc_matsimnibs(mesh)            # scalp projection
pos.pos_ydir   = (pos.matsimnibs[0:3,3] + direction).tolist()
pos.matsimnibs = None                # matsimnibs is not recomputed if already there.

# here we go...
s.open_in_gmsh = False
s.map_to_fsavg = True
s.map_to_vol   = True
s.map_to_MNI   = True

run_simnibs(s)
