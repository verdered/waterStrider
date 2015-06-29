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
import threading
import time

from pygame.time import delay
__author__="svilen.zlatev"
__date__ ="$2013-8-25 11:47:08$"


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
        ser.close() 
        
######################### Threaded #############################################
        
def hiddenNodediscovery(q):
    
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
                print text
         
        print "Spisak: ", node_list # return []
        q.put(node_list)
    
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
        ser.close()
        
       
#===============================================================================
# hiddenXbeeIs
#===============================================================================
def hiddenXbeeChangeState(xbeeRemAddr, xbeePin, xbeePinState): 
    """
    XBee IS command implementation. Input: xbeeRemAddr. Ex: state = hiddenXbeeIs('0013A200406B5174', 'D0')
    Returns: state = True/False
    """
    startTime = time.time()
    i = 0
    timeOut = 3
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
            
        while(i < 3 or startTime-time.time()>timeOut):        
            try:
                xbee.remote_at(dest_addr_long=xbeeRemAddr.decode('hex'),command=xbeePin,parameter=xbeePinStateHex)
                retValue = True
            except ValueError:
                print "ValueError 1"
                retValue = False
            except TypeError:
                print "TypeError 1"
                retValue = False
        
            delay(250) # Wait 250ms for network healing
        
            try:
                xbee.remote_at(dest_addr_long=xbeeRemAddr.decode('hex'),command="IS",frame_id="C")
                response = xbee.wait_read_frame(250)
                print "Otgowor", response
                parametersValue = response.get('parameter', {})
                if parametersValue <> {}:
                    print "DIO 0: ", parametersValue[0].get('dio-0')
                retValue = True
            except ValueError:
                print "ValueError 2"
                retValue = False
            except TypeError:
                print "TypeError 2"
                retValue = False
            i = i+1
            print "i = ", i

    except serial.SerialException as ex:
        text = "Exception is: " + ex.__str__()
        retValue = False
    else:
        ser.close()
        print time.time()-startTime
############ Tryabwa da go dopisha!!! za obrabotka na !!!
        return retValue
    
