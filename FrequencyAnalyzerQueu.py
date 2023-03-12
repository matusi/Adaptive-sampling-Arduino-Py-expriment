import queue
import numpy as np

class FreqAnalyzer:
    def __init__(self, sampling_rate, max_queue_size):
        self.sampling_rate = sampling_rate
        self.max_queue_size = max_queue_size
        self._q = queue.Queue(maxsize=max_queue_size)

    def add_to_queue(self, data):
        if self._q.qsize() < self.max_queue_size:
            self._q.put(data)
        else:
            self._q.get()
            self._q.put(data)

    def analyze_queue(self, window_size, freq_range=None):
        # Check if queue is full
        if self._q.qsize() < self.max_queue_size:
            return None

        # Combine data in queue into single signal
        signal = np.concatenate(list(self._q.queue))

        # Calculate timestamps for each window
        num_samples = len(signal)
        num_windows = int(np.ceil(num_samples / window_size))
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
