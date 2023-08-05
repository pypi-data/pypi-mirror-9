import os
import sys
import time
import math
import bisect

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from scipy.optimize import curve_fit
from statsmodels.tsa import stattools

from Base import Base
import lomb


class Amplitude(Base):
    """Half the difference between the maximum and the minimum magnitude"""

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        N = len(magnitude)
        sorted_mag = np.sort(magnitude)
        return (np.median(sorted_mag[-int(0.05 * N):]) -
                np.median(sorted_mag[0:int(0.05 * N)])) / 2.0


class Rcs(Base):
    #Range of cumulative sum
    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        sigma = np.std(magnitude)
        N = len(magnitude)
        m = np.mean(magnitude)
        s = np.cumsum(magnitude - m) * 1.0 / (N * sigma)
        R = np.max(s) - np.min(s)
        return R


class StetsonK(Base):
    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        N = len(magnitude)
        sigmap = (np.sqrt(N * 1.0 / (N - 1)) *
                  (magnitude - np.mean(magnitude)) / np.std(magnitude))

        K = (1 / np.sqrt(N * 1.0) *
             np.sum(np.abs(sigmap)) / np.sqrt(np.sum(sigmap ** 2)))

        return K


class Automean(Base):
    """This is just a prototype, not a real feature"""

    def __init__(self, length = [0,0]):
        self.Data = ['magnitude']
        
        self.length = length[0]
        self.length2 = length[1]

    def fit(self, data):
        magnitude = data[0]        
        return np.mean(magnitude) + self.length + self.length2


class Meanvariance(Base):
    """variability index"""
    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        return np.std(magnitude) / np.mean(magnitude)


class Autocor_length(Base):

    def __init__(self, nlags = 100):
        self.Data = ['magnitude']
        self.nlags = nlags

    def fit(self, data):
        magnitude = data[0]
        AC = stattools.acf(magnitude, self.nlags)
        k = next((index for index, value in
                 enumerate(AC) if value < np.exp(-1)), None)

        return k


class SlottedA_length(Base):

    def __init__(self, T = -99):
        """
        lc: MACHO lightcurve in a pandas DataFrame
        k: lag (default: 1)
        T: tau (slot size in days. default: 4)
        """
        self.Data = ['magnitude','time']
        
        SlottedA_length.SAC = []

        self.T = T

    def slotted_autocorrelation(self, data, time, T, K,
                                second_round=False, K1=100):

        slots = np.zeros((K, 1))
        i = 1

        # make time start from 0
        time = time - np.min(time)

        # subtract mean from mag values
        m = np.mean(data)
        data = data - m

        prod = np.zeros((K, 1))
        pairs = np.subtract.outer(time, time)
        pairs[np.tril_indices_from(pairs)] = 10000000

        ks = np.int64(np.floor(np.abs(pairs) / T + 0.5))

        #We calculate the slotted autocorrelation for k=0 separately
        idx = np.where(ks == 0)
        prod[0] = ((sum(data ** 2) + sum(data[idx[0]] *
                   data[idx[1]])) / (len(idx[0]) + len(data)))
        slots[0] = 0

        #We calculate it for the rest of the ks
        if second_round is False:
            for k in np.arange(1, K):
                idx = np.where(ks == k)
                if len(idx[0]) != 0:
                    prod[k] = sum(data[idx[0]] * data[idx[1]]) / (len(idx[0]))
                    slots[i] = k
                    i = i + 1
                else:
                    prod[k] = np.infty
        else:
            for k in np.arange(K1, K):
                idx = np.where(ks == k)
                if len(idx[0]) != 0:
                    prod[k] = sum(data[idx[0]] * data[idx[1]]) / (len(idx[0]))
                    slots[i - 1] = k
                    i = i + 1
                else:
                    prod[k] = np.infty
            np.trim_zeros(prod, trim='b')

        slots = np.trim_zeros(slots, trim='b')
        return prod / prod[0], np.int64(slots).flatten()

    def fit(self, data):
        magnitude = data[0]
        time = data[1]
        N = len(time)

        if self.T == -99:
            deltaT = time[1:] - time[:-1]
            sorted_deltaT = np.sort(deltaT)
            self.T = sorted_deltaT[int(N * 0.05)+1]


        # T=4
        K = 100
        [SAC, slots] = self.slotted_autocorrelation(magnitude, time, self.T, K1)
        SlottedA_length.SAC = SAC
        SlottedA_length.slots = slots

        SAC2 = SAC[slots]
        k = next((index for index, value in
                 enumerate(SAC2) if value < np.exp(-1)), None)

        while k is None:
            K = K+K
            [SAC, slots] = self.slotted_autocorrelation(magnitude, time, self.T,
                                                    K, second_round=True,
                                                    K1=K/2)
            SAC2 = SAC[slots]
            k = next((index for index, value in
                     enumerate(SAC2) if value < np.exp(-1)), None)

        return slots[k] * self.T

    def getAtt(self):
        return SlottedA_length.SAC, SlottedA_length.slots


