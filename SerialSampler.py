import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import threading

from freq_anal_fixing_ts import FreqAnalyzer
# DEFAULT PYTHON SAMPLING RATE ! THIS IS NOT REACHED THE ARDIUNO IS SLOW
DEFAULT_SAMPLING_RATE = 30
# Arduino sampling rate
ARDUINO_SAMPLING_RATE = 300

 # Time window size in seconds
WINDOW_DURATION = 1 
#NUMBER OF SAMPLES IN A WINDOW
WINDOW_SAMPLES = int(WINDOW_DURATION * ARDUINO_SAMPLING_RATE)

# Frequency range of interest
FREQ_RANGE = (0, 2000)





### Flag to indicate finishing collection if one window data of lenth 
analyse_window_flag = False
evaluate_sampling_rate  = False
# Create frequency analyzer object



class ArduinoCommunication:
    def __init__(self, port='COM10', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for serial to initialize
        # Flag to indicate when to stop the program
        self.stop_flag = False
        self.num_samples = 100
        self.data = np.zeros((0, 2))

        self.sampling_frequency = 0
        self.analyzer = FreqAnalyzer(DEFAULT_SAMPLING_RATE)

    def start_sine_wave(self):
        self.ser.write(b'1')
        print("Sent start command to Arduino")
    
        while True:
            if self.ser.in_waiting > 0:
                response = self.ser.readline().decode().rstrip()
                timestamp, sample = response.split(",")
                self.data = np.array([[0, 0], [np.uint32(int(timestamp)), int(sample[:-1])]])
                print("first timestamp: ", timestamp)
                print("first sample: ", int(sample[:-1]))
                break

        return self.data
    
    def stop_sine_wave(self):
        self.ser.write(b'2')
        print("Sent stop command to Arduino")
        
    def set_frequency(self, frequency):
        cmd = f'{frequency:.2f}'.encode()
        self.ser.write(cmd)
        print(f"Frequency set to {frequency:.2f} Hz")
    
    
    def sample_data(self, duration, sampling_frequency):
        self.sampling_frequency = sampling_frequency
        num_samples = int(duration * self.sampling_frequency)
        self.data = np.empty((num_samples, 2), dtype=int)
        delay = 1.0 / self.sampling_frequency
        start_time = time.time()
        last_sample_time = start_time  # Initialize the last sample time to start time
    
        for i in range(num_samples):
            self.ser.write(b'3')
            while True:
                if self.ser.in_waiting > 0:
                    response = self.ser.readline().decode().rstrip()
                    timestamp, sample = response.split(",")
                    timestamp = np.uint32(int(timestamp))

                    sample = int(sample[:-1])
                    current_time = time.time()  # Get the current time
                    elapsed_time = current_time - start_time
                    time_since_last_sample = current_time - last_sample_time  # Calculate time since last sample
                    last_sample_time = current_time  # Update the last sample time
                    self.data[i] = [last_sample_time*1000, sample]
                    print(f"timestamp: {timestamp}, sample: {sample}, elapsed time: {elapsed_time:.3f}, time since last sample: {time_since_last_sample:.6f}")
                    break
            time.sleep(delay)
    
        return self.data
    def analyze_signal(self, analyzer):
        counter = 0
        
        results = []  # create an empty list to store the results
        while True:
        # Get signal from queue
            signal, timestamp = analyzer._q.get()

        # Convert timestamp to milliseconds
            timestamp_ms = timestamp.timestamp() * 1000

        # Analyze signal every 100 samples
            counter += 1
            if counter % 100 == 0:
                max_freq, max_amplitude = analyzer.get_max_freq(signal, WINDOW_SAMPLES, FREQ_RANGE)

            # Add results to list
                results.append((timestamp_ms, max_freq))

            # Check if one window data has been collected
                if len(signal) == WINDOW_SAMPLES:
                # Perform analysis on the collected window
                    max_freq, max_amplitude = analyzer.get_max_freqs(signal, WINDOW_SAMPLES, FREQ_RANGE)

                # Add results to list
                    results.append((timestamp_ms, max_freq))

                # Reset flag to indicate that the analysis has been performed
                    global analyse_window_flag
                    analyse_window_flag = False
                    break
                

        # Clear the queue
                analyzer._q.task_done()



    def evaluate_sampling_rate(self,window_data, current_sampling_rate, confidence_parameter, h, max_freq):
    # function body


    # Compute the current maximum frequency from the frequeny analyzer method 
    
        # Set the upper and lower thresholds based on the current maximum frequency and the confidence parameter
        F_max = max_freq
        F_up = min((1 + confidence_parameter) * F_max, current_sampling_rate / 2)
        F_down = (1 - confidence_parameter) * F_max
    # Check if the current maximum frequency is above the upper threshold
        if max_freq > F_up:
        # Increment the counter for the number of consecutive windows above the upper threshold
            global h1,h2
            h1 += 1
            h2 = 0
        # Check if enough consecutive windows have been above the upper threshold to trigger a change in sampling rate
            if h1 > h:
            # Update the maximum frequency
                F_max = max_freq
            # Update the upper and lower thresholds
                F_up = min((1 + confidence_parameter) * F_max, current_sampling_rate / 2)
                F_down = (1 - confidence_parameter) * F_max
            # Update the sampling rate
                new_sampling_rate = F_max * confidence_parameter
            # Reset the counters
                h1 = 0
                h2 = 0
                return new_sampling_rate
    # Check if the current maximum frequency is below the lower threshold
        elif max_freq < F_down:
        # Increment the counter for the number of consecutive windows below the lower threshold
            
            h2 += 1
            h1 = 0
        # Check if enough consecutive windows have been below the lower threshold to trigger a change in sampling rate
            if h2 > h:
            # Update the maximum frequency
                F_max = max_freq
                # Update the upper and lower thresholds
                F_up = min((1 + confidence_parameter) * F_max, current_sampling_rate / 2)
                F_down = (1 - confidence_parameter) * F_max
                # Update the sampling rate
                new_sampling_rate = F_max * confidence_parameter
                # Reset the counters
                h1 = 0
                h2 = 0
                return new_sampling_rate
    # Return the current sampling rate if neither threshold has been crossed
        return current_sampling_rate


    def create_dataframe(self):
        df = pd.DataFrame(self.data, columns=['Elapsed Time', 'Sample'])
        start_time = df['Elapsed Time'].iloc[0]
        end_time = df['Elapsed Time'].iloc[-1]
        duration = end_time - start_time
        print(f"Collected {len(df)} samples in {duration:.3f} seconds")

    # Plot the data
    
     
        self.plot_data(df)

        return df

    def save_to_csv(self, filename):
        df = self.create_dataframe()
        df.to_csv(filename, index=False)
        
    def close(self):
        self.ser.close()
        

    def plot_data(self, df, x_col='Elapsed Time', y_col='Sample'):

        plt.plot(df[x_col], df[y_col], color='red', label='Data')
        plt.xlabel('Time (s)', fontsize=16)
        plt.ylabel('Signal Amplitude', fontsize=16)
        plt.title('Raw Signal', fontsize=16)
        plt.legend(fontsize=14)
        plt.show()


if __name__ == '__main__':
    
    SAMPLERATE = 10  ### iniital
    CONFIDENCE_PAR = 5  ## C in asa 
    NUMBEROFBROKENTHEASHOLDS = 2  ### h in asa 
    
    
    
    analyzer = FreqAnalyzer(DEFAULT_SAMPLING_RATE)  
    arduino = ArduinoCommunication()
    arduino.stop_sine_wave()  # stop sine wave if already started 
    arduino.set_frequency(10.0)  # set frequency
    arduino.start_sine_wave()
    data = arduino.sample_data(1.0,SAMPLERATE)  # sampling function takes (duration in sec , samlping rate in Hz)
    print (data)
    print (type(data))
    print (len(data))
    # Analyze the signal using the frequency analyzer object
    analyzer_thread = threading.Thread(target=arduino.analyze_signal, args=(analyzer,))
    analyzer_thread.start()
    timestamps, max_freqs, spectrum = analyzer.get_max_freqs(signal=data, window_size=5, freq_range=(0, 2000))
    arduinodf = arduino.create_dataframe()  # create dataframe
    
    ## evaluate the new sampling rate
    evaluate_sampling_rate(WINDOW_SAMPLES, SAMPLERATE, CONFIDENCE_PAR, NUMBEROFBROKENTHEASHOLDS, max_freqs)
    
    
    print(arduinodf.head())  # print first few rows of dataframe
    arduino.save_to_csv('data.csv')  # save data to CSV file
    print ( 'now plotting data')
    arduino.plot_data(arduinodf)
    
    
    arduino.close()  # close serial connection
   