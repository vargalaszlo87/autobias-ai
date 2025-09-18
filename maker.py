#!/usr/bin/python3

import subprocess
import tempfile
import numpy as np
from os import system

print ("Make learn datas");

circuitFile = "common-emitter-01.cir"

# delete files
#subprocess.run("rm /autobasis-ai/output/*.*")
system('rm output/test.txt > /dev/null 2>&1')
system('rm output/*.* > /dev/null 2>&1')

# read the circuit-file
with open(circuitFile, "r") as f:
		circuit = f.read()
		tempCircuit = circuit
#
# constans
#
VCC = 12
R1 = 47000
# make variations
#
# ranges:
#
# RLOAD = 1 -- 1000
RLOAD_minRange = 1
RLOAD_maxRange = 100 # 1000
RLOAD_step = 1
#
# hFE
hFE_minRange = 100
hFE_maxRange = 101 # 800
hFE_step = 1
#
# Temperature °C
temperature_minRange = 0
temperature_maxRange = 1 # 80
temperature_step = 1
#
# R2 
R2_minRange = 2200
R2_maxRange = 10000
R2_step = 100
#
# transient
transientMin = "0.1m"
transientMax = "20m"
transientStep = ""

# core

system('echo "Temperature[Clesius];hFE;RLOAD[ohm];RMS(V(out))[A];RMS(I(RLOAD))[A]" > output/test.txt')

temperatureValue = temperature_minRange
while (temperatureValue <= temperature_maxRange):
		valuehFE = hFE_minRange
		while (valuehFE <= hFE_maxRange):
				valueRLOAD = RLOAD_minRange
				while (valueRLOAD <= RLOAD_maxRange):
						# reload the circuit
						circuit = tempCircuit
						
						# options
						circuit += "\n.options savecurrents"
						circuit += "\n.temp "+str(temperatureValue)
						circuit += "\n.fourier 1k V(out)"
						
						# params
						circuit += "\n.param R1=47000 R2=10000 RC=4.7k RE=1k CE=100u CIN=10u COUT=10u RLOAD=" + str(valueRLOAD) + " VCC=12 HFE="+str(valuehFE)+""

						# control
						circuit += "\n.control"
						
						# operations
						circuit += "\nop"
						circuit += "\ntran "+transientMin+" "+transientMax+" " + transientStep

						# datas
						circuit += "\nwrdata output/data_"+str(valueRLOAD)+"_"+str(valuehFE)+"_"+str(temperatureValue)+".txt V(out) @RLOAD[i]"


						# ends
						circuit += "\n.endc"
						circuit += "\n.end"
						
						# temp file
						# ideiglenes fájl
						with open("circuit.cir", "w") as f:
								f.write(circuit)
						
						subprocess.run(["ngspice", "-b", "circuit.cir"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

						# make RMS
						data = np.loadtxt("output/data_"+str(valueRLOAD)+"_"+str(valuehFE)+"_"+str(temperatureValue)+".txt")
						col2 = data[:,1]
						col4 = data[:,3]

						# RMS számítás
						rms2 = np.sqrt(np.mean(col2**2))
						rms4 = np.sqrt(np.mean(col4**2))

						system('echo "'+str(temperatureValue)+';'+str(valuehFE)+';'+str(valueRLOAD)+';'+str(rms2)+';'+str(rms4)+'" >> output/test.txt')

						# deletes
						system("rm output/data_"+str(valueRLOAD)+"_"+str(valuehFE)+"_"+str(temperatureValue)+".txt");
						
						data = ""
						col2 = ""
						col4 = ""

						valueRLOAD = valueRLOAD + RLOAD_step

				valuehFE = valuehFE + hFE_step

		temperatureValue = temperatureValue + temperature_step


