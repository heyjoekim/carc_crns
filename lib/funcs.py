"""
Python File with functions and other variables
    Author: Haejo Kim
    Affiliation: Syracuse University
    Date last edited: Apr. 30, 2024

"""


import numpy as np
import pandas as pd
import scipy

from lib.uranos import URANOS

# Other Functions
def mean_bias_error(xx, yy):
    # Calculate mean bias error
    mbe = np.mean(xx-yy)
    return(mbe)

# constants
crns_x = -211.265  # Detector x pos [m]
crns_y = -167.261  # Detector y pos [m]

# spline model
# make spline model:
HDPE_25mm = pd.read_csv('./data/DRFs/ResponseFunction_HDPE25mm.txt',
                        header=None,
                        sep='\t',
                        names=['E [MeV]','response'])
HDPE_25mm['eV'] = HDPE_25mm['E [MeV]']/1e-6

logx = np.log10(HDPE_25mm['E [MeV]'])
logy = np.log10(HDPE_25mm.response)
lin_interp = scipy.interpolate.interp1d(logx, logy, kind='cubic', fill_value='extrapolate')

log_interp = lambda zz: np.power(10.0, lin_interp(np.log10(zz)))

def readUranosNC(path, run_dir, crns_x, crns_y):
    # read URANOS model output located at folderi
    #   path    : path to general location of model output files
    #   run_dir : working directory where Detector Hits file is located
    #   crns_x  : x direction of CRNS (center is (0,0))
    #   crns_y  : y direction of CRNS (center is (0,0))
    # Outputs:
    #   U       : URANOS Object
    #   U.Hits  : Hits DF
    U = URANOS(folder=path+run_dir)
    # read detector hits and drop dups
    U = U.read_hits().drop_multicounts()

    # recalculate distance to CRNS not located at center
    U.Hits['r'] = np.sqrt((U.Hits['x'] - crns_x)**2+(U.Hits['y'] - crns_y)**2)

    # weight hits using DRF
    U = U.weight_by_detector_response(method='drf',
                                      file = './data/DRFs/ResponseFunction_HDPE25mm.txt')
    U.Hits['Prob'] = log_interp(U.Hits['Energy_[MeV]'])/100
    return(U, U.Hits)


def calcNeutronCounts(hits_df):
    # calculate Filtered Neutron Counts
    return(hits_df['Prob'].sum())