class StetsonK_AC(SlottedA_length):

    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        a = StetsonK_AC()
        [autocor_vector, slots] = a.getAtt()

        autocor_vector = autocor_vector[slots]
        N_autocor = len(autocor_vector)
        sigmap = (np.sqrt(N_autocor * 1.0 / (N_autocor - 1)) *
                 (autocor_vector - np.mean(autocor_vector)) /
                  np.std(autocor_vector))

        K = (1 / np.sqrt(N_autocor * 1.0) *
             np.sum(np.abs(sigmap)) / np.sqrt(np.sum(sigmap ** 2)))

        return K


class StetsonL(Base):
    def __init__(self):
        self.Data = ['magnitude','time','magnitude2']

    def fit(self, data):

        aligned_magnitude = data[4]
        aligned_magnitude2 = data[5]

        N = len(aligned_magnitude)

            #sys.exit(1)

        sigmap = (np.sqrt(N * 1.0 / (N - 1)) *
                 (aligned_magnitude[:N] - np.mean(aligned_magnitude)) /
                  np.std(aligned_magnitude))

        sigmaq = (np.sqrt(N * 1.0 / (N - 1)) *
                 (aligned_magnitude2[:N] - np.mean(aligned_magnitude2)) /
                  np.std(aligned_magnitude2))
        sigma_i = sigmap * sigmaq

        J = (1.0 / len(sigma_i) *
             np.sum(np.sign(sigma_i) * np.sqrt(np.abs(sigma_i))))

        K = (1 / np.sqrt(N * 1.0) *
             np.sum(np.abs(sigma_i)) / np.sqrt(np.sum(sigma_i ** 2)))

        return J * K / 0.798


class Con(Base):
    """Index introduced for selection of variable starts from OGLE database.


    To calculate Con, we counted the number of three consecutive measurements
    that are out of 2sigma range, and normalized by N-2
    Pavlos not happy
    """
    def __init__(self, consecutiveStar=3):
        self.Data = ['magnitude']

        self.consecutiveStar = consecutiveStar

    def fit(self, data):

        magnitude = data[0]
        N = len(magnitude)
        if N < self.consecutiveStar:
            return 0
        sigma = np.std(magnitude)
        m = np.mean(magnitude)
        count = 0

        for i in xrange(N - self.consecutiveStar + 1):
            flag = 0
            for j in xrange(self.consecutiveStar):
                if(magnitude[i + j] > m + 2 * sigma or magnitude[i + j] < m - 2 * sigma):
                    flag = 1
                else:
                    flag = 0
                    break
            if flag:
                count = count + 1
        return count * 1.0 / (N - self.consecutiveStar + 1)


# class VariabilityIndex(Base):

#     # Eta. Removed, it is not invariant to time sampling
#     '''
#     The index is the ratio of mean of the square of successive difference to
#     the variance of data points
#     '''
#     def __init__(self):
#         self.category='timeSeries'


#     def fit(self, data):

#         N = len(data)
#         sigma2 = np.var(data)

#         return 1.0/((N-1)*sigma2) * np.sum(np.power(data[1:] - data[:-1] , 2)
    #)


