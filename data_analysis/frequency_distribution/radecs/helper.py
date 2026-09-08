import numpy as np
from scipy.stats import moyal
from scipy.optimize import curve_fit
from scipy.ndimage import uniform_filter1d, shift


#----------------------------------
# helper functions
#----------------------------------
class helper:
    #---------- linear function ----------
    def function_linear(self, x, a, b):
        '''
        ---------- linear function ----------

        INPUT: x, a, b

        RETURN: function values
        '''
        return a*x + b

    #---------- parabola function ----------
    def function_parabola(self, x, a, mu, c):
        '''
        ---------- parabola function ----------

        INPUT: x, a, mu, c

        RETURN: function values
        '''
        return a * (x-mu)**2 + c

    #---------- Gaussian function ----------
    def function_gaussian(self, x, a, mu, sigma, c=0):
        '''
        ---------- Gaussian function ----------

        INPUT: x, a, mu, sigma, c=0

        RETURN: function values
        '''
        return a * np.exp(-(x-mu)**2 / (2*sigma**2)) + c

    #---------- Gaussian function (normalized) ----------
    def function_gaussian_norm(self, x, mu, sigma, c=0):
        '''
        ---------- Gaussian function (normalized) ----------

        INPUT: x, mu, sigma, c=0

        RETURN: function values
        '''
        return 1/np.sqrt(2*np.pi*sigma**2) * np.exp(-(x-mu)**2 / (2*sigma**2)) + c
    
    #---------- moyal function ----------
    def function_moyal(self, x, A, loc, scale, c=0):
        '''
        ---------- moyal function ----------

        NOTE: for waveform shapes (ref. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.moyal.html)

        INPUT: x, A, peak position, scale, c=0

        RETURN: function values
        '''
        try:
            func = np.asarray([moyal(loc[i],scale).pdf(x) for i in range(len(loc))])
            return A[:,np.newaxis] * func/np.max(func) + c
        except:
            func = moyal(loc,scale).pdf(x)
            return A * func/np.max(func) + c
     
    #---------- butterworth function ----------
    def function_butterworth(self, frequencies, freq_cut, order=1, amplitude=1):
        '''
        ---------- butterworth function ----------

        NOTE: higher-order low-pass filter function (ref. https://www.changpuak.ch/electronics/downloads/On_the_Theory_of_Filter_Amplifiers.pdf)

        INPUT: frequencies, cutoff frequency, order=1, amplitude=1

        RETURN: function values
        '''
        return amplitude / np.sqrt(1+(frequencies/freq_cut)**(2*order))

    #---------- Gaussian fit ----------
    def fit_gaussian(self, x, y, ye, params):
        '''
        ---------- Gaussian fit ----------

        INPUT: x values, y values, y errors, start parameters

        RETURN: popt, perr (from scipy.optimize.curve_fit)
        '''
        popt, pcov = curve_fit(self.function_gaussian, x, y, sigma=ye, absolute_sigma=True, p0=params)
        perr = np.diag(pcov)
        
        return popt, perr
    
    #---------- Real Input FFT function ----------
    def FFT(self, sig_time, sig_value):
        '''
        ---------- Real Input FFT function ----------

        INPUT: signal time, signal values

        RETURN: frequency, intensitiy
        '''
        frequency = np.fft.rfftfreq(len(sig_time), 1e-9*(sig_time[1]-sig_time[0]))
        intensity = np.fft.rfft(sig_value)
        return frequency, intensity
        
    #---------- low-pass-filter ----------
    def lowpass(self, sig_time, sig_value, lowpass_limit=30e6, lowpass_order=3):
        '''
        ---------- low-pass-filter ----------

        INPUT: sig_time, sig_value, lowpass_limit=30e6, lowpass_order=3

        RETURN: filtered sig_value
        '''
        if lowpass_limit == True:
            lowpass_limit = 30e6
        if lowpass_limit != False:
            # FFT
            time_fft, sig_fft = self.FFT(sig_time, sig_value)
            # butterworth filtering
            sig_fft_filter = sig_fft * self.function_butterworth(time_fft, lowpass_limit, lowpass_order)

            # backtransformation
            return np.fft.irfft(sig_fft_filter)

        else:
            return sig_value

    #---------- moving average function ----------
    def moving_average(self, sig_value, window_size=3):
        '''
        ---------- moving average function ----------

        INPUT: sig_value, window_size=3

        RETURN: filtered sig_value
        '''
        if window_size > 1:
            return uniform_filter1d(sig_value, size=window_size, axis=1, mode='nearest')
        
        else:
            return sig_value

    #---------- circular shift ----------
    def circular_shift(self, arr, shift_value):
        '''
        ---------- circular shift ----------
        
        NOTE: a set of floats 'arr' (i.e. shape=(924)) will be shifted by a set of values in an array 'shift_value' (i.e. shape=(45,32))
        It is used to shift digitizer signal times (shape=(samples)) by the measured trigger timings (shape=(events,channels)) and returns times (shape=(events,channels,samples) like the signal itself)
        
        INPUT: 1dim-array, 2-dim array

        RETURN: shifted values (3-dim array)
        '''
        return shift(arr, shift_value, mode='wrap', order=1)

    #---------- pandas dataframe to numpy ndarray ----------
    def pd_to_np(self, pd_entry):
        '''

        NOTE:converts a pandas dataframe to a numpy ndarray

        INPUT: pandas dataframe

        RETURN: numpy ndarray
        '''
        return np.vstack(pd_entry.to_numpy())
    
    #---------- prints h5 file structure ----------
    def print_h5(path, group='/', sep='\t'):
        '''
        
        NOTE: print HDF5 file metadata
        Iterate through groups in a HDF5 file and prints the groups and datasets names and datasets attributes
        group: you can give a specific group, defaults to the root group
        
        INPUT: path, (group, seperator)
        
        RETURN: print out
        '''
        with h5py.File(path,'r') as f:
            #descend_obj(f[group])
            obj=f[group]
            if type(obj) in [h5py._hl.group.Group,h5py._hl.files.File]:
                for key in obj.keys():
                    print(sep,'-',key,':',obj[key])
                    descend_obj(obj[key],sep=sep+'\t')
            elif type(obj)==h5py._hl.dataset.Dataset:
                for key in obj.attrs.keys():
                    print(sep+'\t','-',key,':',obj.attrs[key])
                
    #---------- prints shape of np.ndarray bc i'm lazy ----------
    def fshape(self, x):
        '''
        ---------- prints shape of np.ndarray bc i'm lazy ----------
        '''
        print(np.shape(x))