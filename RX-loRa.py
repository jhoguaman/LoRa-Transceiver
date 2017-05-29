#!/usr/bin/python
# -*- coding: utf-8 -*-
import spidev
#|import RPi.GPIO as GPIO
import time

_slaveSelectPin = 17        #SPI Chip select input
content = ""
currentMode             =   0x81
#msg[]

#establecemos el sistema de numeracion que queramos, en mi caso BCM
#|GPIO.setmode(GPIO.BCM)

#configuramos el pin GPIO17 como una salida
#|GPIO.setup(_slaveSelectPin, GPIO.OUT)




REG_FIFO 		         =   0x00
REG_FIFO_ADDR_PTR        =   0x0D
REG_FIFO_TX_BASE_AD      =   0x0E
REG_FIFO_RX_BASE_AD      =   0x0F
REG_RX_NB_BYTES          =   0x13
REG_OPMODE               =   0x01
REG_FIFO_RX_CURRENT_ADDR =   0x10
REG_IRQ_FLAGS            =   0x12
REG_DIO_MAPPING_1        =   0x40
REG_DIO_MAPPING_2        =   0x41

REG_MODEM_CONFIG         =   0x1D
REG_MODEM_CONFIG2        =   0x1E

REG_PAYLOAD_LENGTH       =   0x22
REG_IRQ_FLAGS_MASK       =   0x11
REG_HOP_PERIOD           =   0x24

# MODES
RF92_MODE_RX_CONTINUOS   =   0x85
RF92_MODE_TX             =   0x83
RF92_MODE_SLEEP          =   0x80
RF92_MODE_STANDBY        =   0x81

PAYLOAD_LENGTH           =   0x0A
IMPLICIT_MODE            =   0x0E

#POWER AMPLIFIER CONFIG
REG_PA_CONFIG            =   0x09
PA_MAX_BOOST             =   0x8F
PA_LOW_BOOST             =   0x81
PA_MED_BOOST             =   0x8A
PA_OFF_BOOST             =   0x00

#LOW NOISE AMPLIFIER
REG_LNA                  =   0x0C
LNA_MAX_GAIN             =   0x23  # 0010 0011
LNA_OFF_GAIN             =   0x00

REG_PA_DAC               =   0x5A

#PREAMBLE LENGTH
RegPreambleMsb           =   0x20
RegPreambleLsb           =   0x21

#Spread Factor 6
RegDetectOptimize        =   0x31
RegDetectionThreshold    =   0x37

#Optimise the LoRa modulation (values of register)
DetectOptimize           =   0x05
DetectionThreshold       =   0x0C
ModemConfig2             =   0x64


def setLoRaMode():
    MODE_SLEEP()
    writeRegister(REG_OPMODE, 0x80)
    return "LoRa mode set"

def setMode(newMode):
#	if (newMode == currentMode)
    return


#Method:   Read Register
def readRegister(addr):
    print("readRegister", addr)
    select()
    to_send = [addr]
    #|spi.writebytes(to_send)
    #|regval=spi.readbytes(1)
    regval= 'ok'
    unselect()
    return regval


#Method:   Write Register
def writeRegister(addr, value):
    print("writeRegister", addr , 'value', value)
    select()
    #|spi.writebytes(addr)
    #|spi.writebytes(value)
    unselect()

#Method:   Select Transceiver
def select():
    print("high")
    #|GPIO.output(_slaveSelectPin, GPIO.HIGH)

#Method:   UNSelect Transceiver
def unselect():
    print("low")
    #|GPIO.output(_slaveSelectPin, GPIO.LOW)


#MODES
def MODE_RX_CONTINUOS():
    writeRegister(REG_PA_CONFIG, PA_OFF_BOOST)      #TURN PA OFF FOR RECIEVE??
    writeRegister(REG_LNA, LNA_MAX_GAIN)            #MAX GAIN FOR RECIEVE
    writeRegister(REG_OPMODE, RF92_MODE_RX_CONTINUOS)
    print("Changing to Receive Continous Mode")

def MODE_TX():
    writeRegister(REG_LNA, LNA_OFF_GAIN)            #TURN LNA OFF FOR TRANSMITT
    writeRegister(REG_PA_CONFIG, PA_MAX_BOOST)      #TURN PA TO MAX POWER
    writeRegister(REG_OPMODE, RF92_MODE_TX)
    print("Changing to Transmit Mode")

def MODE_SLEEP():
    writeRegister(REG_OPMODE, RF92_MODE_SLEEP)
    print("Changing to Sleep Mode")

def MODE_STANDBY():
    writeRegister(REG_OPMODE, RF92_MODE_STANDBY);
    print("Changing to Standby Mode");


spi = spidev.SpiDev()
#|spi.open(0,0)
time.sleep(3)


setLoRaMode()
#type(REG_IRQ_FLAGS)

#dato=readRegister(REG_IRQ_FLAGS)
#print(dato)

#writeRegister(REG_IRQ_FLAGS,REG_IRQ_FLAGS)

#MODE_SLEEP()
#MODE_RX_CONTINUOS()
#MODE_TX()
MODE_STANDBY()
reg_print=readRegister(REG_OPMODE)

#|GPIO.cleanup()  #devuelve los pines a su estado inicial
#|spi.close()
print(reg_print)