class Color(Base):
    """Average color for each MACHO lightcurve
    mean(B1) - mean(B2)
    """
    def __init__(self):
        self.Data = ['magnitude','time','magnitude2']
        

    def fit(self, data):
        magnitude = data[0]
        magnitude2 = data[3]
        return np.mean(magnitude) - np.mean(magnitude2)


# The categories of the following featurs should be revised

class Beyond1Std(Base):
    """Percentage of points beyond one st. dev. from the weighted
    (by photometric errors) mean
    """

    def __init__(self):
        self.Data = ['magnitude','error']
    

    def fit(self, data):

        magnitude = data[0]
        error = data[2]
        n = len(magnitude)

        weighted_mean = np.average(magnitude, weights=1 / error ** 2)

        # Standard deviation with respect to the weighted mean

        var = sum((magnitude - weighted_mean) ** 2)
        std = np.sqrt((1.0 / (n - 1)) * var)

        count = np.sum(np.logical_or(magnitude > weighted_mean + std,
                                     magnitude < weighted_mean - std))

        return float(count) / n


class SmallKurtosis(Base):
    """Small sample kurtosis of the magnitudes.

    See http://www.xycoon.com/peakedness_small_sample_test_1.htm
    """

    def __init__(self):
        self.category = 'basic'
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        n = len(magnitude)
        mean = np.mean(magnitude)
        std = np.std(magnitude)

        S = sum(((magnitude - mean) / std) ** 4)

        c1 = float(n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
        c2 = float(3 * (n - 1) ** 2) / ((n - 2) * (n - 3))

        return c1 * S - c2


class Std(Base):
    """Standard deviation of the magnitudes"""

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        return np.std(magnitude)


class Skew(Base):
    """Skewness of the magnitudes"""

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        return stats.skew(magnitude)


class StetsonJ(Base):
    """Stetson (1996) variability index, a robust standard deviation"""

    def __init__(self):
        self.Data = ['magnitude','time','magnitude2']

    def fit(self, data):
        aligned_magnitude = data[4]
        aligned_magnitude2 = data[5]
        N = len(aligned_magnitude)

        sigmap = (np.sqrt(N * 1.0 / (N - 1)) *
                 (aligned_magnitude[:N] - np.mean(aligned_magnitude)) /
                  np.std(aligned_magnitude))
        sigmaq = (np.sqrt(N * 1.0 / (N - 1)) *
                 (aligned_magnitude2[:N] - np.mean(aligned_magnitude2)) /
                  np.std(aligned_magnitude2))
        sigma_i = sigmap * sigmaq

        J = (1.0 / len(sigma_i) * np.sum(np.sign(sigma_i) *
             np.sqrt(np.abs(sigma_i))))

        return J


class MaxSlope(Base):
    """
    Examining successive (time-sorted) magnitudes, the maximal first difference
    (value of delta magnitude over delta time)
    """

    def __init__(self):
        self.Data = ['magnitude','time']

    def fit(self, data):

        magnitude = data[0]
        time = data[1]
        slope = np.abs(magnitude[1:] - magnitude[:-1]) / (time[1:] - time[:-1])
        np.max(slope)

        return np.max(slope)


class MedianAbsDev(Base):

    def __init__(self):
        self.category = 'basic'
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        median = np.median(magnitude)

        devs = (abs(magnitude - median))

        return np.median(devs)


class MedianBRP(Base):
    """Median buffer range percentage

    Fraction (<= 1) of photometric points within amplitude/10
    of the median magnitude
    """

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        median = np.median(magnitude)
        amplitude = (np.max(magnitude) - np.min(magnitude)) / 10
        n = len(magnitude)

        count = np.sum(np.logical_and(magnitude < median + amplitude,
                                      magnitude > median - amplitude))

        return float(count) / n


class PairSlopeTrend(Base):
    """
    Considering the last 30 (time-sorted) measurements of source magnitude,
    the fraction of increasing first differences minus the fraction of
    decreasing first differences.
    """

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        data_last = magnitude[-30:]

        return (float(len(np.where(np.diff(data_last) > 0)[0]) -
                len(np.where(np.diff(data_last) <= 0)[0])) / 30)


class FluxPercentileRatioMid20(Base):

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        sorted_data = np.sort(magnitude)
        lc_length = len(sorted_data)

        F_60_index = int(0.60 * lc_length)
        F_40_index = int(0.40 * lc_length)
        F_5_index = int(0.05 * lc_length)
        F_95_index = int(0.95 * lc_length)

        F_40_60 = sorted_data[F_60_index] - sorted_data[F_40_index]
        F_5_95 = sorted_data[F_95_index] - sorted_data[F_5_index]
        F_mid20 = F_40_60 / F_5_95

        return F_mid20


class FluxPercentileRatioMid35(Base):

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        sorted_data = np.sort(magnitude)
        lc_length = len(sorted_data)

        F_325_index = int(0.325 * lc_length)
        F_675_index = int(0.675 * lc_length)
        F_5_index = int(0.05 * lc_length)
        F_95_index = int(0.95 * lc_length)

        F_325_675 = sorted_data[F_675_index] - sorted_data[F_325_index]
        F_5_95 = sorted_data[F_95_index] - sorted_data[F_5_index]
        F_mid35 = F_325_675 / F_5_95

        return F_mid35


class FluxPercentileRatioMid50(Base):

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        sorted_data = np.sort(magnitude)
        lc_length = len(sorted_data)

        F_25_index = int(0.25 * lc_length)
        F_75_index = int(0.75 * lc_length)
        F_5_index = int(0.05 * lc_length)
        F_95_index = int(0.95 * lc_length)

        F_25_75 = sorted_data[F_75_index] - sorted_data[F_25_index]
        F_5_95 = sorted_data[F_95_index] - sorted_data[F_5_index]
        F_mid50 = F_25_75 / F_5_95

        return F_mid50


class FluxPercentileRatioMid65(Base):

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        sorted_data = np.sort(magnitude)
        lc_length = len(sorted_data)

        F_175_index = int(0.175 * lc_length)
        F_825_index = int(0.825 * lc_length)
        F_5_index = int(0.05 * lc_length)
        F_95_index = int(0.95 * lc_length)

        F_175_825 = sorted_data[F_825_index] - sorted_data[F_175_index]
        F_5_95 = sorted_data[F_95_index] - sorted_data[F_5_index]
        F_mid65 = F_175_825 / F_5_95

        return F_mid65


class FluxPercentileRatioMid80(Base):

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        sorted_data = np.sort(magnitude)
        lc_length = len(sorted_data)

        F_10_index = int(0.10 * lc_length)
        F_90_index = int(0.90 * lc_length)
        F_5_index = int(0.05 * lc_length)
        F_95_index = int(0.95 * lc_length)

        F_10_90 = sorted_data[F_90_index] - sorted_data[F_10_index]
        F_5_95 = sorted_data[F_95_index] - sorted_data[F_5_index]
        F_mid80 = F_10_90 / F_5_95

        return F_mid80


class PercentDifferenceFluxPercentile(Base):

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        median_data = np.median(magnitude)

        sorted_data = np.sort(magnitude)
        lc_length = len(sorted_data)
        F_5_index = int(0.05 * lc_length)
        F_95_index = int(0.95 * lc_length)
        F_5_95 = sorted_data[F_95_index] - sorted_data[F_5_index]

        percent_difference = F_5_95 / median_data

        return percent_difference


class PercentAmplitude(Base):

    def __init__(self):
        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        median_data = np.median(magnitude)
        distance_median = np.abs(magnitude - median_data)
        max_distance = np.max(distance_median)

        percent_amplitude = max_distance / median_data

        return percent_amplitude


class LinearTrend(Base):

    def __init__(self):
        self.Data = ['magnitude','time']

    def fit(self, data):
        magnitude = data[0]
        time = data[1]
        regression_slope = stats.linregress(time, magnitude)[0]

        return regression_slope


class Eta_color(Base):

    def __init__(self):

        self.Data = ['magnitude','time','magnitude2']

    def fit(self, data):
        aligned_magnitude = data[4]
        aligned_magnitude2 = data[5]
        aligned_time = data[6]
        N = len(aligned_magnitude)
        B_Rdata = aligned_magnitude - aligned_magnitude2
        # # N = len(B_Rdata)
        # sigma2 = np.var(B_Rdata)

        # return 1.0/((N-1)*sigma2) * np.sum(np.power(B_Rdata[1:] -
            #B_Rdata[:-1] , 2))

        w = 1.0 / np.power(aligned_time[1:] - aligned_time[:-1], 2)
        w_mean = np.mean(w)

        N = len(aligned_time)
        sigma2 = np.var(B_Rdata)

        S1 = sum(w * (B_Rdata[1:] - B_Rdata[:-1]) ** 2)
        S2 = sum(w)

        eta_B_R = (w_mean * np.power(aligned_time[N - 1] -
                   aligned_time[0], 2) * S1 / (sigma2 * S2 * N ** 2))

        return eta_B_R


class Eta_e(Base):

    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):

        magnitude = data[0]
        time = data[1]
        w = 1.0 / np.power(time[1:] - time[:-1], 2)
        w_mean = np.mean(w)

        N = len(time)
        sigma2 = np.var(magnitude)

        S1 = sum(w * (magnitude[1:] - magnitude[:-1]) ** 2)
        S2 = sum(w)

        eta_e = (w_mean * np.power(time[N - 1] -
                 time[0], 2) * S1 / (sigma2 * S2 * N ** 2))

        return eta_e


