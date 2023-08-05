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
import sys
import ConfigParser
#sys.path.insert(0, '/media/TOSHIBA EXT/repos/pyFRET/pyfret')
import pyALEX as pyx
import os

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
        auto_dd = config.getfloat('parameters', 'auto_DD')
        auto_da = config.getfloat('parameters', 'auto_DA')
        auto_ad = config.getfloat('parameters', 'auto_AD')
        auto_aa = config.getfloat('parameters', 'auto_AA')
        lk = config.getfloat('parameters', 'leakage')
        dr = config.getfloat('parameters', 'direct')
        T_don = config.getint('parameters', 'T_donor')
        T_acc = config.getint('parameters', 'T_acceptor')
        gamma = config.getfloat('parameters', 'gamma')
        Smin = config.getfloat('parameters', 'Smin')
        Smax = config.getfloat('parameters', 'Smax')
    except:
        raise

    
    try:
        # get plotting parameters for scatter-histogram
        save = config.getboolean('scatterhist', 'save')
        if save:
            outname = config.get('scatterhist', 'outname')
            outtype = config.get('scatterhist', 'filetype')

        # get plotting data for histogram and to save data
        csv_name = config.get('histogram', 'csv_name')
        img = config.getboolean('histogram', 'img')
        if img:
            im_name = config.get('histogram', 'im_name')
            imtype = config.get('histogram', 'imtype')
        gauss = config.getboolean('histogram', 'gauss') 
        if gauss:
            gauss_name = config.get('histogram', 'gauss_name')
    except:
        raise
    print("Config File Read")

    print("Making results directory")
    if not os.path.exists(results_directory):
        os.makedirs(results_directory)    

    # get data
    print("Making ALEX data object")
    files = []
    for i in range(filestart, fileend):
        name = ".".join(["%s%04d" %(filename, i), filetype])
        files.append(name)      
    ALEX_data = pyx.parse_bin(filepath, files)

    # denoise data and analyse
    print("Data Analysis")
    ALEX_data.subtract_bckd(auto_dd, auto_da, auto_ad, auto_aa)
    ALEX_data.thresholder(T_don, T_acc)
    ALEX_data.subtract_crosstalk(lk, dr)

    # make plots
    print("Making plots")
    ALEX_data.scatter_hist(Smin, Smax, save=save, filepath=results_directory, imgname=outname, imgtype=outtype)
    ALEX_data.build_histogram(results_directory, csv_name, image = img, imgname = im_name, imgtype=imtype, gauss = gauss, gaussname = gauss_name)

if __name__ == "__main__":
    configname = sys.argv[1]
    main(configname)