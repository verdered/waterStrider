#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         interface.py
# Purpose:      Interface module for Sprinkler control system
#
# Author:       dipl.eng.PhD Svilen Zlatev
#
# Created:      01-August-2013
# Copyright:    (c) 2013 by Pronix1 Ltd.
# Licence:      wxWindows license
#----------------------------------------------------------------------------

__author__="svilen.zlatev"
__date__ ="$2013-8-25 11:47:08$"

import threading
import time
import os
import wx
import serial
# from serial.tools import list_ports
from xbee import XBee,ZigBee
# from threading import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    
import Queue

from pygame.time import delay

listOfNodes = []

ISCOMMANDINPROCESS = 0

def list_serial_ports():
    # Windows
    if os.name == 'nt':
        # Scan for available ports.
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append('COM'+str(i + 1))
                s.close()
            except serial.SerialException:
                pass
        return available
    else:
        # Mac / Linux
        return [port[0] for port in list_ports.comports()];
    

def isWindows():
    """
    Returns True if osName is Windows
    """
    if os.name == 'nt':
        return True
    else:
        return False

def isLinux():
    """
    Returns True if osName is Windows
    """
    if os.name == 'linux':
        return True
    else:
        return False    
    
def getComPortListXML():
    """
    Get COM ports information from XML
    """
    comList = []
    comDict = {}
    
    try:
        COMPORT_XML = ET.ElementTree(file = 'comport.xml')
        comRoot = COMPORT_XML.getroot()

        for comport in COMPORT_XML.iterfind('com'):
            comDict['name'] = comport.get('name')
            for prop in comport:
                comDict[prop.tag] = prop.text
            comList.append(comDict)
            comDict = {}
        return comList
    except:
        return []
    
def getActiveComPort():
    """
    Returns Active com port list of dictionaries with com port parameters
    """
    activeComPortList = []
    comPortList = getComPortListXML()  
    if comPortList:
        for comPort in comPortList:
            if comPort.get('active') == 'active':
                activeComPortList.append(comPort)
        return activeComPortList
    else:
        return []
#################################################################################


def node_discovery():
    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        count = 0
    
    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut)
        xbee = ZigBee(ser,escaped=True)
        node_list=[]        
        xbee.at(command='ND')
        response = {'':''}
        while response <> {}:
            response = xbee.wait_read_frame()
            if response:
                print response
                node_list.append(response)
            else:
                text = "Xbee: Timeout during node discovery operation!"
         
        print "Spisak: ", node_list # return []
        return node_list
    
    except serial.SerialException as ex:
        text = "Exception: " + ex.__str__()
        return text
    else:
        xbee.halt()
        ser.close()


def xbee_pin(xbeeRemAddr, xbeePin, xbeePinState):
    "Manipulate XBee pins. Input: xbeeRemAddr, xbeePin, xbeePinState. Ex: xbee_pin('0013A200406B5174'.decode('hex'),'D0','ON')"

    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        count = 0
        
    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut) 
        xbee = ZigBee(ser,escaped=True)
        
        if xbeePinState == 'ON':
            xbeePinStateHex = '\x05'

        if xbeePinState == 'OFF':
            xbeePinStateHex = '\x04'
            
        try:
            xbee.remote_at(dest_addr_long=xbeeRemAddr,command=xbeePin,parameter=xbeePinStateHex)
        finally:
            return 1
    
    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        return 0
    else:
        xbee.halt()
        ser.close()
        
       
def xbee_is(xbeeRemAddr):
    """
    XBee IS command implementation. Input: xbeeRemAddr. Ex: xbee_is('0013A200406B5174')
    """
    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        count = 0

    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut) 
        xbee = ZigBee(ser,escaped=True)
        
        xbee.remote_at(dest_addr_long=xbeeRemAddr,command="IS",frame_id="C")
        response = xbee.wait_read_frame()
        return response
    
    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        return 0
    else:
        xbee.halt()
        ser.close()    
        
def xbee_hv(xbeeRemAddr):
    """
    XBee HV command implementation. Input: xbeeRemAddr. Ex: xbee_is('0013A200406B5174')
    """
    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        count = 0

    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut) 
        xbee = ZigBee(ser,escaped=True)
        
        xbee.remote_at(dest_addr_long=xbeeRemAddr,command="HV",frame_id="C")
        response = xbee.wait_read_frame()
        return response
    
    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        return 0
    else:
        xbee.halt()
        ser.close()        

def xbee_vr(xbeeRemAddr):
    """
    XBee VR command implementation. Input: xbeeRemAddr. Ex: xbee_is('0013A200406B5174')
    """
    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        count = 0

    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut) 
        xbee = ZigBee(ser,escaped=True)
        
        xbee.remote_at(dest_addr_long=xbeeRemAddr,command="VR",frame_id="C")
        response = xbee.wait_read_frame()
        return response
    
    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        return 0
    else:
        xbee.halt()
        ser.close()
        