class Mean(Base):

    def __init__(self):

        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        B_mean = np.mean(magnitude)

        return B_mean


class Q31(Base):

    def __init__(self):

        self.Data = ['magnitude']

    def fit(self, data):
        magnitude = data[0]
        return np.percentile(magnitude, 75) - np.percentile(magnitude, 25)


class Q31_color(Base):

    def __init__(self):

        self.Data = ['magnitude','time','magnitude2']

    def fit(self, data):
        aligned_magnitude = data[4]
        aligned_magnitude2 = data[5]
        N = len(aligned_magnitude)
        b_r = aligned_magnitude[:N] - aligned_magnitude2[:N]

        return np.percentile(b_r, 75) - np.percentile(b_r, 25)


class AndersonDarling(Base):

    def __init__(self):

        self.Data = ['magnitude']

    def fit(self, data):

        magnitude = data[0]
        ander = stats.anderson(magnitude)[0]
        #return ander
        return 1 / (1.0 + np.exp(-10 * (ander - 0.3)))


class PeriodLS(Base):

    def __init__(self, ofac = 6.):

        self.Data = ['magnitude','time']
        self.ofac = ofac;

    def fit(self, data):

        magnitude = data[0]
        time = data[1]

        global new_time
        global prob
        global period

        fx, fy, nout, jmax, prob = lomb.fasper(time, magnitude, self.ofac, 100.)
        period = fx[jmax]
        T = 1.0 / period
        new_time = np.mod(time, 2 * T) / (2 * T)

        return T


