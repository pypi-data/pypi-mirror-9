# Copyright (c) 2014 Rebecca R. Murphy
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import struct
import csv

try:
    import numpy as np
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    import matplotlib
    import math as ma
    from sklearn import mixture
    #print "Imports all good"
except:
    print "Numerical libraries not present in your systems"


def _runningMean(x, T):
    """
    Calculate running sum over array x with summation window T.
    Called by APBS and DCBS to calculate number of photons arriving within time window T

    Arguments:
    * x: a numpy array of photon counts
    * T: window length (number of array entries) over which to sum photons
    """
    return np.convolve(x, np.ones((T,)), mode='same')

class FRET_data:

    """
    This class holds single molecule data.

    It has two attributes, donor and acceptor to hold photon counts from the donor and acceptor channels respectively.
    These are numpy arrays.

    It can be initialized from two lists or two arrays of photon counts: data = FRET_data(donor_events_list, acceptor_events_list)

    """

    def __init__(self, donor, acceptor):
        """
        Initialize the FRET data object.

        Arguments:

        * donor: list or array of donor time-bins
        * acceptor: list or array of acceptor time-bins.

        """
        self.donor = np.array(donor).astype(float)
        self.acceptor = np.array(acceptor).astype(float)    
    
    def subtract_bckd(self, bckd_d, bckd_a):
        """
        Subtract background noise from donor and acceptor channel data.

        Arguments:

        * bckd_d: average noise per time-bin in the donor channel
        * bckd_a: average noise per time-bin in the acceptor channel
        """
        self.donor = self.donor - bckd_d
        self.acceptor = self.acceptor - bckd_a 
        return self


    def subtract_crosstalk(self, ct_d, ct_a):
        """
        Subtract crosstalk from donor and acceptor channels.

        Arguments:

        * ct_d: fractional cross-talk from donor to acceptor (float between 0 and 1)
        * ct_a: fractional cross-talk from acceptor to donor (float between 0 and 1)
        """
        donor_cross_talk = self.donor * ct_d
        acceptor_cross_talk = self.acceptor * ct_a
        self.donor = self.donor - acceptor_cross_talk
        self.acceptor = self.acceptor - donor_cross_talk
        return self
        

    def threshold_AND(self, D_T, A_T):
        """
        Select data based on the AND thresholding criterion.

        Arguments:

        * D_T: threshold for the donor channel
        * A_T: threshold for the acceptor channel

        An event is above threshold if nD > donor_threshold AND nA > acceptor_threshold
        for nD and nA photons in the donor and acceptor channels respectively
        """
        select = (self.donor > D_T) & (self.acceptor > A_T)
        self.donor = self.donor[select]
        self.acceptor = self.acceptor[select]
        return self
        
    def threshold_OR(self, D_T, A_T):
        """
        Select data based on the OR thresholding criterion.

        Arguments:

        * D_T: threshold for the donor channel
        * A_T: threshold for the acceptor channel

        An event is above threshold in nD > donor_threshold OR nA > acceptor_threshold
        for nD and nA photons in the donor and acceptor channels respectively
        """
        select = (self.donor > D_T) | (self.acceptor > A_T)
        self.donor = self.donor[select]
        self.acceptor = self.acceptor[select]
        return self

    def threshold_SUM(self, T):
        """
        Select data based on the SUM thresholding criterion.

        Arguments:
        T: threshold above which a time-bin is accepted as a fluorescent burst

        An event is above threshold in nD  + nA > threshold
        for nD and nA photons in the donor and acceptor channels respectively
        """
        select = (self.donor + self.acceptor > T)
        self.donor = self.donor[select]
        self.acceptor = self.acceptor[select]
        return self

    def proximity_ratio(self, gamma=1.0):
        """
        Calculate the proximity ratio (E) and return an array of values.

        Arguments:
        None    

        Keyword arguments:

        * gamma (default value 1.0): the instrumental gamma-factor

        Calculation: 

        E = nA / (nA + gamma*nD) for nA and nD photons in the acceptor and donor channels respectively
        """
        E = self.acceptor / (self.acceptor + (gamma * self.donor))
        return E

    # burst search
    def APBS(self, T, M, L):
        """
        All-photon bust search algorithm as implemented in Nir et al. J Phys Chem B. 2006 110(44):22103-24.
        Returns a FRET_bursts object.

        Arguments:
        * T: time-window (in bins) over which to sum photons 
        * M: number of photons in window of length T required to identify a potential burst. 
        * L: total number of photons required for an identified burst to be accepted.

        From Nir et al.:
        The start (respectively, the end) of a potential burst is detected when the number of photons in the averaging window of duration T is larger (respectively, smaller) than the minimum number of photons M.
        A potential burst is retained if the number of photons it contains is larger than a minimum number L.
        """

        data = self.donor + self.acceptor
        means = _runningMean(data, T)
        donor_bursts, acceptor_bursts, b_start, b_end = self._APBS_bursts(data, means, M, L)
        FRET_bursts_obj = FRET_bursts(donor_bursts, acceptor_bursts, b_start, b_end)
        return FRET_bursts_obj


    def _APBS_bursts(self, data, means, M, L):
        assert len(data) == len(means)
        donor_bursts = []
        acceptor_bursts = []
        burst_starts = []
        burst_ends = []
        positions = []
        bursts = []
        burst = 0
        b_donor = 0
        b_acceptor = 0

        burst_len = 0
        collecting = False
        for pos in range(len(data)):
            if means[pos] >= M:
                collecting = True
                burst_len += 1
                burst += data[pos]
                b_donor += self.donor[pos]
                b_acceptor += self.acceptor[pos]
            else:
                if collecting:
                    bursts.append(burst)
                    donor_bursts.append(b_donor)
                    acceptor_bursts.append(b_acceptor)
                    burst_pos = pos - (float(burst_len) / 2)
                    burst_starts.append(pos - burst_len)
                    burst_ends.append(pos)
                    positions.append(burst_pos)
                burst = 0
                b_donor = 0
                b_acceptor = 0
                burst_len = 0
                collecting = False

        bursts = np.array(bursts)
        donor_bursts = np.array(donor_bursts)
        acceptor_bursts = np.array(acceptor_bursts)
        burst_starts = np.array(burst_starts)
        burst_ends = np.array(burst_ends)
        positions = np.array(positions)

        select = bursts >= L
        bursts = bursts[select]
        positions = positions[select]
        donor_bursts = donor_bursts[select]
        acceptor_bursts = acceptor_bursts[select]
        burst_starts = burst_starts[select]
        burst_ends = burst_ends[select]

        return donor_bursts, acceptor_bursts, burst_starts, burst_ends

    def DCBS(self, T, M, L):
        """
        Dual-channel bust search algorithm as implemented in Nir et al. J Phys Chem B. 2006 110(44):22103-24.
        Returns a FRET_bursts object.

        Arguments:
        * T: time-window (in bins) over which to sum photons 
        * M: number of photons in window of length T required to identify a potential burst. 
        * L: total number of photons required for an identified burst to be accepted.

        From Nir et al.:
        The start (respectively, the end) of a potential burst is detected when the number of photons in the averaging window of duration T is larger (respectively, smaller) than the minimum number of photons M.
        A potential burst is retained if the number of photons it contains is larger than a minimum number L.
        """

        donor_means = _runningMean(self.donor, T)
        acceptor_means = _runningMean(self.acceptor, T)
        donor_bursts, acceptor_bursts, b_start, b_end = self._DCBS_bursts(donor_means, acceptor_means, M, L)
        FRET_bursts_obj = FRET_bursts(donor_bursts, acceptor_bursts, b_start, b_end)
        return FRET_bursts_obj

    def _DCBS_bursts(self, donor_means, acceptor_means, M, L):
        assert len(self.donor) == len(donor_means)
        donor_bursts = []
        acceptor_bursts = []
        burst_starts = []
        burst_ends = []
        positions = []
        b_donor = 0
        b_acceptor = 0

        burst_len = 0
        collecting = False
        for pos in range(len(self.donor)):
            # condition depends on both channels
            if (donor_means[pos] >= M) & (acceptor_means[pos] >= M):
                collecting = True
                burst_len += 1
                b_donor += self.donor[pos]
                b_acceptor += self.acceptor[pos]
            else:
                if collecting:
                    donor_bursts.append(b_donor)
                    acceptor_bursts.append(b_acceptor)
                    burst_pos = pos - (float(burst_len) / 2)
                    burst_starts.append(pos - burst_len)
                    burst_ends.append(pos)
                    positions.append(burst_pos)
                b_donor = 0
                b_acceptor = 0
                burst_len = 0
                collecting = False

        donor_bursts = np.array(donor_bursts)
        acceptor_bursts = np.array(acceptor_bursts)
        burst_starts = np.array(burst_starts)
        burst_ends = np.array(burst_ends)
        positions = np.array(positions)

        select = (donor_bursts >= L) & (acceptor_bursts >= L) 
        positions = positions[select]
        donor_bursts = donor_bursts[select]
        acceptor_bursts = acceptor_bursts[select]
        burst_starts = burst_starts[select]
        burst_ends = burst_ends[select]

        return donor_bursts, acceptor_bursts, burst_starts, burst_ends



    def make_3d_plot(self, filepath, imgname, imgtype="pdf", labels = ["Donor", "Acceptor", "Frequency"]):
        """
        Make a 3D histogram of donor and acceptor photon counts.

        Arguments:

        * filepath: path to folder where data will be saved
        * filename: name of image file to save plot

        Keyword arguments:

        * filetype: image type (as string). Default "pdf". Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        * labels: axes labels, list of strings ["Xtitle", "Ytitle", "Ztitle"]. Default ["Donor", "Acceptor", "Frequency"]
        """

        fullname = ".".join([imgname, imgtype])
        max_val = max(max(self.donor), max(self.acceptor))
        big_matrix = np.zeros((ma.ceil(max_val)+1, ma.ceil(max_val)+1))
        for (i, j) in zip(self.donor, self.acceptor):
            big_matrix[i][j] += 1

        fig = plt.figure()
        ax = fig.gca(projection="3d")
        ax.locator_params(nbins=4)
        X = np.arange(0, max_val+1, 1)
        Y = np.arange(0, max_val+1, 1)
        X, Y = np.meshgrid(X, Y)
        surf = ax.plot_surface(X, Y, big_matrix, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0, antialiased=False)
        #fig.colorbar(surf, shrink=0.5, aspect=5)
        ax.set_xlabel("\n%s" %labels[0])
        ax.set_ylabel("\n%s" %labels[1])
        ax.set_zlabel("\n%s" %labels[2])
        figname = os.path.join(filepath, fullname)
        plt.savefig(figname)
        plt.close()
        return self

    def make_hex_plot(self, filepath, imgname, imgtype="pdf", labels = ["Donor", "Acceptor"], xmax = None, ymax = None, binning=None):
        """
        Make a 2D representation of donor and acceptor photon count frequencies.

        Based on the matplotlib.pyplot construction "hexbin": http://matplotlib.org/api/pyplot_api.html

        Arguments:

        * filepath: path to folder where data will be saved
        * imgname: name of image file to save plot

        Keyword arguments:

        * imgtype: image type (as string). Default "pdf". Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        * labels: axes labels, list of strings ["Xtitle", "Ytitle"]. Default ["Donor", "Acceptor"]
        * xmax: maximum x-axis value. Default None (maximum will be the brightest donor event)
        * ymax: maximum x-axis value. Default None (maximum will be the brightest acceptor event)
        * binning: type of binning to use for plot. Default: None (bin colour corresponds to frequency). 
            Accepted vals: "log" (bin colour corresponds to frequency), integer (specifies number of bins), sequence (specifies bin lower bounds)
        """

        fullname = ".".join([imgname, imgtype])
        plt.hexbin(self.donor, self.acceptor, bins=binning)
        plt.colorbar()
        plt.xlabel("\n%s" %labels[0])
        plt.ylabel("\n%s" %labels[1])
        figname = os.path.join(filepath, fullname)
        if (xmax != None) & (ymax != None):
            plt.xlim(0, xmax)
            plt.ylim(0, ymax)
        plt.savefig(figname)
        plt.close()
        return self
    
    def build_histogram(self, filepath, csvname, gamma=1.0, bin_min=0.0, bin_max=1.0, bin_width=0.02, image = False, imgname = None, imgtype=None, gauss = True, gaussname = None, n_gauss=1):
        """
        Build a proximity ratio histogram and save the frequencies and bin centres as a csv file. 
        Optionally plot and save a graph and perform a simple gaussian fit.

        Arguments:

        * E: array of FRET efficiecies
        * filepath: path to folder where the histogram will be saved (as a string)
        * csvname: the name of the file in which the histogram will be saved (as a string)

        Keyword arguments:

        * gamma: Instrumental gamma factor. (float, default value 1.0)
        * bin_min: the minimum value for a histogram bin (default 0.0)
        * bin_max: the maximum value for a histogram bin (default 1.0)
        * bin_width: the width of one bin (default 0.02)
        * image: Boolean. True plots a graph of the histogram and saves it (default False)
        * imgname: the name of the file in which the histogram graph will be saved (as a string)
        * imgtype: filetype of histogram image. Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        * gauss: Boolean. True will fit the histogram with a single gaussian distribution (default False)
        * gaussname: the name of the file in which the parameters of the Gaussian fit will be saved
        * n_gauss: number of Gaussain distributions to fit. Default = 1
        """

        E = self.proximity_ratio(gamma)

        csv_title = ".".join([csvname, "csv"])
        csv_full = os.path.join(filepath, csv_title)
        with open(csv_full, "w") as csv_file:
            bins = np.arange(bin_min, bin_max, bin_width)
            freq, binss, _ = plt.hist(E, bins, facecolor = "grey")
            bin_centres = []
            for i in range(len(binss)-1):
                bin_centres.append((binss[i+1] + binss[i])/2)
            for bc, fr in zip(bin_centres, freq):
                csv_file.write("%s, %s \n" %(bc, fr))
        if image == True:
            img_name = ".".join([imgname, imgtype])
            img_path = os.path.join(filepath, img_name)
            plt.xlabel("FRET Efficiency")
            plt.ylabel("Number of Events")
            plt.savefig(img_path)
            plt.cla()
        if gauss == True and gaussname != None:
            # fit
            ms, cs, ws = fit_mixture(E, ncomp=n_gauss)

            # set up
            histo = plt.hist(E, bins, label='Test data', facecolor = "grey", normed=True)
            csv_title = ".".join([gaussname, "csv"])
            csv_full = os.path.join(filepath, csv_title)
            csv_file = open(csv_full, "w")
            csv_file.write("E, sigma, weight\n")

            # plot and write to file
            for w, m, c in zip(ws, ms, cs):
                plt.plot(histo[1],w*matplotlib.mlab.normpdf(histo[1],m,c), linewidth=3)
                csv_file.write("%s,%s,%s\n" % (m, c, w))

            plt.xlabel("FRET Efficiency")
            plt.ylabel("Number of Events")
            gauss_title = ".".join([gaussname, imgtype])
            gauss_title = os.path.join(filepath, gauss_title)
            plt.savefig(gauss_title)

            csv_file.close()            
        plt.close()
        return self

