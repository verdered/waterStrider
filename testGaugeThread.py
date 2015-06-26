#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         testGaugeThread.py
# Purpose:      Test Result Dialog in HtmlWindow
#
# Author:       dipl.eng.PhD Svilen Zlatev
#
# Created:      27-October-2014
# Copyright:    (c) 2013 by Pronix1 Ltd.
# Licence:      wxWindows license
#----------------------------------------------------------------------------
'''
Created on 27.10.2014

@author: svilen.zlatev
'''

from threading import *

class testAllNodes(Thread):
    def __init__(self, facilitymap_, nodesCount):
        Thread.__init__(self)
        self.sortAll = []
        self.start()
        self.status
        self.facilitymap_= facilitymap_
        self.nodesCount = nodesCount

        
    def run(self):
        """
        """
        currValue = 0
      
        for cell in self.facilitymap_:
            for phase in self.facilitymap_[cell]:
                for node in self.facilitymap_[cell][phase]:
                    longAddress = self.facilitymap_[cell][phase][node]

                    self.sortAll.append(self.Parent.testOneNode(cell, phase, node, longAddress))
                    currValue += 1
                    self.status = round((currValue/float(nodeCount))*100,0)