class Period_fit(Base):

    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):

        try:
            return prob
        except:    
            print "error: please run PeriodLS first to generate values for Period_fit"


class Psi_CS(Base):

    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        
        try:
            magnitude = data[0]
            time = data[1]
            folded_data = magnitude[np.argsort(new_time)]

            sigma = np.std(folded_data)
            N = len(folded_data)
            m = np.mean(folded_data)
            s = np.cumsum(folded_data - m) * 1.0 / (N * sigma)
            R = np.max(s) - np.min(s)

            return R
        except:
            print "error: please run PeriodLS first to generate values for Psi_CS"


class Psi_eta(Base):

    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):

        # folded_time = np.sort(new_time)
        try:
            magnitude = data[0]
            folded_data = magnitude[np.argsort(new_time)]

            # w = 1.0 / np.power(folded_time[1:]-folded_time[:-1] ,2)
            # w_mean = np.mean(w)

            # N = len(folded_time)
            # sigma2=np.var(folded_data)

            # S1 = sum(w*(folded_data[1:]-folded_data[:-1])**2)
            # S2 = sum(w)

            # Psi_eta = w_mean * np.power(folded_time[N-1]-folded_time[0],2) * S1 /
            # (sigma2 * S2 * N**2)

            N = len(folded_data)
            sigma2 = np.var(folded_data)

            Psi_eta = (1.0 / ((N - 1) * sigma2) *
                       np.sum(np.power(folded_data[1:] - folded_data[:-1], 2)))

            return Psi_eta
        except:
            print "error: please run PeriodLS first to generate values for Psi_eta"


