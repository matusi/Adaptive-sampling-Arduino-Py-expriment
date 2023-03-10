## Adaptive-sampling-Arduino-Py-expriment
The following setup is being used to evaluate the implementation of the based spectrum adaptive sampling algorithm.
A microcontroller (Arduino) is being used to generate a sine wave continuously with a pre-programmed sampling rate.

The computer is connected to the Arduino Via Serial.

'1' command will start the sine wave generation.
'2' command will stop the sine wave generation and restart the values.
'3' command is used to return timestamp and sample from the sine wave current value.
'x' command where x is an integer  greater than 10 and lesser then 1000 is used to update the frequency of the generated sine wave.




For this setup, the Arduino is considered to be a sensor and the computer describes a sensor controller.
According to the Nyquist criterion, the generated sine wave can be recovered with the computer if the sampling rate $F_s$.

 F_s >= freq_{sine} * 2 .




## Adaptive sampling
The implementation of the adaptive sampling acquisition in python consists if the following blocks 


  # A sampler block  which takes  as input a given duration and the sampling rate to handle the data acquisition  from the microcontroller for the given window of time.
   # A spectrum analyzer block which takes a signal, an analyses  window size and the sampling rate to return the maximum frequency detected in the spectrum of the signal.
       
       
       
 # An adaptive sampling evaluation block which takes as input the current detected maximum frequency from a given window and the current sampling rate, an algorithm confidence parameters to handle the evaluation of the spectrum and the metric used to output the next sampling rate for the next window of time which is sent to the sampler.
          

