#!/usr/bin/env python
# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

'''
Created on 13.07.2015

@author: svilen.zlatev
'''
import wxversion
wxversion.select('2.8-gtk2-unicode')
import wx

###########################################################################
## Class stopAllDlg
###########################################################################

class stopAllDlg ( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Stop All", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.CAPTION|wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP )
        
        self.SetSizeHintsSz( wx.Size( 400,250 ), wx.DefaultSize )
        
        stopAllCommonSizer = wx.BoxSizer( wx.VERTICAL )
        
        stopAllCommonSizer.SetMinSize( wx.Size( 400,250 ) ) 
        self.stopAllLabel = wx.StaticText( self, wx.ID_ANY, u"Stopping in progress...", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stopAllLabel.Wrap( -1 )
        stopAllCommonSizer.Add( self.stopAllLabel, 0, wx.ALL, 5 )
        
        stopAllBoxSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Cell 1" ), wx.VERTICAL )
        
        stopAllBoxSizer1.SetMinSize( wx.Size( 370,-1 ) ) 
        self.stopAllLabelCell1 = wx.StaticText( self, wx.ID_ANY, u"%", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stopAllLabelCell1.Wrap( -1 )
        stopAllBoxSizer1.Add( self.stopAllLabelCell1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        self.stopAllGaugeCell1 = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size( 370,-1 ), wx.GA_HORIZONTAL )
        self.stopAllGaugeCell1.SetValue( 0 ) 
        self.stopAllGaugeCell1.SetMinSize( wx.Size( 380,-1 ) )
        
        stopAllBoxSizer1.Add( self.stopAllGaugeCell1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        
        stopAllCommonSizer.Add( stopAllBoxSizer1, 1, wx.EXPAND, 3 )
        
        stopAllBoxSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Cell 2" ), wx.VERTICAL )
        
        self.stopAllLabelCell2 = wx.StaticText( self, wx.ID_ANY, u"%", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stopAllLabelCell2.Wrap( -1 )
        stopAllBoxSizer2.Add( self.stopAllLabelCell2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        self.stopAllGaugeCell2 = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size( 370,-1 ), wx.GA_HORIZONTAL )
        self.stopAllGaugeCell2.SetValue( 0 ) 
        self.stopAllGaugeCell2.SetMinSize( wx.Size( 380,-1 ) )
        
        stopAllBoxSizer2.Add( self.stopAllGaugeCell2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        
        stopAllCommonSizer.Add( stopAllBoxSizer2, 1, wx.EXPAND, 5 )
        
        
        self.SetSizer( stopAllCommonSizer )
        self.Layout()
        stopAllCommonSizer.Fit( self )
        
        self.Centre( wx.BOTH )
    
    def __del__( self ):
        pass