class CAR_sigma(Base):

    def __init__(self):

        self.Data = ['magnitude','time','error']

    def CAR_Lik(self, parameters, t, x, error_vars):

        sigma = parameters[0]
        tau = parameters[1]
       #b = parameters[1] #comment it to do 2 pars estimation
       #tau = params(1,1);
       #sigma = sqrt(2*var(x)/tau);

        b = np.mean(x) / tau
        epsilon = 1e-300
        cte_neg = -np.infty
        num_datos = np.size(x)

        Omega = []
        x_hat = []
        a = []
        x_ast = []

        # Omega = np.zeros((num_datos,1))
        # x_hat = np.zeros((num_datos,1))
        # a = np.zeros((num_datos,1))
        # x_ast = np.zeros((num_datos,1))

        # Omega[0]=(tau*(sigma**2))/2.
        # x_hat[0]=0.
        # a[0]=0.
        # x_ast[0]=x[0] - b*tau

        Omega.append((tau * (sigma ** 2)) / 2.)
        x_hat.append(0.)
        a.append(0.)
        x_ast.append(x[0] - b * tau)

        loglik = 0.

        for i in range(1, num_datos):

            a_new = np.exp(-(t[i] - t[i - 1]) / tau)
            x_ast.append(x[i] - b * tau)
            x_hat.append(
                a_new * x_hat[i - 1] +
                (a_new * Omega[i - 1] / (Omega[i - 1] + error_vars[i - 1])) *
                (x_ast[i - 1] - x_hat[i - 1]))

            Omega.append(
                Omega[0] * (1 - (a_new ** 2)) + ((a_new ** 2)) * Omega[i - 1] *
                (1 - (Omega[i - 1] / (Omega[i - 1] + error_vars[i - 1]))))

            # x_ast[i]=x[i] - b*tau
            # x_hat[i]=a_new*x_hat[i-1] + (a_new*Omega[i-1]/(Omega[i-1] +
                #error_vars[i-1]))*(x_ast[i-1]-x_hat[i-1])
            # Omega[i]=Omega[0]*(1-(a_new**2)) + ((a_new**2))*Omega[i-1]*
            #( 1 - (Omega[i-1]/(Omega[i-1]+ error_vars[i-1])))

            loglik_inter = np.log(
                ((2 * np.pi * (Omega[i] + error_vars[i])) ** -0.5) *
                (np.exp(-0.5 * (((x_hat[i] - x_ast[i]) ** 2) /
                 (Omega[i] + error_vars[i]))) + epsilon))

            loglik = loglik + loglik_inter

            if(loglik <= cte_neg):
                print('CAR lik se fue a inf')
                return None

        # the minus one is to perfor maximization using the minimize function
        return -loglik

    def calculateCAR(self, time, data, error):

        x0 = [10, 0.5]
        bnds = ((0, 100), (0, 100))
        # res = minimize(self.CAR_Lik, x0, args=(LC[:,0],LC[:,1],LC[:,2]) ,
            #method='nelder-mead',bounds = bnds)

        res = minimize(self.CAR_Lik, x0, args=(time, data, error),
                       method='nelder-mead', bounds=bnds)
        # options={'disp': True}
        sigma = res.x[0]
        global tau
        tau = res.x[1]
        return sigma

    # def getAtt(self):
    #     return CAR_sigma.tau

    def fit(self, data):
        # LC = np.hstack((self.time , data.reshape((self.N,1)), self.error))

        N = len(data[0])
        magnitude = data[0].reshape((N, 1))
        time = data[1].reshape((N, 1)) 
        error = data[2].reshape((N, 1)) ** 2
       
        a = self.calculateCAR(time, magnitude, error)

        return a


class CAR_tau(Base):

    def __init__(self):

        self.Data = ['magnitude','time','error']

    def fit(self, data):

        try:
            return tau
        except:
            print "error: please run CAR_sigma first to generate values for CAR_tau"


