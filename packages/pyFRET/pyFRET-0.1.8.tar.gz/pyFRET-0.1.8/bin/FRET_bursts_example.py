"""
Copyright (c) 2014 Rebecca R. Murphy
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

from __future__ import print_function
import ConfigParser
import sys
from pyfret import pyFRET as pft
#import pyFRET as pft
import os
import matplotlib.pyplot as plt
import numpy as np

def main(cfgname):
    # open config file
    print("Reading Config File")
    try:
        config = ConfigParser.RawConfigParser({})
        config.read(cfgname)
    except IOError:
        raise

    # read input parameters
    try:
        filepath = config.get('input', 'filepath')
        filename = config.get('input', 'filename')
        filestart = config.getint('input', 'start')
        fileend = config.getint('input', 'end')
        filetype = config.get('input', 'extension')
        results_directory = config.get('input', 'results_directory')
    except:
        raise

    # read analysis parameters
    try:
        N_D = config.getfloat('parameters', 'N_D')
        N_A = config.getfloat('parameters', 'N_A')
        ctk_da = config.getfloat('parameters', 'ctk_da')
        ctk_ad = config.getfloat('parameters', 'ctk_ad')
    except:
        raise

    # read APBS parameters
    try:
        T1 = config.getfloat('APBS', 'T')
        L1 = config.getfloat('APBS', 'L')
        M1 = config.getfloat('APBS', 'M') 
    except:
        raise

    # read DCBS parameters
    try:
        T2 = config.getfloat('DCBS', 'T')
        L2 = config.getfloat('DCBS', 'L')
        M2 = config.getfloat('DCBS', 'M') 
    except:
        raise

    # read plotting parameters
    try:
        bin_min = config.getfloat('plotting', 'bin_min')
        bin_max = config.getfloat('plotting', 'bin_max')
        bin_width = config.getfloat('plotting', 'bin_width') 
        image = config.getboolean('plotting', 'image') 
        image_type = config.get('plotting', 'image_type')
        gauss = config.getboolean('plotting', 'fit_gauss')

        APBS_csv = config.get('plotting', 'APBS_csv')
        APBS_image = config.get('plotting', 'APBS_image')
        APBS_hist = config.get('plotting', 'APBS_hist')
        DCBS_csv = config.get('plotting', 'DCBS_csv')
        DCBS_image = config.get('plotting', 'DCBS_image')
        DCBS_hist = config.get('plotting', 'DCBS_hist')
    except:
        raise

    # read RASP parameters
    try:
        Emin = config.getfloat('RASP', 'Emin')
        Emax = config.getfloat('RASP', 'Emax')
        Tmin = config.getint('RASP', 'Tmin')
        Tmax = config.getint('RASP', 'Tmax')

        RASP_csv = config.get('RASP', 'RASP_csv')
        RASP_hist = config.get('RASP', 'RASP_hist')
    except:
        raise

    print("Config file read") 
    print("Making results directory")
    if not os.path.exists(results_directory):
        os.makedirs(results_directory)

    # get data
    print("Making FRET data object") 
    files = []
    for i in range(filestart, fileend):
        name = ".".join(["%s%04d" %(filename, i), filetype])
        files.append(name)
    FRET_data = pft.parse_bin(filepath, files)  

    # run burst search
    # apbs
    print("Burst search: APBS")
    APBS_bursts = FRET_data.APBS(T1, M1, L1)
    APBS_bursts.denoise_bursts(N_D, N_A)
    APBS_bursts.subtract_crosstalk(ctk_ad, ctk_da)
    APBS_bursts.scatter_intensity(results_directory, APBS_image)
    APBS_bursts.build_histogram(results_directory, APBS_csv, gamma=1.0, bin_min=bin_min, bin_max=bin_max, bin_width=bin_width, image=image, imgname=APBS_hist, imgtype=image_type, gauss=gauss, gaussname=None)
    plt.hist(APBS_bursts.burst_len, bins=np.arange(0, 300, 10))
    plt.show()

    # dcbs
    print("Burst search: DCBS")
    DCBS_bursts = FRET_data.DCBS(T2, M2, L2)
    DCBS_bursts.denoise_bursts(N_D, N_A)
    DCBS_bursts.subtract_crosstalk(ctk_ad, ctk_da)
    DCBS_bursts.scatter_intensity(results_directory, DCBS_image)
    DCBS_bursts.build_histogram(results_directory, DCBS_csv, gamma=1.0, bin_min=bin_min, bin_max=bin_max, bin_width=bin_width, image=image, imgname=DCBS_hist, imgtype=image_type, gauss=gauss, gaussname=None)
    plt.hist(APBS_bursts.burst_len, bins=np.arange(0, 300, 10))
    plt.show()

    # RASP
    print("RASP")
    recurrent_bursts = APBS_bursts.RASP(Emin, Emax, Tmin, Tmax)
    recurrent_bursts.build_histogram(results_directory, RASP_csv, gamma=1.0, bin_min=bin_min, bin_max=bin_max, bin_width=bin_width, image=image, imgname=RASP_hist, imgtype=image_type, gauss=gauss, gaussname=None)


if __name__ == "__main__":
    configname = sys.argv[1]
    main(configname)