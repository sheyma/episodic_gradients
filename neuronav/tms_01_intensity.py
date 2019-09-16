import os
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd

file_in  = '/data/pt_neuam005/simnibs_TMS/Participants_data_intake_v2.xlsx'
file_out = '/data/pt_neuam005/simnibs_TMS/tms_estimate.xlsx'
outpath  = '/data/pt_neuam005/simnibs_TMS/subjects/'
db       = pd.read_excel(file_in, index_col='VP_Number')

### HARD CODED FROM TMS MASCHINE
x = np.array([10, 20, 30, 40, 50, 50, 70, 80, 90, 100])
y = np.array([13, 27, 44, 59, 75, 90, 106, 121, 137, 153])

### LINEAR FIT
a, b, r_value, p_value, std_err = stats.linregress(x, y)
y_fit  = a * x + b

### FIT SUBJECT DATA
myindex    = db.index.dropna()
x_subjects = (np.array(db.loc[myindex]['RTMS_intensity'].values))
y_estimate = a * x_subjects + b

### PLOT
fig = plt.figure()
line1 = plt.plot(x,y, 'o', label='coil')
line2 = plt.plot(x, y_fit, label= 'coil fit')
line3 = plt.plot(x_subjects, y_estimate, 'or', label='subjects')
plt.legend()
plt.xlabel('Instensity Percentage')
plt.ylabel('Intensity [A/$\mu$ s] ')
#plt.show()

# GENERATE NEW DATA FRAME
rColumns = ['subject_id', 'TMS_est', 'RTMS_int', 'mpfc_direc']
df       = pd.DataFrame(index=myindex,
                        columns=rColumns)

# SAVE VALUES INDIVIDUALLY FOR EACH SUBJECT
for idx in myindex:
    # get RTMS_intensity and fit it to linear regression
    df.loc[idx]['RTMS_int'] = db.loc[idx]['RTMS_intensity']
    df.loc[idx]['TMS_est']  = a * (db.loc[idx]['RTMS_intensity']) + b

    # get mPFC stimulation coil direction
    if db.loc[idx]['Stimulation_01'] == 'mPFC':
        df.loc[idx]['mpfc_direc'] = db.loc[idx]['Handle_Dir.1']
    if db.loc[idx]['Stimulation_02'] == 'mPFC':
        df.loc[idx]['mpfc_direc'] = db.loc[idx]['Handle_Dir.2']
    if db.loc[idx]['Stimulation_03'] == 'mPFC':
        df.loc[idx]['mpfc_direc'] = db.loc[idx]['Handle_Dir.3']

    # save...
    if idx < 10:
        df.loc[idx]['subject_id'] = 'sub-0' + str(int(idx))

        if os.path.exists(outpath + 'sub-0' + str(int(idx)))==True:
            #print('sub-0' + str(int(idx)), np.array([df.loc[idx]['TMS_est']]))
            np.savetxt(outpath + 'sub-0' + str(int(idx)) +
                       '/tms_int_sub-0' + str(int(idx)) + '.txt',
                       np.array([df.loc[idx]['TMS_est']]), fmt='%2.2f')

            np.savetxt(outpath + 'sub-0' + str(int(idx)) +
                       '/mpfc_dir_sub-0' + str(int(idx)) + '.txt',
                       np.array([df.loc[idx]['mpfc_direc']]), fmt='%s')

    else:
        df.loc[idx]['subject_id'] = 'sub-' + str(int(idx))

        if os.path.exists(outpath + 'sub-' + str(int(idx)))==True:
            #print('sub-' + str(int(idx)), np.array([df.loc[idx]['TMS_est']]))
            np.savetxt(outpath + 'sub-' + str(int(idx)) +
                        '/tms_int_sub-' + str(int(idx)) + '.txt',
                        np.array([df.loc[idx]['TMS_est']]), fmt='%2.2f')

            np.savetxt(outpath + 'sub-' + str(int(idx)) +
                       '/mpfc_dir_sub-' + str(int(idx)) + '.txt',
                       np.array([df.loc[idx]['mpfc_direc']]), fmt='%s')

#df.to_excel(file_out)
