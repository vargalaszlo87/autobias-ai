#!/usr/bin/python3

import subprocess
import tempfile
import numpy as np
from os import system
import math
import sys
import json

# clear all 
system ("clear");

#
# title 
#
name = "dataMaker"
version = "v.1.0"
title = name + " " + version + "\n"
#
print (title);
#

circuitFile = "common-emitter-01.cir"
outputFile = "output.txt"

#
# delete or continue
#
isContinue = 0
if len(sys.argv) > 1:
    if sys.argv[1] == "continue":
        isContinue = 1
if isContinue == 0:
    system('rm output/*.* > /dev/null 2>&1')
#
# read the circuit-file
with open(circuitFile, "r") as f:
		circuit = f.read()
		tempCircuit = circuit
#

               
#
# constans
#
VCC = 12
# make variations
#
# the counter of the variations
# 
countVariation = []
#
# ranges:
#
# RLOAD = 1 -- 1000
RLOAD_minRange = 1
RLOAD_maxRange = 100 # 1000
RLOAD_step = 1
countVariation.append((RLOAD_maxRange - RLOAD_minRange) / RLOAD_step)
#
# hFE
hFE_minRange = 100
hFE_maxRange = 800 # 800
hFE_step = 50
countVariation.append((hFE_maxRange - hFE_minRange) / hFE_step)
#
# Temperature °C
temperature_minRange = 20
temperature_maxRange = 40 # 80
temperature_step = 1
countVariation.append((temperature_maxRange - temperature_minRange) / temperature_step)
#
# R1 
R1_minRange = 10000
R1_maxRange = 100000
R1_step = 1000
countVariation.append((R1_maxRange - R1_minRange) / R1_step)
#
# R2 
R2_minRange = 2000
R2_maxRange = 5000 
R2_step = 100
countVariation.append((R2_maxRange - R2_minRange) / R2_step)
#
# RE
RE_minRange = 0
RE_maxRange = 500
RE_step = 100
countVariation.append((RE_maxRange - RE_minRange) / RE_step)
#
# RC
RC_minRange = 1000
RC_maxRange = 5000
RC_step = 100
countVariation.append((RC_maxRange - RC_minRange) / RC_step)
#
# transient
transientMin = "0.1m"
transientMax = "20m"
transientStep = ""

# core

# variations:
maxVariations = math.floor(math.prod(countVariation));
maxFileSize = math.floor(maxVariations * 47 / math.pow(1024,2))

system('echo "Temperature[Clesius];hFE;RLOAD[ohm];R1[ohm];R2[ohm];RC[ohm];RE[ohm];RMS(V(out))[A];RMS(I(RLOAD))[A]" > output/' + outputFile)

counterMain = 0
R1_value = R1_minRange
while (R1_value <= R1_maxRange):
    R2_value = R2_minRange
    while (R2_value <= R2_maxRange):
        RC_value = RC_minRange
        while (RC_value <= RC_maxRange):
            RE_value = RE_minRange
            while (RE_value <= RE_maxRange):
                valueTemperature = temperature_minRange
                while (valueTemperature <= temperature_maxRange):
                    valuehFE = hFE_minRange
                    while (valuehFE <= hFE_maxRange):
                        valueRLOAD = RLOAD_minRange
                        while (valueRLOAD <= RLOAD_maxRange):
                            
                            #
                            # status refresh
                            #
                            counterMain = counterMain + 1
                            if counterMain % 100 == 0:
                                
                                # screen 
                                system("clear")
                                print (title)
                                print (str(counterMain / maxVariations * 100) + "% -> " + f"{counterMain:,}".replace(",", " ") + " / " + f"{maxVariations:,}".replace(",", " ") + "\r")
                                print ("File size in Mbyte: " + f"{maxFileSize:,}".replace(",", " "));

                                #values now
                                params = {
                                    "R1": R1_value,
                                    "R2": R2_value,
                                    "RC": RC_value,
                                    "RE": RE_value,
                                    "temperature": valueTemperature,
                                    "hFE" : valuehFE,
                                    "RLOAD" : valueRLOAD
                                }
                                with open("output/params.json", "w") as f:
                                    json.dump(params, f, indent=4)       
                            #
                                                           
                            # reload the circuit
                            circuit = tempCircuit
                            
                            # options
                            circuit += "\n.options savecurrents"
                            circuit += "\n.temp "+str(valueTemperature)
                            circuit += "\n.fourier 1k V(out)"
                            
                            # params
                            circuit += "\n.param R1=" + str(R1_value) + " R2=" + str(R2_value) + " RC=" + str(RC_value) + " RE=" +str(RE_value)+ " CE=100u CIN=10u COUT=10u RLOAD=" + str(valueRLOAD) + " VCC=12 HFE="+str(valuehFE)+""

                            # control
                            circuit += "\n.control"
                            
                            # operations
                            circuit += "\nop"
                            circuit += "\ntran "+transientMin+" "+transientMax+" " + transientStep

                            # datas
                            # tempFileName = "data_"+str(valueRLOAD)+"_"+str(valuehFE)+"_"+str(valueTemperature)+".txt"
                            tempFile = "tempFile.txt"
                            circuit += "\nwrdata output/" +tempFile+ " V(out) @RLOAD[i]"

                            # ends
                            circuit += "\n.endc"
                            circuit += "\n.end"
                            
                            # temp file
                            # ideiglenes fájl
                            with open("circuit.cir", "w") as f:
                                f.write(circuit)
                            f.close()    
                                                        
                            subprocess.run(["ngspice", "-b", "circuit.cir"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

                            # make RMS
                            data = np.loadtxt("output/" + tempFile)
                            col2 = data[:,1]
                            col4 = data[:,3]

                            # RMS számítás
                            rms2 = np.sqrt(np.mean(col2**2))
                            rms4 = np.sqrt(np.mean(col4**2))

                            system('echo "'+str(valueTemperature)+';'+str(valuehFE)+';'+str(valueRLOAD)+';'+str(R1_value)+';'+str(R2_value)+';'+str(RC_value)+';'+str(RE_value)+';'+f"{rms2:.3e}"+';'+f"{rms4:.3e}"+'" >> output/' + outputFile)

                            # deletes
                            # system("rm output/" + tempFileName);
                            
                            data = ""
                            col2 = ""
                            col4 = ""

                            valueRLOAD = valueRLOAD + RLOAD_step

                        valuehFE = valuehFE + hFE_step

                    valueTemperature = valueTemperature + temperature_step

                R2_value = R2_value + R2_step

            RE_value = RE_value + RE_step
        
        RC_value = RC_value + RC_step

    R1_value = R1_value + R1_step
    
    