class CAR_tmean(Base):

    def __init__(self):

        self.Data = ['magnitude','time','error']

    def fit(self, data):
        
        magnitude = data[0]

        try:
            return np.mean(magnitude) / tau
        except:
            print "error: please run CAR_sigma first to generate values for CAR_tmean"
            
class Freq1_harmonics_amplitude_0(Base):
    def __init__(self):
        self.Data = ['magnitude','time']

    def fit(self, data):
        magnitude = data[0]
        time = data[1]

        time = time - np.min(time)

        global A
        global PH
        global scaledPH
        A = []
        PH = []
        scaledPH = []
        
        def model(x, a, b, c, Freq):
             return a*np.sin(2*np.pi*Freq*x)+b*np.cos(2*np.pi*Freq*x)+c
        
        try:   
            for i in range(3):
                
                # fundamental_Freq = period

                wk1, wk2, nout, jmax, prob = lomb.fasper(time, magnitude, 6., 100.)
    
                fundamental_Freq = wk1[jmax]
                
                # fit to a_i sin(2pi f_i t) + b_i cos(2 pi f_i t) + b_i,o
                
                # a, b are the parameters we care about
                # c is a constant offset
                # f is the fundamental Frequency
                def yfunc(Freq):
                    def func(x, a, b, c):
                        return a*np.sin(2*np.pi*Freq*x)+b*np.cos(2*np.pi*Freq*x)+c
                    return func
                
                Atemp = []
                PHtemp = []
                popts = []
                
                for j in range(4):
                    popt, pcov = curve_fit(yfunc((j+1)*fundamental_Freq), time, magnitude)
                    Atemp.append(np.sqrt(popt[0]**2+popt[1]**2))
                    PHtemp.append(np.arctan(popt[1] / popt[0]))
                    popts.append(popt)
                
                A.append(Atemp)
                PH.append(PHtemp)
                
                for j in range(4):
                    magnitude = np.array(magnitude) - model(time, popts[j][0], popts[j][1], popts[j][2], (j+1)*fundamental_Freq)
            
            for ph in PH:
                scaledPH.append(np.array(ph) - ph[0])

            return A[0][0]
        except:
            print "error: please run PeriodLS first to generate values for all harmonics"



class Freq1_harmonics_amplitude_1(Base):
    def __init__(self):
        
        self.Data = ['magnitude','time']

    def fit(self, data):

        try:
            return A[0][1]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq1_harmonics_amplitude_2(Base):
    def __init__(self):
        
        self.Data = ['magnitude','time']

    def fit(self, data):

        try:
            return A[0][2]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq1_harmonics_amplitude_3(Base):
    def __init__(self):
        
        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[0][3]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_amplitude_0(Base):
    def __init__(self):
        
        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[1][0]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_amplitude_1(Base):
    def __init__(self):
         
         self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[1][1]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_amplitude_2(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[1][2]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_amplitude_3(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[1][3]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_amplitude_0(Base):
    def __init__(self):
        
        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[2][0]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_amplitude_1(Base):
    def __init__(self):
        
        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[2][1]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_amplitude_2(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[2][2]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_amplitude_3(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return A[2][3]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq1_harmonics_rel_phase_0(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[0][0]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq1_harmonics_rel_phase_1(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[0][1]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq1_harmonics_rel_phase_2(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[0][2]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq1_harmonics_rel_phase_3(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[0][3]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_rel_phase_0(Base):
    def __init__(self):
        self.category = 'timeSeries'

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[1][0]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_rel_phase_1(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[1][1]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_rel_phase_2(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[1][2]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq2_harmonics_rel_phase_3(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[1][3]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_rel_phase_0(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[2][0]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_rel_phase_1(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[2][1]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_rel_phase_2(Base):
    def __init__(self):

        self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[2][2]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"

class Freq3_harmonics_rel_phase_3(Base):
    def __init__(self):
 
         self.Data = ['magnitude','time']

    def fit(self, data):
        try:
            return scaledPH[2][3]
        except:
            print "error: please run Freq1_harmonics_amplitude_0 first to generate values for all harmonics"