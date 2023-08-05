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
#sys.path.insert(0, '/media/TOSHIBA EXT/repos/pyFRET/pyfret')
import pyFRET as pft
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
        auto_d = config.getfloat('parameters', 'auto_donor')
        auto_a = config.getfloat('parameters', 'auto_acceptor')
        ctk_da = config.getfloat('parameters', 'ctk_da')
        ctk_ad = config.getfloat('parameters', 'ctk_ad')
        thresholding = config.get('parameters', 'thresholding')
        if thresholding == "AND":
            T_don = config.getint('parameters', 'T_donor')
            T_acc = config.getint('parameters', 'T_acceptor')
        elif thresholding == "SUM":
            T_sum = config.getint('parameters', 'T_sum')
        gamma = config.getfloat('parameters', 'gamma')
    except:
        raise

    # read plotting parameters
    try:
        csv_name = config.get('histogram', 'csv_name') 
        image = config.getboolean('histogram', 'image')
        if image:
            im_name = config.get('histogram', 'image_name')
            im_type = config.get('histogram', 'image_type') 
        gauss = config.getboolean('histogram', 'fit_gauss')
        if gauss:
            gauss_name = config.get('histogram', 'gauss_name')

        hex_name = config.get('hexplot', 'filename')
        hex_type = config.get('hexplot', 'filetype')
        bin_type = config.get('hexplot', 'binning')

        z_name = config.get('3Dplot', 'filename')
        z_type = config.get('3Dplot', 'filetype')

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

    # plot raw data
    print("Plotting Raw Data") 
    FRET_data.make_3d_plot(results_directory, z_name, imgtype=z_type)
    FRET_data.make_hex_plot(results_directory, hex_name, imgtype=hex_type, binning=bin_type)

    # analyse data
    print("Data Analysis")
    FRET_data.subtract_bckd(auto_d, auto_a)
    FRET_data.subtract_crosstalk(ctk_da, ctk_ad)
    FRET_data.threshold_AND(T_don, T_acc)
    E = FRET_data.proximity_ratio(gamma=gamma)

    # plot analysed data
    print("Making histogram")
    FRET_data.build_histogram(results_directory, csv_name, bin_min=0.0, bin_max=1.0, bin_width=0.02, image = image, imgname = im_name, imgtype=im_type, gauss = gauss, gaussname = gauss_name)
    FRET_data.make_3d_plot(results_directory, z_name, imgtype=z_type)


if __name__ == "__main__":
    configname = sys.argv[1]
    main(configname)