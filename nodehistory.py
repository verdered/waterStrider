#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 26.08.2014

@author: svilen.zlatev
'''

import time
import datetime

try:
    import xml.etree.cElementTree as HT
except ImportError:
    import xml.etree.ElementTree as HT
    
NODE_HISTORY_XML = HT.ElementTree(file = 'nodes_history.xml')

def getNHEvents(cell, phase, node):
    """
        Returns dictionary with ts:text
    """
    global NODE_HISTORY_XML
    
    events_dict = {}
    
    for nodes in NODE_HISTORY_XML.findall('node'):
        if nodes.get('cell') == cell and nodes.get('phase') == phase and nodes.get('name') == node:
            for event in nodes.findall('event'):
                events_dict[event.get('timestamp')] = event.text
    
    return events_dict

def getNHVersion(cell, phase, node):
    """
    """
    global NODE_HISTORY_XML
    
    version = ''
    
    for nodes in NODE_HISTORY_XML.findall('node'):
        if nodes.get('cell') == cell and nodes.get('phase') == phase and nodes.get('name') == node:
            version = nodes.get('ver')
    
    return version

def getNHName(cell, phase, node):
    """
    """
    global NODE_HISTORY_XML
    
    version = ''
    
    for nodes in NODE_HISTORY_XML.findall('node'):
        if nodes.get('cell') == cell and nodes.get('phase') == phase and nodes.get('name') == node:
            version = nodes.get('sp')
    
    return version

                
def addEvent(cell, phase, node, text):
    """
    """
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    for nodes in NODE_HISTORY_XML.findall('node'):
        if nodes.get('cell') == cell and nodes.get('phase') == phase and nodes.get('name') == node:
                node_new=HT.SubElement(nodes, 'event')
                node_new.set('timestamp',st)
                node_new.text = text
                
    NODE_HISTORY_XML.write('nodes_history.xml',encoding='UTF-8')
    
def updateVersion(cell, phase, node, version):
    """
    """
    
    for nodes in NODE_HISTORY_XML.findall('node'):
        if nodes.get('cell') == cell and nodes.get('phase') == phase and nodes.get('name') == node:
                nodes.set('ver',version)
                
    NODE_HISTORY_XML.write('nodes_history.xml',encoding='UTF-8')
    
def updateName(cell, phase, node, name_sp):
    """
    """
    
    for nodes in NODE_HISTORY_XML.findall('node'):
        if nodes.get('cell') == cell and nodes.get('phase') == phase and nodes.get('name') == node:
                nodes.set('sp',name_sp)
                
    NODE_HISTORY_XML.write('nodes_history.xml',encoding='UTF-8')    
    
                
                
                
                