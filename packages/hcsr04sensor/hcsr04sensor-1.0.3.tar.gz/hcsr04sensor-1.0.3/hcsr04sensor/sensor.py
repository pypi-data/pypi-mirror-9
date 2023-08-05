# simple module for measuring distance with an Ultrasonic sound sensor
# and a Raspberry Pi
# Al Audet
# MIT License

import time
import math
import RPi.GPIO as GPIO


class Measurement(object):
    '''Create a measurement using an HC-SR04 Ultrasonic Sensor'''
    def __init__(self, trig_pin, echo_pin, rounded_to, temperature):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.rounded_to = rounded_to
        self.temperature = temperature

    def distance(self):
        """Return the distance, in cm, of an object adjusted for
        temperature in Celcius."""
        speed_of_sound = 331.3 * math.sqrt(1+(self.temperature / 273.15))
        sample = []
        for distance_reading in range(11):
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trig_pin, GPIO.LOW)
            time.sleep(0.3)
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trig_pin, False)
            while GPIO.input(self.echo_pin) == 0:
                sonar_signal_off = time.time()
            while GPIO.input(self.echo_pin) == 1:
                sonar_signal_on = time.time()
            time_passed = sonar_signal_on - sonar_signal_off
            distance_cm = time_passed * ((speed_of_sound * 100) / 2)
            sample.append(distance_cm)
            GPIO.cleanup()
        sorted_sample = sorted(sample)
        sensor_distance = sorted_sample[5]
        return round(sensor_distance, self.rounded_to)
