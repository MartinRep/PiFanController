import os
from time import sleep
import time
import datetime
import sys
import RPi.GPIO as GPIO
from multiprocessing import Process, active_children, cpu_count, Pipe
import psutil
import logging



pin = 1
maxTMP = 40
procs = []
FIB_N = 100


def setup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin, GPIO.OUT)
	GPIO.setwarnings(False)
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
    setPin(True)
    return()

def fanOFF():
    setPin(False)
    return()

logging.basicConfig(filename = "CPUtest.log", level = logging.INFO)

try:
	count = 0
	tempsum = 0
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	lowest_temp = getCPUtemperature()
	ltemp_time =  str(st)
	highest_temp = getCPUtemperature()
	htemp_time =  str(st)
	CPUmax()
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
                if temp > highest_temp:
                        highest_temp = temp
                        htemp_time =  st
                if temp < lowest_temp:
                        lowest_temp = temp
                        ltemp_time =  st
                sleep(1)
        
except KeyboardInterrupt:
        logg("Average temp was %0.2f C" %(tempsum/count))
        logg("Highest temp: %0.2f C at %s" %(highest_temp, htemp_time))
        logg("Lowest temp: %0.2f C at %s" %(lowest_temp, ltemp_time))
        logg("Number of Cores %d" % len(procs))
        for p in procs:
                p.terminate()
        logg("Processes terminated")

#setup()
#fanOFF()
#print("FAN OFF")
#sleep(30)
#fanON()
#print("FAN ON")
#sleep(30)
#fanOFF()
#print("FAN OFF")
#test