class FRET_bursts(FRET_data):
    """
    This class holds single molecule burst data. Photon bursts are stored in numpy arrays. There is a separate array for each of the two
    photon streams, for the start and end of each burst and for the burst duration.

    The two attributes corresponding to bursts from the four photon streams from a FRET experiment are numpy arrays:

    * donor: The donor channel
    * acceptor: The acceptor channel

    The three further attributes, corresponding to burst duration, burst start time and burst end time are also numpy arrays:

    * burst_len: Length (in bins) of each identified burst
    * burst_starts: Start time (bin number) of each identified burst
    * burst_ends: End time (bn number) of each identified burst
    
    The class can be initialized directly from four lists or arrays: two of burst photon counts; the burst start times and the burst end times: 
    bursts = FRET_bursts(donor_bursts, acceptor_bursts, burst_starts, burst_ends).
    
    However, it is more typically achieved by running the APBS or DCBS algorithm that forms part of the FRET_data class.

    """


    def __init__(self, donor, acceptor, burst_starts, burst_ends):
        FRET_data.__init__(self, donor, acceptor)
        self.total = self.donor + self.acceptor
        self.burst_starts = burst_starts
        self.burst_ends = burst_ends
        self.burst_len = self.burst_ends - self.burst_starts

    def denoise_bursts(self, N_D, N_A):
        """
        Subtract background noise from donor and acceptor bursts.

        Arguments:

        * N_D: average noise per time-bin in the donor channel
        * N_A: average noise per time-bin in the acceptor channel
        """
        
        donor_noise = N_D * self.burst_len
        acceptor_noise = N_A * self.burst_len

        self.donor = self.donor - donor_noise
        self.acceptor = self.acceptor - acceptor_noise

        return self

    def scatter_intensity(self, filepath, imgname, imgtype="pdf", labels = ["Burst Duration", "Burst Intensity"]):
        """
        Plot a scatter plot of burst brightness vs burst duration

        Arguments:
        * filepath: file path to the directory in which the image will be saved
        * imgname: name under which the image will be saved

        Keyword arguments:
        * imgtype: filetype of histogram image. Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        * labels: labels for x and y axes, as a 2-element list of strings: ["x-title", "y-title"]. Default value: ["Burst Duration", "Burst Intensity"]
        """

        fullname = ".".join([imgname, imgtype])
        figname = os.path.join(filepath, fullname)
        plt.scatter(self.burst_len, self.total)
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])
        plt.savefig(figname)
        plt.close()
        return self

    def RASP(self, Emin, Emax, Tmin, Tmax, gamma=1.0):
        """
        Recurrence Analysis of Single Particles analysis as implemented in Hoffmann et al. Phys Chem Chem Phys. 2011 13(5):1857-1871.
        Returns a FRET_bursts object.

        Arguments:
        * Emin: minimum value of E (proximity ratio) to consider for initial bursts
        * Emax: maximum value of E (proximity ratio) to consider for initial bursts
        * Tmin: start time (in number of bins after the initial burst) to search for recurrent bursts 
        * Tmax: end time (in number of bins after the initial burst) to search for recurrent bursts
        
        Keyword Arguments:
        * gamma: value of instrumental gamma factor to use in calculating the proximity ratio. Default value = 1.0.

        From Hoffmann et al.:
        First, the bursts b2 must be detected during a time interval between t1 and t2 (the 'recurrence interval', T = (t1,t2)) 
        after a previous burst b1 (the 'initial burst'). Second, the initial bursts must yield a transfer efficiency, E(b1), 
        within a defined range, Delta E1 (the 'initial E range'). 

        In this implementation, Tmin and Tmax correspond to t1 and t2 respectively. The initial E range lies between Emin and Emax.

        """

        E1 = self.proximity_ratio(gamma)
        E_select = (E1 > Emin) & (E1 < Emax)

        E_sel = E1[E_select]
        end_sel = self.burst_ends[E_select]

        T_start = end_sel + Tmin
        T_end = end_sel + Tmax

        Eevents = np.array([])
        donor = np.array([])
        acceptor = np.array([])
        b_start = np.array([])
        b_end = np.array([])

        for s, e in zip(T_start, T_end):
            sel = (self.burst_starts >= s) & (self.burst_starts <= e)
            Eevents = np.hstack((Eevents, E1[sel]))
            donor = np.hstack((donor, self.donor[sel]))
            acceptor = np.hstack((acceptor, self.acceptor[sel]))
            b_start = np.hstack((b_start, self.burst_starts[sel]))
            b_end = np.hstack((b_end, self.burst_ends[sel]))
        recurrent_bursts = FRET_bursts(donor, acceptor, b_start, b_end)
        return recurrent_bursts


