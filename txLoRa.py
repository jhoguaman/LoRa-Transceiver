#!/usr/bin/python
# -*- coding: utf-8 -*-
import spidev
import RPi.GPIO as GPIO
import time

_slaveSelectPin = 17        #SPI Chip select input
payload="0123ABCDEF"

#establecemos el sistema de numeracion que queramos, en mi caso BCM
GPIO.setmode(GPIO.BCM)

#configuramos el pin GPIO17 como una salida
GPIO.setup(_slaveSelectPin, GPIO.OUT)


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
    return print("LoRa mode set")

#Method:   Read Register
def readRegister(addr):
    print("readRegister", hex(addr))
    to_send = (addr & 0x7F)
    select()
    spi.xfer2([to_send])
    regval=spi.readbytes(1)
    unselect()
    return regval

#Method:   Write Register
def writeRegister(addr, value):
    print("writeRegister", hex(addr) , 'value to write', hex(value))
    addr=(addr | 0x80)
    config=[addr , value]
    select()
    spi.xfer2(config)
    unselect()

#Method:   Select Transceiver
def select():
    GPIO.output(_slaveSelectPin, GPIO.LOW)

#Method:   UNSelect Transceiver
def unselect():
    GPIO.output(_slaveSelectPin, GPIO.HIGH)


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
    writeRegister(REG_OPMODE, RF92_MODE_STANDBY)
    print("Changing to Standby Mode")



#Method:   Setup to receive continuously
def startReceiving():
    MODE_STANDBY()
    time.sleep(.1)
    #Turn on implicit header mode and set payload length
    writeRegister(REG_MODEM_CONFIG, IMPLICIT_MODE)
    writeRegister(REG_PAYLOAD_LENGTH, PAYLOAD_LENGTH)
    writeRegister(REG_HOP_PERIOD, 0xFF)
    RegFifoRxBaseAd = readRegister(REG_FIFO_RX_BASE_AD)     #RegFifoRxBaseAddr indicates the point in the data buffer where information will be written to in event of a receive operation
    writeRegister(REG_FIFO_ADDR_PTR, RegFifoRxBaseAd[0])
    #Preamble config
    writeRegister(RegPreambleMsb, 0x00)
    writeRegister(RegPreambleLsb, 0x0C)
    #Optimese the LoRa modulation
    writeRegister(REG_MODEM_CONFIG2, ModemConfig2)
    writeRegister(RegDetectOptimize, DetectOptimize)
    writeRegister(RegDetectionThreshold, DetectionThreshold)
    #Setup Receive Continous Mode
    MODE_RX_CONTINUOS()
    time.sleep(.1)

#Method:   Receive FROM BUFFER
def receiveMessage():
    currentAddr = readRegister(REG_FIFO_RX_CURRENT_ADDR)
    receivedCount = readRegister(REG_RX_NB_BYTES)
    print("Packet! RX Current Addr: ", hex(currentAddr[0]))
    print("Number of bytes received: ", hex(receivedCount[0]))
    writeRegister(REG_FIFO_ADDR_PTR, currentAddr)
    #now loop over the fifo getting the data
    i=0
    message = [None]*receivedCount[0]
    while (i < receivedCount[0]):
        message[i] = readRegister(REG_FIFO)
        i=i+1
    return message


#Method:   Send TO BUFFER
def sendData(buffer):
    print("Sending: ")
    print(buffer)
    MODE_STANDBY()

    writeRegister(REG_FIFO_TX_BASE_AD, 0x00)    # Update the address ptr to the current tx base address
    writeRegister(REG_FIFO_ADDR_PTR, 0x00)

    addr=(REG_FIFO | 0x80)
    i=0
    listLen=(len(buffer)+1)
    listBuffer=[None]*listLen
    listBuffer[0]=addr
    while (i < len(buffer)):
        listBuffer[i+1]=buffer[i]
        i=i+1

    select()
    spi.xfer2(listBuffer)
    unselect()

    #go into transmit mode
    MODE_TX()
    print("sending")
    x = readRegister(REG_IRQ_FLAGS)
    #once TxDone has flipped, everything has been sent
    while ((x[0] & 0x08) == 0x00):
        print(".")
    print(" done sending!")
    #clear the flags 0x08 is the TxDone flag
    writeRegister(REG_IRQ_FLAGS, 0x08)


#Init Setup
spi = spidev.SpiDev()
spi.open(0,1)
time.sleep(3)

setLoRaMode()

#Turn on implicit header mode and set payload length
writeRegister(REG_MODEM_CONFIG, IMPLICIT_MODE)
writeRegister(REG_PAYLOAD_LENGTH, PAYLOAD_LENGTH)
#Change the DIO mapping to 01 so we can listen for TxDone on the interrupt
writeRegister(REG_DIO_MAPPING_1, 0x40)
writeRegister(REG_DIO_MAPPING_2, 0x00)

#Go to standby mode
MODE_STANDBY()
#Preamble config
writeRegister(RegPreambleMsb, 0x00)
writeRegister(RegPreambleLsb, 0x0C)
#Optimese the LoRa modulation
writeRegister(REG_MODEM_CONFIG2, ModemConfig2)
writeRegister(RegDetectOptimize, DetectOptimize)
writeRegister(RegDetectionThreshold, DetectionThreshold)
#startReceiving()
print("Setup Complete")

while True:
    sendData(payload)
    time.sleep(10)


reg_print=readRegister(REG_OPMODE)

GPIO.cleanup()  #devuelve los pines a su estado inicial
spi.close()

print(format(reg_print[0], '02x'))
