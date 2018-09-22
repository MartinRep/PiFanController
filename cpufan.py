import os
from time import sleep
import time
import datetime
import sys
import RPi.GPIO as GPIO
from multiprocessing import Process, active_children, cpu_count, Pipe
import psutil
import logging



pin = 22        # GPIO pin number for FAN transistor control
maxTMP = 55     # Temperature of CPU when FAN turns ON
procs = []
FIB_N = 100
fan_flip = 0    # timestamp for fan switch calculations
flip_interval = 60      # defines minimum time in seconds for FAN to flip switch
load_interval = 600     # duration of CPU full load. In seconds
cooldown_temp = 45      # Temperature of CPU when FAN turns OFF.


def setup():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.setwarnings(False)
        global fan_flip
        fan_flip = time.monotonic()
        return()

def getCPUtemperature():
	res = os.popen('vcgencmd measure_temp').readline()
	temp = float((res.replace("temp=","").replace("'C\n","")))
	#print("temp is {0}".format(temp)) #Uncomment here for testing
	return temp

def getCPUfrequency():
        with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq') as freqFile:
                freq = float(freqFile.read().replace('\n',''))
        return freq

def fib(n):
    if n < 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

def loop():
        while True:
                fib(FIB_N)


def CPUmax():
        #command = 'sysbench --test=cpu --cpu-max-prime=' + str(prime) + ' --num-threads=4 run'
        #print(command)
        #reult = os.popen(command).readline()
        for i in range(cpu_count()):
                p_conn, ch_conn = Pipe()
                proc = Process(target=loop)
                proc.start()
                procs.append(proc)
        return()

def CPUmin():
        for p in procs:
                p.terminate()

def CPUusage():
        CPU_Pct = psutil.cpu_percent()
        #print(CPU_Pct)
        return CPU_Pct

def logg(msg):
        print(msg)
        logging.info(msg)
        
def setPin(mode): # useful if you want to add logging
        GPIO.output(pin, mode)
        return()

def fanON():
        global fan_flip
        last_flip = (time.monotonic() - fan_flip)       # Only flip the switch once every 60 seconds
        logg("flip time %0.2f" %last_flip)
        if last_flip > flip_interval:
                setPin(True)
                logg("Fan ON")
                fan_flip = time.monotonic()     # Reset flip timer
        return()

def fanOFF():
        global fan_flip
        last_flip = (time.monotonic() - fan_flip)       # Only flip the switch once every 60 seconds
        if last_flip > flip_interval:
                setPin(False)
                logg("Fan OFF")
                fan_flip = time.monotonic()     # Reset flip timer
        return()

logging.basicConfig(filename = "CPUtest.log", level = logging.INFO)

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

        CPUmax()        # Turn ON full load on all CPU cores
        logg("CPU load set to MAX")
        cpu_load = time.monotonic()

        while True:
                CPU_freq = getCPUfrequency() / 1000
                temp = getCPUtemperature()
                ts = time.time()
                st = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
                logg("\n%s \n-------------------------\nTemp: %.2f C" %(st, temp))
                logg("CPU freq: %0.0f Mhz" %(CPU_freq))
                logg("CPU usage: %0.1f" %(CPUusage()))
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
                if (time.monotonic() - cpu_load) > load_interval:       # Only runs CPU load for period of time
                        logg("CPU load turned OFF")
                        CPUmin()
                sleep(1)
        
except KeyboardInterrupt:       # Gracefull shutdown
        logg("Average temp was %0.2f C" %(tempsum/count))
        logg("Highest temp: %0.2f C at %s" %(highest_temp, htemp_time))
        logg("Lowest temp: %0.2f C at %s" %(lowest_temp, ltemp_time))
        logg("Number of Cores %d" % len(procs))
        CPUmin()
        logg("Processes terminated")
        fanOFF()