def parse_csv(filepath, filelist, delimiter=","):
    """
    Read data from a list of csv and return a FRET_data object.

    Arguments:

    * filepath: the path to the folder containing the files
    * filelist: list of files to be analysed

    Keyword arguments:

    * delimiter (default ","): the delimiter between values in a row of the csv file.

    This function assumes that each row of your file has the format:
    "donor_item,acceptor_item" 

    If your data does not have this format (for example if you have separate files for donor and acceptor data), this function will not work well for you.
    """
    donor_data = []
    acceptor_data = []
    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        with open(current_file) as csv_file:
            current_data = csv.reader(csv_file, delimiter=',')
            for row in current_data:
                donor_data.append(float(row[0]))
                acceptor_data.append(float(row[1]))
    FRET_data_obj = FRET_data(donor_data, acceptor_data)
    return FRET_data_obj

def parse_bin(filepath, filelist, bits=8):
    """
    Read data from a list of binary files and return a FRET_data object.

    Arguments:

    * filepath: the path to the folder containing the files
    * filelist: list of files to be analysed

    Keyword arguments:

    * bits (default value 8): the number of bits used to store a donor-acceptor pair of time-bins

    **Note: This file structure is probably specific to the Klenerman group's .dat files.**
        **Please don't use it unless you know you have the same filetype!** 
    """
    byte_order = sys.byteorder
    try:
        if byte_order == "little":
            edn = '>ii'
        elif byte_order == "big":
            edn = '<ii'
    except ValueError:
        print "Unknown byte order"
        raise
    donor_data = []
    acceptor_data = []
    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        counter = 0
        data = []
        with open(current_file, "rb") as f:
            x = f.read(bits)
            while x:
                data.append(struct.unpack(edn, x))
                x = f.read(bits)
        #return np.array(data)
        for tup in data:
            donor_data.append(float(tup[0]))
            acceptor_data.append(float(tup[1]))
    FRET_data_obj = FRET_data(donor_data, acceptor_data)
    return FRET_data_obj

