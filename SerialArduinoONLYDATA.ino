#include <Arduino.h>
#include <math.h>
#define BAUD_RATE 9600
#define SAMPLING_RATE 300 // Default sampling rate (Hz)
#define DEFAULT_FREQ 10 // Default frequency (Hz)

unsigned long samplingPeriod = 1000000 / SAMPLING_RATE;
int numSamplesPerLoop = SAMPLING_RATE / DEFAULT_FREQ;
float freq = DEFAULT_FREQ;
bool generateSine = false;
int first_measrflag = 0;
int16_t sample = 0;
unsigned long lastTimestamp = 0;

void start() {
  generateSine = true;
  first_measrflag = 1; // send the first sample for time synchronisation
}

void stop() {
  generateSine = false;
}

void sendCsv(unsigned long timestamp, int16_t sample) {
  char csv[48];
  sprintf(csv, "%lu,%d;", timestamp, sample);
  Serial.println(csv);
}

void setup() {
  Serial.begin(BAUD_RATE);
}

void loop() {
  if (Serial.available() > 0) {
    int input = Serial.parseInt();
    if (input == 1) {
      start();
    } else if (input == 2) {
      stop();
      sample = 0;
      lastTimestamp = 0;
    } else if (input >= 10 && input <= 1000) {
      freq = input;
    }
  }

  if (generateSine) {
    for (int i = 0; i < numSamplesPerLoop; i++) {
      int16_t sample = 32767 * sin(2 * M_PI * freq * (lastTimestamp / 1000000.0));
      if (first_measrflag == 1) {
        sendCsv(lastTimestamp, sample);
        first_measrflag = 0;
      }
      if (Serial.available() > 0) {
        int input = Serial.parseInt();
        if (input == 3) {
          sendCsv(lastTimestamp, sample);
        } else if (input == 2) {
          stop();
        }
      }
      lastTimestamp += samplingPeriod;
    }
  }
}
