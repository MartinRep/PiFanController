import os
from time import sleep
import time
import datetime
import sys
import RPi.GPIO as GPIO

pin = 1
maxTMP = 40


def setup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pin, GPIO.OUT)
	GPIO.setwarnings(False)
	return()

def getCPUtemperature():
	res = os.popen('vcgencmd measure_temp').readline()
	temp =(res.replace("temp=","").replace("'C\n",""))
	#print("temp is {0}".format(temp)) #Uncomment here for testing
	return temp

def setPin(mode): # useful if you want to add logging
    GPIO.output(pin, mode)
    return()

def fanON():
    setPin(True)
    return()

def fanOFF():
    setPin(False)
    return()

def getTEMP():
    CPU_temp = float(getCPUtemperature())
    if CPU_temp>maxTMP:
        fanON()
    else:
        fanOFF()
    return()

try:
	count = 0
	tempsum = 0
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	lowest_temp = float(getCPUtemperature())
	ltemp_time =  str(st)
	highest_temp = float(getCPUtemperature())
	htemp_time =  str(st)
	while True:
		temp = float(getCPUtemperature())
		ts = time.time()
		st = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
		print("%s Temp: %.2f C" %(st, temp))
		tempsum += temp
		count += 1
		if temp > highest_temp:
			highest_temp = temp
			htemp_time =  st
		if temp < lowest_temp:
                        lowest_temp = temp
                        ltemp_time =  st
		sleep(5)
except KeyboardInterrupt:
	print("Average temp was %0.2f C" %(tempsum/count))
	print("Highest temp: %0.2f C at %s" %(highest_temp, htemp_time))
	print("Lowest temp: %0.2f C at %s" %(lowest_temp, ltemp_time))

#setup()
#fanOFF()
#print("FAN OFF")
#sleep(30)
#fanON()
#print("FAN ON")
#sleep(30)
#fanOFF()
#print("FAN OFF")
