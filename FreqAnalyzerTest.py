
import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import threading

from freq_anal_fixing_ts import FreqAnalyzer

import numpy as np

analyzer = FreqAnalyzer(sampling_rate=44100)
test_signal = np.sin(2*np.pi*1000*np.arange(44100)/44100)
timestamps, max_freqs, spectrum = analyzer.get_max_freqs(signal=test_signal, window_size=1024, freq_range=(800, 1200))
print(max_freqs)
