#include <Arduino.h>
#include <math.h>
#include <string.h>

#define SAMPLING_RATE 1000 // Default sampling rate (Hz)
#define DEFAULT_FREQ 10 // Default frequency (Hz)

unsigned long lastTimestamp = 0;
unsigned long samplingPeriod = 1000000 / SAMPLING_RATE;
int numSamplesPerLoop = SAMPLING_RATE / DEFAULT_FREQ;
float freq = DEFAULT_FREQ;
bool generateSine = false;

void start() {
  generateSine = true;
}

void stop() {
  generateSine = false;
}

void sendCsv(int16_t sample, unsigned long timestamp) {
  char csv[32];
  sprintf(csv, "%d,%lu;", sample, timestamp);
  Serial.println(csv);
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {}
}

void loop() {
  if (Serial.available() > 0) {
    byte incomingByte = Serial.read();
    char command[1];
    Serial.readBytes(command, 1);

    if (command[0] == 0xA0) {
      start();
    } else if (command[0] == 0xB0) {
      stop();
    }
  }

  if (generateSine) {
    for (int i = 0; i < numSamplesPerLoop; i++) {
      float t = i / (float)SAMPLING_RATE;
      float phase = 2 * M_PI * freq * t;
      int16_t sample = 32767 * sin(phase);

      if (Serial.available() > 0) {
        if (Serial.read() == 0xEE) {
          sendCsv(sample, lastTimestamp);
        }
      }

      lastTimestamp += samplingPeriod;

      if (!generateSine) {
        break;
      }
    }
  }
}
