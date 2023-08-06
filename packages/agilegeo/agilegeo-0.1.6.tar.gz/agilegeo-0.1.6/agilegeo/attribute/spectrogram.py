from numpy import zeros, log2, ceil, arange, absolute, floor, sum
from scipy.fftpack import fft
from scipy.signal import get_window
from agilegeo.util import next_pow2
from numpy import hanning, concatenate

def spectra(data, window_length, dt=1.0, window_type='boxcar',
            overlap=0.5, normalize=False,
            zero_padding=0):
    """
    Calculates a spectrogram using windowed STFTs.
     
    :param data: 1D numpy array to process into spectra.
    :param window_length: The length of the window in seconds if
                          dt is set, otherwise in samples. Will
                          zero pad to the closest power of two.
    :keyword window_type: A string specifying the type of window to
                          use for the STFT. The same input as
                          scipy.signal.get_window
    :keyword dt: The time sample interval of the trace. Defaults to
                 1, which allows window_length to be in seconds.
                   
    :keyword overlap: The fractional overlap for each window.
                      A value of 0 uses no redudant data, a value of 1
                      slides the STFT window one sample at a time.
                      Defaults to 0.5
    :keyword normalize: Normalizes the each spectral slice to have
                        unity energy.
    :keyword zero_padding: The amount of zero padding to when creating
                           the spectra.
                      
    :returns: A spectrogram of the data ([time, freq]).
            ( 2D array for 1D input )
    """

    
    # Make the base window
    window_n = floor( window_length / dt )
    pad = floor( zero_padding / dt )
    window = get_window(window_type, window_n)
    
    # Calculate how many STFTs we need to do.
    stride = window.size * (1 - overlap) + 1
    n_windows = int(ceil((data.size - window.size) / stride) + 1)

    # Pad window to power of 2
    padded_window = zeros(next_pow2(window.size+pad))
    
    # Init the output array
    output = zeros([n_windows, int(padded_window.size)/2])

    norm_factor = 1.0
    
    # Do the loop
    for i in range(int(n_windows)):

        start = int(i * stride)
        end = start + int(window.size)
        
        # Do not compute last samples if we don't have a full window
        if ( end > data.size-1 ): break

        padded_window[0:window.size] = window*data[start:end]
        spect = (2.* absolute(fft(padded_window))/ \
                         window.size)[0:int(padded_window.size /2.)]
                         
        if normalize: output[i, :] = spect / sum(spect**2)
                
        else: output[i, :] = spect
    
    return output



    
        
        
        
        
