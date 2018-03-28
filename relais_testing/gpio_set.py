#!/usr/bin/python3
import RPi.GPIO as GPIO
import sys

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    inp = input("gpio-number: ")
    n = int(inp)
    GPIO.setup(n, GPIO.OUT)

    on = False
    while True:
        inp = input("toggle?")
        if inp == "exit":
            GPIO.cleanup()
            sys.exit()
        else:
            if on:
                GPIO.output(n, GPIO.LOW)
            else:
                GPIO.output(n, GPIO.HIGH)
            on = not on