# def _fit_gauss(bin_centres, frequencies, p0=[1.0, 0.0, 1.0]):
#     """
#     Fit a histogram with a single gaussian distribution.

#     Arguments:

#     * bin_centres: list of histogram bin centres
#     * frequencies: list of histogram bin frequencies

#     Keyword arguments:

#     p0: initial values for gaussian fit as a list of floats: [Area, mu, sigma]. (Default: [1.0, 0.0, 1.0])
#     """
#     def gauss(x, *p):
#         A, mu, sigma = p
#         return A*np.exp(-(x-mu)**2/(2.*sigma**2))
#     coeff, var_matrix = curve_fit(gauss, bin_centres, frequencies, p0)
#     hist_fit = gauss(bin_centres, *coeff)
#     return coeff, var_matrix, hist_fit

def fit_mixture(data, ncomp=1):
    """
    Fit data using Gaussian mixture model

    Arguments:

    * data: data to be fitted, as a numpy array

    Key-word arguments:

    * ncomp (default value 1): number of components in the mixture model.
    """
    clf = mixture.GMM(n_components=ncomp, covariance_type='full')
    clf.fit(data)
    ml = clf.means_
    wl = clf.weights_
    cl = clf.covars_
    ms = [m[0] for m in ml]
    cs = [np.sqrt(c[0][0]) for c in cl]
    ws = [w for w in wl]
    return ms, cs, ws

        