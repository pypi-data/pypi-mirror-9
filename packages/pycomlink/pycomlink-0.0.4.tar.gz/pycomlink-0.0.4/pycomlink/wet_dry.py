
        
###############################################################            
# Functions for the wet/dry classification of RSL time series #          
###############################################################
        
#-------------------------------------#        
# Rolling std deviation window method #
#-------------------------------------#
                                                                                                    
def wet_dry_std_dev(rsl, window_length, threshold):
    roll_std_dev = rolling_std_dev(rsl, window_length)
    wet = roll_std_dev > threshold
    return wet, roll_std_dev

def rolling_window(a, window):
    import numpy as np
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def rolling_std_dev(x, window_length, pad_only_left=False):
    import numpy as np
    roll_std_dev = np.std(rolling_window(x, window_length), 1)
    pad_nan = np.zeros(window_length-1)
    pad_nan[:] = np.NaN
    # add NaN to start and end of array
    ix_mid = len(pad_nan)/2
    if pad_only_left == False:
        roll_std_dev = np.concatenate((pad_nan[:ix_mid], 
                                       roll_std_dev,
                                       pad_nan[ix_mid:]))
    elif pad_only_left == True:
        roll_std_dev = np.concatenate((pad_nan, roll_std_dev))
    else:
        ValueError('pad_only_left must be either True or False')
    return roll_std_dev
    

#-----------------------------------------------#
# Rolling Fourie Transform window method (STFT) #
#-----------------------------------------------#

def find_lowest_std_dev_period(rsl, window_length=600):
    import numpy as np
    from matplotlib import mlab
    
    # pad_only_left was added to be backwards compatible with the
    # old rolling_std_dev function which only padded with NaN on the
    # left side of the time series. Now symetric padding is default!!!
    roll_std_dev = rolling_std_dev(rsl,window_length, pad_only_left=True)
    dry_stop = mlab.find(roll_std_dev == np.nanmin(roll_std_dev))
    if len(dry_stop) > 1:
        dry_stop = dry_stop[0]
    dry_start = dry_stop - window_length
    return dry_start, dry_stop
 
def wet_dry_stft(rsl, window_length, threshold, f_divide, 
                 t_dry_start, t_dry_stop, 
                 window=None, Pxx=None, f=None, f_sampling=1/60.0):
    import numpy as np
    #from pylab import specgram
    from matplotlib.mlab import specgram as specg
    
    # Calculate spectrogarm Pxx if it is not supplied as function argument 
    if Pxx is None:
        # Set up sliding window for STFT
        NFFT = window_length
        if window == None:
            window = np.hamming(window_length)        
        # Calculate spectrogram using STFT    
        Pxx, f, t = specg(rsl, 
                          NFFT=NFFT, 
                          Fs=f_sampling, 
                          noverlap=NFFT-1, 
                          window=window)
    elif Pxx is not None and f is not None:
        print 'Skipping spectrogram calculation and using supplied Pxx'
        #
        # TODO: check that Pxx has the correct size
        #
        #..... assert len(Pxx[0]) == len(rsl) - window_length
    elif Pxx is not None and f is None:
        raise ValueError('You have to supply f if you supply Pxx')
    else:
        raise ValueError('This should be imposible')
    
    # Add NaNs as the missing spectral data at the begining and end of 
    # the time series (stemming from the window length) 
    N_diff = len(rsl) - len(Pxx[0])
    N_missing_start = np.floor(N_diff/2.0)
    N_missing_end = N_diff - N_missing_start
    Pxx_extended =  np.concatenate((nans([len(Pxx),N_missing_start]),
                           Pxx,
                           nans([len(Pxx),N_missing_end])),1)
    
    # Calculate mean dry spectrum
    P_dry_mean = np.nanmean(Pxx_extended[:, t_dry_start:t_dry_stop], axis=1)

    # Normalize the power spectrogram with the mean dry spectrum.
    # The arrary([...]) syntax is needed to transpose P_dry_mean to
    # a column vector (1D arrays cannot be transposed in Numpy)
    P_norm = Pxx_extended/ np.array([P_dry_mean]).T
    
    i_f_divide_low = np.where(f<=f_divide)
    i_f_divide_high = np.where(f>f_divide)
    N_f_divide_low = len(i_f_divide_low)
    N_f_divide_high = len(i_f_divide_high)
    
    P_norm_low = np.mean(P_norm[i_f_divide_low],axis=0)
    P_norm_high = np.mean(P_norm[i_f_divide_high],axis=0)
    P_sum_diff = P_norm_low/N_f_divide_low - P_norm_high/N_f_divide_high
    
    wet = P_sum_diff > threshold
    info = {'P_norm': P_norm, 'P_sum_diff': P_sum_diff, 
            'Pxx': Pxx_extended, 'P_dry_mean': P_dry_mean, 'f': f}
    
    return wet, info   


####################
# Helper functions #
####################

def nans(shape, dtype=float):
    import numpy as np
    a = np.empty(shape, dtype)
    a.fill(np.nan)
    return a