#!/usr/bin/env python
import sys
import time
import os
import subprocess
import RPi.GPIO as io
import Adafruit_DHT
import paho.mqtt.client as mqtt
import datetime
 
io.setmode(io.BCM)
io.setwarnings(False)
SHUTOFF_DELAY = 20  # seconds
DHT_READ_DELAY = 4  # 
PIR_PIN = 25        # PIR pin on the board
DHT_PIN = 26        # DHT pin
io.setup(22, io.OUT) # Backlight pin
pwm=io.PWM(22, 100)  # Backlight PWM
pwm.start(0)

# Primary display
os.environ['DISPLAY'] = ":0"
 
def main():
    io.setup(PIR_PIN, io.IN)
    turned_off = False
    last_motion_time = time.time()
    last_motion_dt = datetime.datetime.now()
    last_dht_time = time.time()
    
    # MQTT Client - Change to your own parameters
    mq_client = mqtt.Client()
    mq_client.connect('10.10.10.10', 1888, 60)
    mq_msg = {}
 
    while True:
        if io.input(PIR_PIN):
            last_motion_time = time.time()
            # print(f"motion! {last_motion_time}")
            sys.stdout.flush()
            if turned_off:
                turned_off = False
                last_motion_dt = datetime.datetime.now()
                turn_on()
        else:
            # print(f'No motion! {last_motion_time}')
            if not turned_off and time.time() > (last_motion_time + SHUTOFF_DELAY):
                turned_off = True
                turn_off()
        if time.time() > (last_dht_time + DHT_READ_DELAY):
            hum, temp = Adafruit_DHT.read(Adafruit_DHT.DHT11, DHT_PIN)
            last_dht_time = time.time()
            if hum is not None and temp is not None:
                # print(f'{last_dht_time}: Hum: {hum}% --- Temp: {temp}C')
                mq_msg['Time'] = datetime.datetime.now().isoformat(timespec='seconds')
                mq_msg['DHT11'] = {
                    'Temperature': temp,
                    'Humidity': hum,
                    'DewPoint': calc_dewpoint(temp, hum)}
                mq_msg['TempUnit'] = 'C'
                mq_msg['LastMotionTime'] = last_motion_dt.isoformat(timespec='seconds')
                print(mq_msg)
                mq_client.publish('panels/panel_upstairs/SENSOR', payload=str(mq_msg), qos=0, retain=False)
        time.sleep(.1)
    mq_client.loop_forever()
        
 
def turn_on():
    # Use DPMS to turn on the display, and fades in the backlight
    subprocess.call('XAUTHORITY=~panel/.Xauthority DISPLAY=:0 xset dpms force on && xset -dpms && xset s off', shell=True)
    for dc in range(0,100,1):
        # print(dc)
        pwm.ChangeDutyCycle(100-dc)
        time.sleep(0.01)
 
def turn_off():
    # fades out the backlight and uses DPMS to turn off the display
    for dc in reversed(range(0,100,1)):
        # print(dc)
        pwm.ChangeDutyCycle(100-dc)
        time.sleep(0.01)
    subprocess.call('XAUTHORITY=~panel/.Xauthority DISPLAY=:0 xset dpms force off && xset s off', shell=True)

def calc_dewpoint(temp, hum):
    # Calculate the dewpoint from the temperature and humidity from the DHT11 sensor
    return round((((hum / 100) ** 0.125) * (112 + 0.9 * temp) + (0.1 * temp) - 112),1)
    
 
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        io.cleanup()
