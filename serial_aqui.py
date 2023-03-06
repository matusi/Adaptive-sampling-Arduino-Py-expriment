import serial
import time

# configure the serial port
ser = serial.Serial('COM10', 9600, timeout=1)

# wait for Arduino to reset
time.sleep(2)

# send start signal to Arduino
print("Starting signal...")
ser.write(b'\xA0')
response = ser.readline()
print("Response from Arduino:", response)

# read data from Arduino
print("Reading data...")
while True:
    response = ser.readline()
    print("Received data from Arduino:", response.decode().strip())
    
    # check for stop signal from user
    user_input = input("Enter 's' to stop: ")
    if user_input == 's':
        # send stop signal to Arduino
        print("Stopping signal...")
        ser.write(b'\xB0')
        response = ser.readline()
        print("Response from Arduino:", response)
        break

# close the serial port
ser.close()
