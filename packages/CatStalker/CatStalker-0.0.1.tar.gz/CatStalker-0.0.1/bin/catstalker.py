#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import argparse

# The binary [PIN_1, PIN_0] == ~(socket - 1)
PIN_0 = 15
PIN_1 = 11

PWR_PIN = 13 # 1 == on, 0 == off
ALL_PIN = 16 # 0 == all, 1 == socket count by PIN_1, PIN_0

def main():
    parser = argparse.ArgumentParser(
        description='control energenie remote board for raspberry pi')
    parser.add_argument('-s', '--socket', type=int,
                        help='control specified socket from 1-4 (default = all)')
    parser.add_argument('-o', '--off', action='store_true',
                        help='turn socket(s) off (default is to turn on)')
    args = parser.parse_args()

    try:
        # set the pins numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Select the GPIO pins used for the encoder K0-K3 data inputs
        GPIO.setup(PIN_1, GPIO.OUT)
        GPIO.setup(PIN_0, GPIO.OUT)
        GPIO.setup(ALL_PIN, GPIO.OUT)
        GPIO.setup(PWR_PIN, GPIO.OUT)

        # Select the signal used to select ASK/FSK
        GPIO.setup(18, GPIO.OUT)

        # Select the signal used to enable/disable the modulator
        GPIO.setup(22, GPIO.OUT)

        # Disable the modulator by setting CE pin lo
        GPIO.output(22, False)

        # Set the modulator to ASK for On Off Keying
        # by setting MODSEL pin lo
        GPIO.output(18, False)

        # Initialise K0-K3 inputs of the encoder to 0000
        GPIO.output(PIN_1, False)
        GPIO.output(PIN_0, False)
        GPIO.output(ALL_PIN, False)
        GPIO.output(PWR_PIN, False)
        time.sleep(0.25)

        pin_pwr = not args.off
        pin_all = args.socket is None
        pin0 = pin_all or (args.socket - 1) % 1 == 0
        pin1 = pin_all or (args.socket - 1) % 2 == 0

        set_output(pin1, pin0, pin_all, pin_pwr)

        GPIO.cleanup()

    # Clean up the GPIOs for next time
    except KeyboardInterrupt:
        GPIO.cleanup()

def set_output(pin1, pin0, pin_all, pin_pwr):
    GPIO.output(PIN_1, pin1)
    GPIO.output(PIN_0, pin0)
    GPIO.output(ALL_PIN, not pin_all) # inverted
    GPIO.output(PWR_PIN, pin_pwr)
    # let it settle, encoder requires this
    time.sleep(0.1)
    # Enable the modulator
    GPIO.output(22, True)
    # keep enabled for a period
    time.sleep(0.25)
    # Disable the modulator
    GPIO.output(22, False)

main()
