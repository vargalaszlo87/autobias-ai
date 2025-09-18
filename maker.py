#!/usr/bin/python3

import subprocess
import tempfile

print ("Make learn datas");

circuitFile = "common-emitter-01.cir"

# read the circuit-file
with open(circuitFile, "r") as f:
    circuit = f.read()
    tempCircuit = circuit

# make variations
#
# ranges:
#
# RLOAD = 1 -- 1000
RLOAD_minRange = 1
RLOAD_maxRange = 1000
RLOAD_step = 1

transientMin = "0.1m"
transientMax = "20m"
transientStep = ""

# core

value = RLOAD_minRange
while (value <= RLOAD_maxRange):
    # reload the circuit
    circuit = tempCircuit
    
    # options
    circuit += "\n.options savecurrents"
    circuit += "\n.fourier 1k V(out)"
    
    # params
    circuit += "\n.param R1=47000 R2=10000 RC=4.7k RE=1k CE=100u CIN=10u COUT=10u RLOAD=" + str(value) + " VCC=12 HFE=200"

    # control
    circuit += "\n.control"
    
    # operations
    circuit += "\nop"
    circuit += "\ntran "+transientMin+" "+transientMax+" " + transientStep

    # datas
    circuit += "\nwrdata output/data_rload_"+str(value)+".txt V(out) @RLOAD[i]"


    # ends
    circuit += "\n.endc"
    circuit += "\n.end"
    
    # temp file
    # ideiglenes fájl
    with open("circuit.cir", "w") as f:
        f.write(circuit)
    
    subprocess.run(["ngspice", "-b", "circuit.cir"])

    value = value + 1


