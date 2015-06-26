#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         ledCtrlDlg.py
# Purpose:      LED control
#
# Author:       dipl.eng.PhD Svilen Zlatev
#
# Created:      15-November-2014
# Copyright:    (c) 2013 by Pronix1 Ltd.
# Licence:      wxWindows license
#----------------------------------------------------------------------------
'''
Created on 15.11.2014

@author: merinid
'''

import wx
from wx.lib.masked import TimeCtrl

class ledCtrlTimePanel ( wx.Panel ):
    '''
        Контрол на старт/стоп на LED на спринклерите
    '''
    
    def __init__( self, parent ):
        wx.Panel.__init__(self, parent)
                        
        wxID_RBOXMODE = wx.NewId()
        wxID_LEDSAVE = wx.NewId()
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        self.ledCtrlDlgMainSz = wx.BoxSizer( wx.VERTICAL )
        
        self.ledCtrlTimeSz = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u" LED контрол " ), wx.HORIZONTAL )
        
        ledRButModeChoices = [ u"Ръчен", u"Автоматичен"]
        self.ledRButMode = wx.RadioBox(self, wxID_RBOXMODE, u"Режим на работа", wx.DefaultPosition, wx.DefaultSize, ledRButModeChoices, 1, wx.RA_SPECIFY_COLS)
        self.ledRButMode.SetSelection( 0 )
        self.ledCtrlTimeSz.Add( self.ledRButMode, 0, wx.ALL, 5 )
        self.ledRButMode.Bind(wx.EVT_RADIOBOX, self.OnRBoxChange, id = wxID_RBOXMODE)                
        
        self.textTimePickerStart = wx.StaticText( self, -1, u"Включване в:", size=(80,-1))      
        self.timePickerStart = TimeCtrl(self, id = -1,
                                    value = '00:00:00',
                                    pos = wx.DefaultPosition,
                                    size = (65,-1),
                                    style = wx.TE_PROCESS_TAB,
                                    validator = wx.DefaultValidator,
                                    name = "time",
                                    format = '24HHMM',
                                    fmt24hr = False,
                                    displaySeconds = False,
                                    spinButton = None,
                                    min = None,
                                    max = None,
                                    limited = None,
                                    oob_color = "Yellow"
                                    )
        h = self.timePickerStart.GetSize().height
        self.spinTimePickerStart = wx.SpinButton( self, -1, wx.DefaultPosition, (-1,h), wx.SP_VERTICAL )
        self.timePickerStart.BindSpinButton( self.spinTimePickerStart )
        self.addWidgets([self.textTimePickerStart, self.timePickerStart, self.spinTimePickerStart])
        
        self.textTimePickerStop = wx.StaticText( self, -1, u"Изключване в:", size=(85,-1))      
        self.timePickerStop = TimeCtrl(self, id = -1,
                                    value = '00:00:00',
                                    pos = wx.DefaultPosition,
                                    size = (65,-1),
                                    style = wx.TE_PROCESS_TAB,
                                    validator = wx.DefaultValidator,
                                    name = "time",
                                    format = '24HHMM',
                                    fmt24hr = False,
                                    displaySeconds = False,
                                    spinButton = None,
                                    min = None,
                                    max = None,
                                    limited = None,
                                    oob_color = "Yellow"
                                    )
        h = self.timePickerStop.GetSize().height
        self.spinTimePickerStop= wx.SpinButton( self, -1, wx.DefaultPosition, (-1,h), wx.SP_VERTICAL )
        self.timePickerStop.BindSpinButton( self.spinTimePickerStop )
        self.addWidgets([self.textTimePickerStop, self.timePickerStop, self.spinTimePickerStop])
        
        self.ledCtrlTimeSz.AddSpacer( ( 0, 0), 1, wx.ALL, 5 )
        
        self.ledButtonSave = wx.Button( self, wxID_LEDSAVE, u"Запазване", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.addWidgets([self.ledButtonSave])

        self.ledCtrlDlgMainSz.Add( self.ledCtrlTimeSz, 1, wx.EXPAND, 5 )
       
        self.ledCtrlDlgMainSz.AddSpacer( ( 0, 0), 1, wx.ALL, 5 )
        
        self.timePickerStart.Disable()
        self.textTimePickerStart.Disable()
        self.spinTimePickerStart.Disable()
        self.timePickerStop.Disable()
        self.textTimePickerStop.Disable()
        self.spinTimePickerStop.Disable()
        self.ledButtonSave.Disable()

        self.SetSizer( self.ledCtrlDlgMainSz )
        self.Layout()
        
        self.Centre( wx.BOTH )
        
    
    def __del__( self ):
        pass
    
    def addWidgets(self, widgets):
        """
        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for widget in widgets:
            if isinstance(widget, wx.StaticText):
                sizer.Add(widget, 0, wx.ALL|wx.CENTER, 5),
            else:
                sizer.Add(widget, 0, wx.ALL, 5)
        self.ledCtrlTimeSz.Add(sizer)
        
    def OnRBoxChange(self, event):
        """
        """
        
        if self.ledRButMode.GetSelection() == 1:
            self.timePickerStart.Enable()
            self.textTimePickerStart.Enable()
            self.spinTimePickerStart.Enable()
            self.timePickerStop.Enable()
            self.textTimePickerStop.Enable()
            self.spinTimePickerStop.Enable()
            self.ledButtonSave.Enable()
        
        if self.ledRButMode.GetSelection() == 0:
            self.timePickerStart.Disable()
            self.textTimePickerStart.Disable()
            self.spinTimePickerStart.Disable()
            self.timePickerStop.Disable()
            self.textTimePickerStop.Disable()
            self.spinTimePickerStop.Disable()
            self.ledButtonSave.Disable()
        