def xbee_tp(xbeeRemAddr):
    """
    XBee TP command implementation. Input: xbeeRemAddr. Ex: xbee_is('0013A200406B5174')
    """
    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        count = 0

    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut) 
        xbee = ZigBee(ser,escaped=True)
        
        xbee.remote_at(dest_addr_long=xbeeRemAddr,command="TP",frame_id="C")
        response = xbee.wait_read_frame()
        return response
    
    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        return 0
    else:
        xbee.halt()
        ser.close() 

################################################################################        
######################### Threaded #############################################
################################################################################
        
def hiddenNodediscovery():
    
    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        
    print "Hidden Discovery"
    
    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut)
        print "porta e otworen", ser.isOpen() 
        xbee = ZigBee(ser,escaped=True)
        xbee.at(command='ND')
        response = {'':''}
        while response <> {}:
            response = xbee.wait_read_frame()
            if response:
                print response
            else:
                text = "Xbee: Timeout during node discovery operation!"
                response = {}
                print text

    
    except serial.SerialException as ex:
        text = "Exception: " + ex.__str__()
        return text
    else:
        ser.close()
        
#===============================================================================
# hiddenXbeePin
#===============================================================================
def hiddenXbeePin(xbeeRemAddr, xbeePin, xbeePinState):
    "Manipulate XBee pins. Input: xbeeRemAddr, xbeePin, xbeePinState. Ex: xbee_pin('0013A200406B5174'.decode('hex'),'D0','ON')"

    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        count = 0
        
    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut) 
        xbee = ZigBee(ser,escaped=True)
        
        if xbeePinState == 'ON':
            xbeePinStateHex = '\x05'

        if xbeePinState == 'OFF':
            xbeePinStateHex = '\x04'
            
        try:
            xbee.remote_at(dest_addr_long=xbeeRemAddr,command=xbeePin,parameter=xbeePinStateHex)
        finally:
            return 1
    
    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        return 0
    else:
        xbee.halt()
        ser.close()
        
       
#===============================================================================
# hiddenXbeeIs IT'S WORKING!!!
#===============================================================================
def hiddenXbeeChangeState(xbeeRemAddr, xbeePin, xbeePinState): 
    """
    XBee IS command implementation. Input: xbeeRemAddr. Ex: state = hiddenXbeeIs('0013A200406B5174', 'D0')
    Returns: state = True/False
    """
    startTime = time.time()
    i = 0
    transit = 3
    timeOut = 0.3
    retValue = False
    
    comPortList = getActiveComPort()
    if comPortList:
        comPort = comPortList[0].get('name')
        timeOut = int(comPortList[0].get('timeout'))
        baudRate = int(comPortList[0].get('baudrate'))
        
    try:
        ser = serial.Serial(comPort, baudRate, timeout=timeOut)
        xbee = ZigBee(ser,escaped=True)
        
        if xbeePinState == 'ON':
            xbeePinStateHex = '\x05'

        if xbeePinState == 'OFF':
            xbeePinStateHex = '\x04'
            
        while(i < transit):        
            try:
                xbee.remote_at(dest_addr_long=xbeeRemAddr.decode('hex'),command=xbeePin,parameter=xbeePinStateHex)
                resp = xbee.wait_read_frame(250)
                print "Otgowor sleed komanda: ", resp
            except ValueError:
                print "ValueError 1"
                retValue = 1
            except TypeError:
                print "TypeError 1"
                retValue = 2
        
            delay(200) #Wait 250ms for network healing
        
            try:
                xbee.remote_at(dest_addr_long=xbeeRemAddr.decode('hex'),command="IS",frame_id="C")
                response = xbee.wait_read_frame(250)
                print "Otgowor sled ATIS: ", response
                #===============================================================
                # try: Tuka tryabwa da analiziram kljucha 'samples'
                #===============================================================
                try:
                    sample = response.get('samples',[])
                    print "Sample", sample
                except KeyError:
                    retValue = 9
                parametersValue = response.get('parameter', [])
                
                try:
                    print "DIO 0: ", parametersValue[0].get('dio-0')
                    if parametersValue[0].get('dio-0') == True:
                        retValue = 3
                        i = 10
                    else:
                        retValue = 4
                        i = 10
                except IndexError:
                    retValue = 10   # No key to get list parameter
                    
            except ValueError:
                print "ValueError 2: ", response
                retValue = 5
            except TypeError:
                print "TypeError 2"
                retValue = 6
            except KeyError:
                print "KeyError 1"
                retValue = 7
            i = i+1
            print "i = ", i

    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        retValue = 8
    else:
        xbee.halt()
        ser.close()
        print time.time()-startTime
############ Tryabwa da go dopisha!!! za obrabotka na !!!
        return retValue
