import re
import numpy as np
import pandas as pd
import uproot
from scipy.signal import convolve
from matplotlib import pyplot as plt

from helper import *


# ----------------------------------
# digitizer data
# ----------------------------------
class digitizer:
    # ---------- init ----------
    def __init__(self, fileName, **kwargs):
        '''
        ---------- calculate waveforms ----------

        NOTE: calculates the signal waveforms of a set of channels for a set of events from the digitizer

        INPUT: run number
               OPTIONS:
               - list_of_events (default: [-1] (== all))
               - list_of_channels (default: [-1] (== all))
               - cf_threshold in [0...1] (default: 0.1)
               - cf_cutoff in [mV] (default: 20)
               - signal_filter ('raw', 'converted'(default), 'lowpass', 'moving-average')
               - lowpass_limit in [Hz] (default: 30e6)
               - lowpass_order (default: 3)
               - average_window (default: 10)

        RETURN: pandas dataframe 
                - list of events
                - list of channels
                - timestamp of events
                - signal time      [ns]    (shape: events, channels, wave values)
                - signal           [mV]    (shape: events, channels, wave values)
                - signal amplitude [mV]    (shape: events, channels)
                - signal integral  [mV*µs] (shape: events, channels)
                - signal cft       [ns]    (shape: events, channels)
                - signal tot       [ns]    (shape: events, channels)
                - signal intensity [mV*µs] (shape: events, channels) (= tot [µs] * amplitude [mV] when amplitude within 50-150 ns)
        '''
        
        self.file_name = fileName
        self.__kwargs = kwargs
        
        self.adc_conversion = 1.1 * 1000 / 2**12 # ADC count to voltage conversion in [mV/ADC count] | +10% from charge injection

        self.__calculate_waveforms()
        
    # ---------- calculate straw waveforms ----------
    def __calculate_waveforms(self):
        ### open file
        with uproot.open(self.file_name) as f:
            tree = f['data']

            # selected events in this run
            list_of_events = self.__kwargs.get('events', None)
            if list_of_events is None:
                list_of_events = np.arange(tree.num_entries)
            elif not isinstance(list_of_events, np.ndarray):
                list_of_events = np.asarray(list_of_events) if isinstance(list_of_events, (list, tuple, range)) else np.asarray([list_of_events])
            
            self.events = list_of_events    
            nEvts = len(list_of_events)

            # selected channels in this run
            list_of_channels = self.__kwargs.get('channels', None)
            if list_of_channels is None:
                list_of_channels = np.asarray([int(re.search(r'ch(\d+)_data', x).group(1)) for x in list(tree.keys()) if re.fullmatch(r'ch\d+_data', x)])
            elif not isinstance(list_of_channels, np.ndarray):
                list_of_channels = np.asarray(list_of_channels) if isinstance(list_of_channels, (list, tuple, range)) else np.asarray([list_of_channels])
            
            self.channels = list_of_channels
            nChannels = len(list_of_channels)

            # get branches
            branches = tree.arrays([f'ch{i}_data' for i in list_of_channels]+['time', 'xinc', 'timestamp'], library='np')#'TR0_0_data', 
            
            # waveform time per sample in [ns]
            self.sample_size = (branches['xinc'][0] / 1e-9)
            
            # waveform length in [ns]
            wave_time = self.sample_size * np.arange(len(branches[list(branches.keys())[0]][0]))[:-100]
            
            # timestamp per event [ns]
            time_stamp = branches['timestamp'][list_of_events]

            # conversion settings
            adc_conv = self.adc_conversion # ADC count to voltage conversion in [mV/ADC count]
            cf_thres = self.__kwargs.get('cf_threshold', 0.1) # percentage of amplitude for constant fraction timing and tot
            cf_cutoff = self.__kwargs.get('cf_cutoff', 20) # minimum signal used for tot threshold in [mV]
            if self.__kwargs.get('signal_filter', 'converted') == 'raw':
                cf_cutoff = self.__kwargs.get('cf_cutoff', 20/adc_conv)
            
            # init data arrays
            wave = np.zeros((nEvts, nChannels, len(wave_time))) # waveform in [mV]
            wave_ampl = np.zeros((nEvts, nChannels)) # amplitude in [mV]
            wave_ampl_time = np.zeros((nEvts, nChannels)) # amplitude time in [ns]
            wave_int = np.zeros_like(wave_ampl) # integral in [mV us]
            wave_tot_raw = np.zeros((nEvts, nChannels, 2)) # time above and below signal threshold in [ns]
            wave_tot = np.zeros_like(wave_ampl) # waveform time over threshold in [ns]
            wave_cft = np.zeros_like(wave_ampl) # waveform timing in [ns]
            
            trig_raw = np.zeros((nEvts, len(wave_time))) # trigger pulse in [ADC counts]
            trig_time = np.zeros_like(wave_ampl) # trigger timing in [ns]

            # fill data arrays
            for ich, ch in enumerate(list_of_channels):
                # waveforms per event of a channel ch in [ADC bins]
                wave_raw = np.stack(branches[f'ch{ch}_data'])[list_of_events, :]
                
                if self.__kwargs.get('signal_filter', 'converted') == 'raw':
                    wave_filtered = wave_raw[:,:-100]

                elif self.__kwargs.get('signal_filter', 'converted') == 'converted':
                    wave_filtered = adc_conv * wave_raw[:,:-100]
                    
                    # baseline substracted
                    wave_filtered -= np.mean(wave_filtered[:,:50], axis=1)[:,np.newaxis] # mV
                    
                elif self.__kwargs.get('signal_filter', 'converted') == 'lowpass':
                    wave_filtered = adc_conv * helper().lowpass(wave_time,
                                                                    wave_raw[:,:-100],
                                                                    lowpass_limit=self.__kwargs.get('lowpass_limit', 30e6), # cut off frequency in [Hz]
                                                                    lowpass_order=self.__kwargs.get('lowpass_order', 3) # butterworth order
                                                                   )
                    # baseline substracted
                    wave_filtered -= np.mean(wave_filtered[:,:50], axis=1)[:,np.newaxis] # mV

                elif self.__kwargs.get('signal_filter', 'converted') == 'moving-average':
                    wave_filtered = adc_conv * helper().moving_average(wave_raw[:,:-100],
                                                                           window_size=self.__kwargs.get('average_window', 10) # size of moving average window
                                                                          )
                    
                    # baseline substracted
                    wave_filtered -= np.mean(wave_filtered[:,:50], axis=1)[:,np.newaxis] # mV
                    
                # signal wave
                wave[:,ich,:] = wave_filtered
                
                # signal amplitude
                wave_ampl[:,ich] = np.max(wave[:,ich,:], axis=1) # mV
                wave_ampl_time[:,ich] = self.sample_size * np.argmax(wave[:,ich,:], axis=1) # ns
                
                # signal integral
                wave_int[:,ich] = np.sum(wave[:,ich,:] * self.sample_size, axis=1)/1000 # mV µs

                # signal tot
                wave_tot_raw[:,ich,:] = np.array([wave_time[np.where(wave > thres)[0][[0,-1]]] 
                                                  if np.any(wave > thres) 
                                                  else 0 for wave, thres in zip(wave[:,ich,:], cf_thres*wave_ampl[:,ich])
                                                 ]) # ns

                # trigger wave
                #trig_raw = np.stack(branches['TR0_0_data'])[list_of_events, :-100]
                #if self.__kwargs.get('signal_filter', 'converted') == 'converted':
                #    trig_raw = 2 * adc_conv * trig_raw
                #    trig_raw -= np.mean(trig_raw[:,:50], axis=1)[:,np.newaxis]
                
                # triger time
                #trig_time[:,ich] = self.sample_size * np.argmax((-0.5 * np.gradient(trig_raw, axis=1)), axis=1) # ns

        wave_tot = wave_tot_raw[:,:,1] - wave_tot_raw[:,:,0]
        wave_cft = wave_tot_raw[:,:,0]
        
        wave_intensity = wave_int * wave_tot/1000 # mV*µs * µs
        
        data = dict() #pd.DataFrame()
        
        data['timestamp'] = time_stamp
        data['waveTime'] = np.broadcast_to(wave_time, wave.shape)
        data['wave'] = wave
        data['amplitude'] = wave_ampl
        data['amplitudeTime'] = wave_ampl_time
        data['integral'] = wave_int
        data['tot'] = wave_tot
        data['cft'] = wave_cft
        data['intensity'] = wave_intensity
        #data['trigger'] = trig_raw
        #data['triggerTime'] = trig_time

        self.waveforms = data
        
        return 0
        