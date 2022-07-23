#!/usr/bin/python3

"""
    Program: LCD1602 Demo with HC-SR04 Sensor (lcd-demo.py)
    Author:  M. Heidenreich, (c) 2020
    Description:
    
    This code is provided in support of the following YouTube tutorial:
    https://youtu.be/DHbLBTRpTWM
    This example shows how to use the LCD1602 I2C display and the HC-SR04 sensor
    with Raspberry Pi using a multi-threaded approach.
    THIS SOFTWARE AND LINKED VIDEO TOTORIAL ARE PROVIDED "AS IS" AND THE
    AUTHOR DISCLAIMS ALL WARRANTIES INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from threading import Thread
from rpi_lcd import LCD
from mpd import MPDClient
import RPi.GPIO as GPIO

reading = True
message = ""

lcd = LCD()

client = MPDClient()
client.timeout = 10
client.idletimeout = None
client.connect("localhost", 6600)
print(client.mpd_version)

buttonPlay = 17
buttonNext = 27
buttonPrev = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPlay, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonNext, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttonPrev, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def safe_exit(signum, frame):
    exit(1)

def update_lcd():
    while reading:
        try:
            currentsong = client.currentsong()
            #print(currentsong)
            lcd.text(currentsong["title"][:16], 1)
        except:
            print("Current song failed")
        sleep(10)

def read_buttons():
    while reading:
        playButtonValue = GPIO.input(buttonPlay)
        if playButtonValue == False:
            print("Toggle")
            try:
                client.pause()
            except:
                print("Toggle failed")
            while GPIO.input(buttonPlay) == False:
                pass
            print("Toggled")
        nextButtonValue = GPIO.input(buttonNext)
        if nextButtonValue == False:
            print("Next")
            try:    
                client.next()
                client.play()
            except:
                print("Next failed")
            while GPIO.input(buttonNext) == False:
                pass
            print("Nexted")
        #prevButtonValue = GPIO.input(buttonPrev)
        #if prevButtonValue == False:
        #    print("Prev")
        #    client.previous()
        #    client.play()
        #    while GPIO.input(buttonPrev) == False:
        #        pass
        #    print("Preved")
        sleep(0.1)

try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    lcd.clear()
    lcd.text("WLAN Radio", 1)

    client.play()

    display = Thread(target=update_lcd, daemon=True)
    buttonread = Thread(target=read_buttons, daemon=True)

    display.start()
    buttonread.start()

    pause()

except KeyboardInterrupt:
    pass

finally:
    reading = False
    display.join()
    buttonread.join()
    lcd.clear()
    sensor.close()
    client.close()
    client.disconnect()
