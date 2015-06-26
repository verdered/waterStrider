#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         scs.py
# Purpose:      Main module for Sprinkler control system
#
# Author:       dipl.eng.PhD Svilen Zlatev
#
# Created:      01-August-2013
# Copyright:    (c) 2013 by Pronix1 Ltd.
# Licence:      GNU Public License; wxWindows license
# print s1[s1.index(s2) + len(s2):]
#----------------------------------------------------------------------------

"""
This module will load and run GUI of Sprinkler control system """

from interface import *
import fcntl, sys

__version__ = "0.8.7"

class SCS_App(wx.App):
    def OnInit(self):
        global __version__
        print wxversion.getInstalled()
        wx.InitAllImageHandlers()
        theMainFraim = SCS_MainFrame(None, wx.ID_ANY, "ASCS ver.:%s" %__version__)
        self.SetTopWindow(theMainFraim)
        theMainFraim.Show()
        theMainFraim.Maximize()
        return True
    
if __name__ == '__main__':
    pid_file = 'scs.pid'
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print "Startirano!!!"
        sys.exit(0)
    app = SCS_App(0)
    app.MainLoop()