# run by using the following python interpreter:
# $ simnibs_python test.py
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
outfile   = os.path.join(sub_dir, sub, 'simnibs_simulation')
intFile   = os.path.join(sub_dir, sub, 'tms_int_' + sub + '.txt' )
coordFile = os.path.join(sub_dir, sub, 'coordinates_' + sub + '.txt' )

tint  = np.loadtxt(intFile).astype(float)
coord = np.loadtxt(coordFile).astype(float)[1:].tolist()[0]

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

# Initialize a TEMPORARY coil position to get params
pos = tmslist.add_position()

pos.centre   = coord	             # entry coordinates
pos.distance = 1.                    # coil distance (mm)
pos.didt     = tint * 1e6            # TMS intensity (A/s)
pos.pos_ydir = ([1,0,0])             # coil towards right
pos.calc_matsimnibs(mesh)            # scalp projection
pos.pos_ydir = (pos.matsimnibs[0:3,3] + [1,0,0]).tolist()
A = pos.centre
B = pos.pos_ydir  #### params needed !!!

################# HERE WE GO ....
k = sim_struct.SESSION()

k.fnamehead = meshfile
k.subpath   = m2mfile
k.pathfem   = outfile

mylist = k.add_tmslist()
mylist.fnamecoil       =  coilnifti
mylist.anisotropy_type = 'scalar'

POS = mylist.add_position()
POS.centre   = A	                 # entry coordinates
POS.distance = 1.                    # coil distance (mm)
POS.didt     = tint * 1e6            # TMS intensity (A/s)
POS.pos_ydir = B

k.open_in_gmsh = False
k.map_to_vol   = True
k.map_to_MNI   = True

run_simnibs(k)
