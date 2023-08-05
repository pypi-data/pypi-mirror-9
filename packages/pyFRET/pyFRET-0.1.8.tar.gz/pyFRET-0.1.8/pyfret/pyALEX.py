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
    from matplotlib.ticker import NullFormatter
    from sklearn import mixture
except:
    print "Numerical libraries not present in the system"


def _runningMean(x, T):
    """
    Calculate running sum over array x with summation window T.
    Called by APBS and DCBS to calculate number of photons arriving within time window T

    Arguments:
    * x: a numpy array of photon counts
    * T: window length (number of array entries) over which to sum photons
    """
    return np.convolve(x, np.ones((T,)), mode='same')

class ALEX_data:

    """
    This class holds single molecule data.

    It has four attributes, corresponding to the four photon streams from an ALEX experiment. These are numpy arrays:

    * D_D: Donor channel when the donor laser is on
    * D_A: Donor channel when the acceptor laser is on
    * A_D: Acceptor channel when the donor laser is on
    * A_A: Acceptor channel when the acceptor laser is on    

    It can be initialized from four lists or four arrays of photon counts: data = FRET_data(D_D_events, D_A_events, A_D_events, A_A_events)

    """

    def __init__(self, D_D, D_A, A_D, A_A):
        """
        Initialize the ALEX_data object.

        Arguments:

        * D_D: Donor channel when the donor laser is on
        * D_A: Donor channel when the acceptor laser is on
        * A_D: Acceptor channel when the donor laser is on
        * A_A: Acceptor channel when the acceptor laser is on  

        """
        self.D_D = np.array(D_D).astype(float)
        self.D_A = np.array(D_A).astype(float)
        self.A_D = np.array(A_D).astype(float)
        self.A_A = np.array(A_A).astype(float)

    def subtract_bckd(self, bckd_D_D, bckd_D_A, bckd_A_D, bckd_A_A):
        """
        Subtract background noise from the four data channels.

        Arguments:

        * bckd_D_D: average noise per time-bin in the channel D_D
        * bckd_D_A: average noise per time-bin in the channel D_A
        * bckd_A_D: average noise per time-bin in the channel A_D
        * bckd_A_A: average noise per time-bin in the channel A_A
        """
        self.D_D = self.D_D - bckd_D_D
        self.D_A = self.D_A - bckd_D_A
        self.A_D = self.A_D - bckd_A_D
        self.A_A = self.A_A - bckd_A_A
        return self

    def thresholder(self, T_D, T_A):
        """
        Select events that have photons above a threshold.

        Arguments:

        * T_D: threshold for photons during donor laser excitation
        * T_A: threshold for photons during acceptor laser excitation

        An event is above threshold if nA_D + nD_D > T_D AND nA_A > T_A
        for nA_D, nD_D and nA_A photons in the channels A_D, D_D and A_A respectively
        """
        select = ((self.D_D + self.A_D > T_D) & (self.A_A > T_A))
        self.D_D = self.D_D[select]
        self.D_A = self.D_A[select]
        self.A_D = self.A_D[select]
        self.A_A = self.A_A[select]
        return self

    def stoichiometry_selection(self, S, S_min, S_max):
        """
        Select data with photons above a threshold.

        Arguments:

        * S: array of stoichiometry values calculated using the stoichiometry method
        * S_min: minimum accepted value of S (float)
        * S_max: maximum accepted value of S (float)

        Event selection criterion: Smin < Sx < Smax, for Stoichiometry Sx of event x
        """
        select = ((S > S_min) & (S < S_max))
        self.D_D = self.D_D[select]
        self.D_A = self.D_A[select]
        self.A_D = self.A_D[select]
        self.A_A = self.A_A[select]
        S = S[select]
        return S

    def subtract_crosstalk(self, l, d):
        """
        Subtract crosstalk from the FRET channel A_D

        Arguments:

        * l: leakage constant from donor channel D_D to acceptor channel A_D (float between 0 and 1)
        * d: direct excitation of the acceptor by the donor laser (float between 0 and 1)
        """
        lk = l * self.D_D
        dire = d * self.A_A
        self.A_D = self.A_D - (lk + dire)
        return self

    def proximity_ratio(self, gamma=1.0):
        """
        Calculate the proximity ratio (E) and return an array of values.

        Arguments:
        None    

        Keyword arguments:
        gamma (default value 1.0): the instrumental gamma-factor

        Calculation: 
        E = nA / (nA + gamma*nD) 
        for nA and nD photons in the acceptor (A_D) and donor (D_D) channels respectively
        """
        E = self.A_D / (self.D_D + (gamma * self.A_D))
        return E

        
    def stoichiometry(self, gamma=1.0):
        """
        Calculate the stoichiometry (S) and return an array of values.

        Arguments:
        None    

        Keyword arguments:
        gamma (default value 1.0): the instrumental gamma-factor

        Calculation: 
        S = (gamma*D_D + A_D) / (gamma*D_D + A_D + A_A)
        """
        num = gamma*self.D_D + self.A_D
        denom = gamma*self.D_D + self.A_D + self.A_A
        S = num / denom
        return S

    def scatter_hist(self, S_min, S_max, gamma=1.0, save=False, filepath=None, imgname=None, imgtype=None):
        """
        Plot a scatter plot of E (proximity ratio) vs S (stoichiometry) and projections of selected E and S values

        Arguments:

        * S_min: minimum accepted value of S (float between 0 and 1)
        * S_max: maximum accepted value of S (float between 0 and 1)

        Keyword arguments:

        * gamma: Instrumental gamma factor. (float, default value 1.0)
        * save: Boolean. True will save an image of the graph plotted (default False)
        * filepath: file path to the directory in which the image will be saved (default None)
        * imgname: name under which the image will be saved (default None)
        * imgtype: filetype of histogram image. Accepted values: jpg, tiff, rgba, png, ps, svg, eps, pdf
        """
 
        # get rough values (pre thresholding)
        Eraw = self.proximity_ratio(gamma)
        Sraw = self.stoichiometry(gamma)
        x1 = Eraw
        y1 = Sraw

        # select based on threshold
        self.stoichiometry_selection(Sraw, S_min, S_max)

        # recalculate E and S
        Eclean = self.proximity_ratio()
        Sclean = self.stoichiometry()
        x2 = Eclean
        y2 = Sclean

        # prepare plot
        nullfmt   = NullFormatter()         # no labels

        # definitions for the axes
        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.65
        bottom_h = left_h = left+width+0.02

        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom_h, width, 0.2]
        rect_histy = [left_h, bottom, 0.2, height]

        # start with a rectangular Figure
        plt.figure(1, figsize=(8,8))

        axScatter = plt.axes(rect_scatter)
        plt.xlabel("E")
        plt.ylabel("S")
        axHistx = plt.axes(rect_histx)
        plt.ylabel("Frequency")
        axHisty = plt.axes(rect_histy)
        plt.xlabel("Frequency")

        # no labels
        axHistx.xaxis.set_major_formatter(nullfmt)
        axHisty.yaxis.set_major_formatter(nullfmt)

        # the scatter plot:
        axScatter.scatter(x1, y1)
        axScatter.axhline(S_min, c="r", ls="--")
        axScatter.axhline(S_max, c="r", ls="--")

        

        # now determine nice limits by hand:
        binwidth = 0.02
        xymax = np.max( [np.max(np.fabs(x1)), np.max(np.fabs(y1))] )
        lim = ( int(xymax/binwidth) + 1) * binwidth

        axScatter.set_xlim( (-lim, lim) )
        axScatter.set_ylim( (-lim, lim) )
        axScatter.set_xlim( (0.0, 1.0) )
        axScatter.set_ylim( (0.0, 1.0) )

        bins = np.arange(0.0, 1.0 + binwidth, binwidth)
        axHistx.hist(x1, bins=bins)
        axHistx.locator_params(nbins=4)
        axHisty.hist(y1, bins=bins, orientation='horizontal')
        axHisty.locator_params(nbins=4)

        axHistx.set_xlim( axScatter.get_xlim() )
        axHisty.set_ylim( axScatter.get_ylim() ) 
        if save and not imgname == None and not filepath == None and not imgtype == None: 
            picname = ".".join([imgname, imgtype])
            picpath = os.path.join(filepath, picname)  
            plt.savefig(picpath)
        plt.clf()
        plt.cla()
        return self

    def build_histogram(self, filepath, csvname, gamma=1.0, S_min=0.1, S_max=1.0, bin_min=0.0, bin_max=1.0, bin_width=0.02, image = False, imgname = None, imgtype=None, gauss = True, gaussname = None, n_gauss=1):
        """
        Build a proximity ratio histogram and save the frequencies and bin centres as a csv file. 
        Optionally plot and save a graph and perform a simple gaussian fit.

        Arguments:

        * filepath: path to folder where the histogram will be saved (as a string)
        * csvname: the name of the file in which the histogram will be saved (as a string)

        Keyword arguments:

        * gamma: Instrumental gamma factor. (float, default value 1.0)
        * S_min: the miniumum stoichiometric value for which to accept a burst (default 0.1)
        * S_max: the maximum stoichiometric value for which to accept a burst (default 0.9)
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
        S = self.stoichiometry(gamma=0.95)
        select = (S > S_min) & (S < S_max)
        E = E[select]

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

    # burst search
    def APBS(self, T, M, L):
        """
        All-photon bust search algorithm as implemented in Nir et al. J Phys Chem B. 2006 110(44):22103-24.
        Calls _runningMean and _APBS_bursts. 
        Returns an ALEX_bursts object.

        Arguments:
        * T: time-window (in bins) over which to sum photons (integer)
        * M: number of photons in window of length T required to identify a potential burst (integer) 
        * L: total number of photons required for an identified burst to be accepted (integer)

        From Nir et al.:
        The start (respectively, the end) of a potential burst is detected when the number of photons in the averaging window of duration T is larger (respectively, smaller) than the minimum number of photons M.
        A potential burst is retained if the number of photons it contains is larger than a minimum number L.
        """

        data = self.D_D + self.D_A + self.A_D + self.A_A
        means = _runningMean(data, T)
        DD_bursts, DA_bursts, AD_bursts, AA_bursts, b_start, b_end = self._APBS_bursts(data, means, M, L)
        ALEX_bursts_obj = ALEX_bursts(DD_bursts, DA_bursts, AD_bursts, AA_bursts, b_start, b_end)
        return ALEX_bursts_obj


    def _APBS_bursts(self, data, means, M, L):
        """
        Identifies burst that meet the specified APBS threshold criteria.

        Arguments:
        * data: array of photon counts, corresponding to the total number of photons in all four channels
        * means: array of summed photon counts, calculated by _runningMean
        * M: number of photons in window of length T required to identify a potential burst (integer) 
        * L: total number of photons required for an identified burst to be accepted (integer)

        Returns seven arrays:
        * DD_bursts: photons in channel D_D for identified bursts
        * DA_bursts: photons in channel D_A for identified bursts
        * AD_bursts: photons in channel A_D for identified bursts
        * AA_bursts: photons in channel A_A for identified bursts 
        * burst_starts: start times (in bins) for identified bursts
        * burst_ends: end times (in bins) for identified bursts
        """
        assert len(data) == len(means)
        DD_bursts = []
        DA_bursts = []
        AD_bursts = []
        AA_bursts = []
        burst_starts = []
        burst_ends = []
        positions = []
        bursts = []
        burst = 0
        b_DD = 0
        b_DA = 0
        b_AD = 0
        b_AA = 0

        burst_len = 0
        collecting = False

        for pos in range(len(data)):
            if means[pos] >= M:
                collecting = True
                burst_len += 1
                burst += data[pos]
                b_DD += self.D_D[pos]
                b_DA += self.D_A[pos]
                b_AD += self.A_D[pos]
                b_AA += self.A_A[pos]
            else:
                if collecting:
                    bursts.append(burst)
                    DD_bursts.append(b_DD)
                    DA_bursts.append(b_DA)
                    AD_bursts.append(b_AD)
                    AA_bursts.append(b_AA)
                    burst_pos = pos - (float(burst_len) / 2)
                    burst_starts.append(pos - burst_len)
                    burst_ends.append(pos)
                    positions.append(burst_pos)
                burst = 0
                b_DD = 0
                b_DA = 0
                b_AD = 0
                b_AA = 0
                burst_len = 0
                collecting = False

        bursts = np.array(bursts)
        DD_bursts = np.array(DD_bursts)
        DA_bursts = np.array(DA_bursts)
        AD_bursts = np.array(AD_bursts)
        AA_bursts = np.array(AA_bursts)
        burst_starts = np.array(burst_starts)
        burst_ends = np.array(burst_ends)
        positions = np.array(positions)

        select = bursts >= L
        bursts = bursts[select]
        positions = positions[select]
        DD_bursts = DD_bursts[select]
        DA_bursts = DA_bursts[select]
        AD_bursts = AD_bursts[select]
        AA_bursts = AA_bursts[select]
        burst_starts = burst_starts[select]
        burst_ends = burst_ends[select]

        return DD_bursts, DA_bursts, AD_bursts, AA_bursts, burst_starts, burst_ends

    def DCBS(self, T, M, L):
        """
        Dual-channel bust search algorithm as implemented in Nir et al. J Phys Chem B. 2006 110(44):22103-24.
        Returns an ALEX_bursts object.

        Arguments:
        * T: time-window (in bins) over which to sum photons 
        * M: number of photons in window of length T required to identify a potential burst. 
        * L: total number of photons required for an identified burst to be accepted.

        From Nir et al.:
        The start (respectively, the end) of a potential burst is detected when the number of photons in the averaging window of duration T is larger (respectively, smaller) than the minimum number of photons M.
        A potential burst is retained if the number of photons it contains is larger than a minimum number L.
        """

        donor = self.D_D + self.A_D # donor excitation period
        acceptor = self.A_A # acceptor excitation period
        donor_means = _runningMean(donor, T)
        acceptor_means = _runningMean(acceptor, T)
        DD_bursts, DA_bursts, AD_bursts, AA_bursts, b_start, b_end = self._DCBS_bursts(donor_means, acceptor_means, M, L)
        ALEX_bursts_obj = ALEX_bursts(DD_bursts, DA_bursts, AD_bursts, AA_bursts, b_start, b_end)
        return ALEX_bursts_obj

    def _DCBS_bursts(self, donor_means, acceptor_means, M, L):
        """
        Identifies burst that meet the specified DCBS threshold criteria.

        Arguments:
        * donor_means: array of summed photon counts during donor exciation, calculated by _runningMean
        * acceptor_means: array of summed photon counts during acceptor exciation, calculated by _runningMean
        * M: number of photons in window of length T required to identify a potential burst (integer) 
        * L: total number of photons required for an identified burst to be accepted (integer)

        Returns seven arrays:
        * DD_bursts: photons in channel D_D for identified bursts
        * DA_bursts: photons in channel D_A for identified bursts
        * AD_bursts: photons in channel A_D for identified bursts
        * AA_bursts: photons in channel A_A for identified bursts 
        * burst_starts: start times (in bins) for identified bursts
        * burst_ends: end times (in bins) for identified bursts
        """
        assert len(self.D_D) == len(donor_means)
        DD_bursts = []
        DA_bursts = []
        AD_bursts = []
        AA_bursts = []
        burst_starts = []
        burst_ends = []
        positions = []
        b_DD = 0
        b_DA = 0
        b_AD = 0
        b_AA = 0

        burst_len = 0
        collecting = False
        for pos in range(len(self.D_D)):
            # condition depends on both channels
            if (donor_means[pos] >= M) & (acceptor_means[pos] >= M):
                collecting = True
                burst_len += 1
                b_DD += self.D_D[pos]
                b_DA += self.D_A[pos]
                b_AD += self.A_D[pos]
                b_AA += self.A_A[pos]
            else:
                if collecting:
                    DD_bursts.append(b_DD)
                    DA_bursts.append(b_DA)
                    AD_bursts.append(b_AD)
                    AA_bursts.append(b_AA)
                    burst_pos = pos - (float(burst_len) / 2)
                    burst_starts.append(pos - burst_len)
                    burst_ends.append(pos)
                    positions.append(burst_pos)
                b_DD = 0
                b_DA = 0
                b_AD = 0
                b_AA = 0
                burst_len = 0
                collecting = False

        DD_bursts = np.array(DD_bursts)
        DA_bursts = np.array(DA_bursts)
        AD_bursts = np.array(AD_bursts)
        AA_bursts = np.array(AA_bursts)
        burst_starts = np.array(burst_starts)
        burst_ends = np.array(burst_ends)
        positions = np.array(positions)

        select = ((DD_bursts + AD_bursts) >= L) & ((AA_bursts) >= L) 
        positions = positions[select]
        DD_bursts = DD_bursts[select]
        DA_bursts = DA_bursts[select]
        AD_bursts = AD_bursts[select]
        AA_bursts = AA_bursts[select]
        burst_starts = burst_starts[select]
        burst_ends = burst_ends[select]

        return DD_bursts, DA_bursts, AD_bursts, AA_bursts, burst_starts, burst_ends

class ALEX_bursts(ALEX_data):

    """
    This class holds single molecule burst data. Photon bursts are stored in numpy arrays. There is a separate array for each of the four
    photon streams, for the start and end of each burst and for the burst duration.

    The four attributes corresponding to bursts from the four photon streams from an ALEX experiment are numpy arrays:

    * D_D: Donor channel when the donor laser is on
    * D_A: Donor channel when the acceptor laser is on
    * A_D: Acceptor channel when the donor laser is on
    * A_A: Acceptor channel when the acceptor laser is on

    The three further attributes, corresponding to burst duration, burst start time and burst end time are also numpy arrays:

    * burst_len: Length (in bins) of each identified burst
    * burst_starts: Start time (bin number) of each identified burst
    * burst_ends: End time (bn number) of each identified burst
    
    The class can be initialized directly from six lists or arrays: four of photon counts, the burst start times and the burst end times: 
    bursts = ALEX_bursts(D_D_events, D_A_events, A_D_events, A_A_events, burst_starts, burst_ends).
    
    However, it is more typically achieved by running the APBS or DCBS algorithm that forms part of the ALEX_data class.

    """


    def __init__(self, D_D, D_A, A_D, A_A, burst_starts, burst_ends):
        ALEX_data.__init__(self, D_D, D_A, A_D, A_A)
        self.total = self.D_D + self.D_A + self.A_D + self.A_A
        self.burst_starts = np.array(burst_starts)
        self.burst_ends = np.array(burst_ends)
        self.burst_len = self.burst_ends - self.burst_starts

    def denoise_bursts(self, N_DD, N_DA, N_AD, N_AA):
        """
        Subtract background noise from ALEX bursts.

        Arguments:

        * N_DD: average noise per time-bin in the channel D_D
        * N_DA: average noise per time-bin in the channel D_A
        * N_AD: average noise per time-bin in the channel A_D
        * N_AA: average noise per time-bin in the channel A_A
        """
        DD_noise = N_DD * self.burst_len
        DA_noise = N_DA * self.burst_len
        AD_noise = N_AD * self.burst_len
        AA_noise = N_AA * self.burst_len
        acceptor_noise = N_A * self.burst_len

        self.D_D = self.D_D - DD_noise
        self.D_A = self.D_A - DA_noise
        self.A_D = self.A_D - AD_noise
        self.A_A = self.A_A - AA_noise

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



def parse_csv(filepath, filelist, delimiter=","):
    """
    Read data from a list of csv and return a FRET_data object.

    Arguments:

    * filepath: the path to the folder containing the files
    * filelist: list of files to be analysed

    Keyword arguments:

    * delimiter (default ","): the delimiter between values in a row of the csv file.

    This function assumes that each row of your file has the format:
    "D_D,D_A,A_D,A_A" 

    If your data does not have this format (for example if you have separate files for donor and acceptor data), this function will not work well for you.

    """

    D_D = []
    D_A = []
    A_D = []
    A_A = []
    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        with open(current_file) as csv_file:
            current_data = csv.reader(csv_file, delimiter=',')
            for row in current_data:
                D_D.append(float(row[0]))
                D_A.append(float(row[1]))
                A_D.append(float(row[2]))
                A_A.append(float(row[3]))
    ALEX_data_obj = ALEX_data(D_D, D_A, A_D, A_A)
    return ALEX_data_obj


def parse_bin(filepath, filelist, bits=16):
    """
    Read data from a list of binary files and return an ALEX_data object.

    Arguments:
    * filepath: the path to the folder containing the files
    * filelist: list of files to be analysed

    Keyword arguments:
    * bits (default value 16): the number of bits used to store a donor-acceptor pair of time-bins 

    **Note: This file structure is probably specific to the Klenerman group's .dat files.**
        **Please don't use it unless you know you have the same filetype!**
    """
    # note that this makes several assumptions about the file structure
    # which are hard-coded. This is pretty ugly and should be changed
    byte_order = sys.byteorder
    try:
        if byte_order == "little":
            edn = '>ii'
        elif byte_order == "big":
            edn = '<ii'
    except ValueError:
        print "Unknown byte order"
        raise
    D_D = []
    D_A = []
    A_D = []
    A_A = []

    for fp in filelist:
        current_file = os.path.join(filepath, fp)
        counter = 0
        data = []
        with open(current_file, "rb") as f:
            x = f.read(bits)
            while x:
                data.append((struct.unpack(edn, x[:8]), struct.unpack(edn, x[8:])))
                x = f.read(bits)
        for tup in data:
            #print tup
            D_D.append(float(tup[0][0]))
            D_A.append(float(tup[0][1]))
            A_D.append(float(tup[1][0]))
            A_A.append(float(tup[1][1]))
    ALEX_data_obj = ALEX_data(D_D, D_A, A_D, A_A)
    return ALEX_data_obj


# def _fit_gauss(bin_centres, frequencies, p0=[1.0, 0.0, 1.0]):
#     """
#     Fit a histogram with a single gaussian distribution.

#     Arguments:
#     * bin_centres: list of histogram bin centres
#     * frequencies: list of histogram bin frequencies

#     Keyword arguments:
#     * p0: initial values for gaussian fit as a list of floats: [Area, mu, sigma]. (Default: [1.0, 0.0, 1.0])
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

