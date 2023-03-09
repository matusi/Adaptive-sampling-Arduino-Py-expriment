
import queue
import numpy as np

class FreqAnalyzer:
    def __init__(self, sampling_rate):
        self.sampling_rate = sampling_rate
        self._q = queue.Queue()

    def get_max_freqs(self, signal, window_size, freq_range=None):
        num_samples = len(signal)
        num_windows = int(np.ceil(num_samples / window_size))

        # Calculate timestamps for each window
        timestamps = np.arange(num_windows) * window_size / self.sampling_rate

        # Loop over all windows
        max_freqs = []
        for i in range(num_windows):
            # Extract current window from signal
            start = i * window_size
            end = min(start + window_size, num_samples)
            window_signal = signal[start:end]

            # Compute FFT of windowed signal
            window_spectrum = np.fft.rfft(window_signal)

            # Find frequency with maximum amplitude in specified range
            if freq_range is not None:
                lo_freq, hi_freq = freq_range
                lo_bin, hi_bin = int(lo_freq * window_size / self.sampling_rate), int(hi_freq * window_size / self.sampling_rate)
                freq_bins = np.arange(lo_bin, hi_bin)
            else:
                freq_bins = np.arange(len(window_spectrum))
            max_freq_bin = np.argmax(np.abs(window_spectrum[freq_bins])) + freq_bins[0]

            # Convert frequency bin to frequency in Hz
            max_freq = max_freq_bin * self.sampling_rate / window_size

            # Append result to list
            max_freqs.append(max_freq)

        return timestamps, max_freqs, window_spectrum
    def get_rms(self, signal, window_size):
        num_samples = len(signal)
        num_windows = int(np.ceil(num_samples / window_size))

        # Calculate timestamps for each window
        timestamps = np.arange(num_windows) * window_size / self.sampling_rate

        # Loop over all windows
        rms_values = []
        for i in range(num_windows):
            # Extract current window from signal
            start = i * window_size
            end = min(start + window_size, num_samples)
            window_signal = signal[start:end]

            # Compute RMS amplitude of windowed signal
            rms = np.sqrt(np.mean(np.square(window_signal)))

            # Append result to list
            rms_values.append(rms)

        return timestamps, rms_values