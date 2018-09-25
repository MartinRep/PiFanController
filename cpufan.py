# Monitors CPU temp and turn ON fan on GPIO 21 when CPU temp > 55, turns it OFF once it's back below 45 'C

# 1. run: crontab -e
# 2. append: @reboot python3 /home/pi/cpufan.py
# 3. Save and Exit
# 4. Reboot Raspberry PI
# 5. Check for running script by running: tail -f /home/pi/<YYY-MM-DD>.log file. Relace YYY-MM-DD in file name with current date of course.

import os
from time import sleep
import time
import datetime
import sys
import RPi.GPIO as GPIO
import psutil
import logging

pin = 21        # GPIO pin number for FAN transistor control
maxTMP = 55     # Temperature of CPU when FAN turns ON
refreshRate = 10        # Refresh rate for temp measurement.
cooldown_temp = 45      # Temperature of CPU when FAN turns OFF.
logFolder = "/home/pi/.cpuTempLog/"

def setup():
        GPIO.setwarnings(False)        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        if not os.path.isdir(logFolder):
                os.makedirs(logFolder)
                print("log folder created: " + logFolder)
        return()

def getCPUtemperature():
	res = os.popen('vcgencmd measure_temp').readline()
	temp = float((res.replace("temp=","").replace("'C\n","")))
	return temp

def getCPUfrequency():
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq') as freqFile:
                freq = float(freqFile.read().replace('\n',''))
        return freq

def CPUusage():
        CPU_Pct = psutil.cpu_percent()
        return CPU_Pct
        
def fanON():
        GPIO.output(pin,True)
        logging.info("Fan ON\n")
        return()

def fanOFF():
        GPIO.output(pin,False)
        logging.info("Fan OFF\n")
        return()

try:
        setup()
        count = 0
        tempsum = 0
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        lowest_temp = getCPUtemperature()
        ltemp_time =  str(st)
        highest_temp = getCPUtemperature()
        htemp_time =  str(st)
        logfile = logFolder + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d') + ".log"
        logging.basicConfig(filename = logfile, level = logging.INFO)
        logging.info("Monitoring CPU temp...")
        while True:
                CPU_freq = getCPUfrequency() / 1000
                temp = getCPUtemperature()
                ts = time.time()
                st = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
                logging.info("%s \n-------------------------\n" %st)
                logging.info("Temp: %.2f C" %temp)
                logging.info("CPU freq: %0.0f Mhz" %(CPU_freq))
                logging.info("CPU usage: %0.1f\n" %(CPUusage()))
                tempsum += temp
                count += 1
                if temp > highest_temp:         # Records highest temp
                        highest_temp = temp
                        htemp_time =  st
                if temp < lowest_temp:          # Records lowest temp
                        lowest_temp = temp
                        ltemp_time =  st
                if temp > maxTMP:       # CPU temp above max temperature set
                        fanON()
                elif temp < cooldown_temp:     # Turns fan off only if CPU temp is lower then cooldown_temp.
                        fanOFF()
               
                sleep(refreshRate)
        
except KeyboardInterrupt:       # Gracefull shutdown
        logging.info("Average temp was %0.2f C" %(tempsum/count))
        logging.info("Highest temp: %0.2f C at %s" %(highest_temp, htemp_time))
        logging.info("Lowest temp: %0.2f C at %s" %(lowest_temp, ltemp_time))
        logging.info("CPU temp monitoring SHUTDOWN!")
        fanOFF()