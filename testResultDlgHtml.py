#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         testResultDlgHtml.py
# Purpose:      Test Result Dialog in HtmlWindow
#
# Author:       dipl.eng.PhD Svilen Zlatev
#
# Created:      22-October-2014
# Copyright:    (c) 2013 by Pronix1 Ltd.
# Licence:      wxWindows license
#----------------------------------------------------------------------------
'''
Created on 22.10.2014

@author: svilen.zlatev
'''
import wxversion
wxversion.select('2.8-gtk2-unicode')
import wx
import wx.html
import os
import time
import datetime
from operator import itemgetter
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
from wx.html import HtmlEasyPrinting

###########################################################################
## Class testResultDlg
###########################################################################

header_part1 = '''
        <html>
          <head>
            <title>Резултати от тест на Xbee управления</title>
            <meta http-equiv="content-type" content="text/html;charset=utf-8">
          </head>
          <body>
            <H3>Резултати от тест на Xbee управления за: </H3> '''

header_part2 = '''
            <table border="1">
            <tr><th bgcolor=#acc8cc><font face="Arial">Клетка:</font></th>
            <th bgcolor=#acc8cc><font face="Arial">Фаза:</font></th><th bgcolor=#acc8cc>Водно оръдие:</font></th>
            <th bgcolor=#acc8cc><font face="Arial">Адрес на у-то</font></th><th bgcolor=#acc8cc><font face="Arial">Откриваемост:</font></th>
            <th bgcolor=#acc8cc><font face="Arial">Съст.клапан</font></th><th bgcolor=#acc8cc><font face="Arial">Съст.LED</font></th>
            <th bgcolor=#acc8cc><font face="Arial">Съст.обр.вр.</font></th><th bgcolor=#acc8cc><font face="Arial">Напрежение Ub,[V]</font></th></tr>
'''
        
footer = '''
            </table>
            <p><small>Автоматично генерирана таблица от ACSC </small></p>
          </body>
        </html>
'''

class testResultDlgHtml ( wx.Dialog ):
    
    def __init__( self, parent, resultList, isAllStopped ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Резултати от теста", pos = wx.DefaultPosition, size = wx.Size( 770,600 ), style = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP )
        
        self.resultPath = "./testresults/"
        self.isAllStopped = isAllStopped
        
        pub.subscribe(self.showTestGauge, ("show.testGauge"))
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        testSbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"" ), wx.VERTICAL )
        
        testFilterSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"" ), wx.HORIZONTAL )
        
        self.testButtonMake = wx.Button( self, wx.ID_ANY, u"Направи нов тест сега!", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.testButtonMake.SetToolTipString( u"сканира управленията и генерира рапорт със сътоянието им" )
        testFilterSizer.Add( self.testButtonMake, 0, wx.ALL, 5 )
        
        
        testFilterSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        
        self.testStaticTextFile = wx.StaticText( self, wx.ID_ANY, u"Файлове с резултати: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.testStaticTextFile.Wrap( -1 )
        testFilterSizer.Add( self.testStaticTextFile, 0, wx.ALL, 5 )
        
        testCboxFileChoices = []
        self.testCboxFile = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, testCboxFileChoices,  wx.CB_SORT|wx.VSCROLL  )
        testFilterSizer.Add( self.testCboxFile, 0, wx.ALL, 5 )
        
        self.testStaticLineFile = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        testFilterSizer.Add( self.testStaticLineFile, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.testButtonShow = wx.Button( self, wx.ID_ANY, u"Покажи резултати", wx.DefaultPosition, wx.DefaultSize, 0 )
        testFilterSizer.Add( self.testButtonShow, 0, wx.ALL, 5 )
        
        
        testSbSizer.Add( testFilterSizer, 1, wx.EXPAND, 5 )
        
        self.testDlghtmlWin = wx.html.HtmlWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 750,400 ), wx.html.HW_SCROLLBAR_AUTO )
        self.testDlghtmlWin.SetToolTipString( u"показва резултатите от теста в табличен вид" )
        
        testSbSizer.Add( self.testDlghtmlWin, 0, wx.ALL, 5 )
        
        testSizerGaugeTest = wx.BoxSizer( wx.HORIZONTAL )
        
        self.testStaticTextGauge = wx.StaticText( self, wx.ID_ANY, u"Прогрес на теста:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.testStaticTextGauge.Wrap( -1 )
        testSizerGaugeTest.Add( self.testStaticTextGauge, 0, wx.ALL, 5 )
        
        self.testGaugeTest = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.testGaugeTest.SetValue( 0 ) 
        self.testGaugeTest.SetToolTipString( u"показва прогреса на теста" )
        self.testGaugeTest.SetMinSize( wx.Size( 600,-1 ) )
        
        testSizerGaugeTest.Add( self.testGaugeTest, 0, wx.ALL, 5 )
        
        testSbSizer.Add( testSizerGaugeTest, 0, wx.EXPAND, 5 )
        
        testSizerButtonClose = wx.BoxSizer( wx.HORIZONTAL )
        
        
        testSizerButtonClose.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        
        self.testButtonClose = wx.Button( self, wx.ID_CLOSE, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.testButtonClose.SetToolTipString( u"натиснете ОК, за да затворите прозореца" )
        self.testButtonPrint = wx.Button( self, wx.ID_PRINT, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.testButtonClose.SetToolTipString( u"печата изведената таблица" )        
        testSizerButtonClose.Add( self.testButtonClose, 0, wx.ALL, 5 )
        testSizerButtonClose.Add( self.testButtonPrint, 0, wx.ALL, 5 )
        
        testSizerButtonClose.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        
        
        testSbSizer.Add( testSizerButtonClose, 1, wx.EXPAND, 5 )
        
#         self.html_printer=Printer()
#         self.html_print=HtmlEasyPrinting(name="Printing", parentWindow=self.TextCtrl)
        
        self.SetSizer( testSbSizer )
        self.Layout()
        
        self.Centre( wx.BOTH )
        
        self.testGaugeTest.Show(False)
        self.testStaticTextGauge.Show(False)

        self.testButtonClose.Bind(wx.EVT_BUTTON, self.OnButtonClosePressed)
        self.testButtonShow.Bind(wx.EVT_BUTTON, self.OnButtonShowPressed)
        self.testButtonMake.Bind(wx.EVT_BUTTON, self.OnButtonMakePressed)
        
        self.loadCboxFiles()
        
        self.testButtonPrint.Hide()
        
    def showTestGauge(self, state):
        """
        """
        testGaugeCurrValue = round((float(state[0])/float(state[1]))*100,0)
        self.testGaugeTest.SetValue(testGaugeCurrValue)
        
        
    def transferListToHtml(self, sequence):
        """
        """
        body = ''
        sortedSequence = sorted(sequence, key=itemgetter(0, 1, 2))
                
        for littleList in sortedSequence:
            try:
                if littleList[4] == 'не е намерено':  
                    body = body + '''<tr bgcolor=#F80000><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                <td>%s</td></tr>''' %(littleList[0], littleList[1], littleList[2], littleList[3],
                                                      littleList[4], littleList[5], littleList[6], littleList[7], 
                                                      littleList[8])
            except IndexError:
                    body = body + '''<tr bgcolor=#FFFFFF><td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td></tr>'''
            
            try:
                if littleList[4] == 'намерено':  
                    body = body + '''<tr bgcolor=#00F800><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                <td>%s</td></tr>''' %(littleList[0], littleList[1], littleList[2], littleList[3],
                                                      littleList[4], littleList[5], littleList[6], littleList[7], 
                                                      littleList[8])
            except IndexError:
                    body = body + '''<tr bgcolor=#FFFFFF><td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td></tr>'''
            except UnicodeDecodeError:
                    body = body + '''<tr bgcolor=#FFFFFF><td>UDE</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td></tr>'''
            
            try: 
                if littleList[4] == 'няма монтирано управление!':  
                    body = body + '''<tr bgcolor=#FFFF33><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                                <td>%s</td></tr>''' %(littleList[0], littleList[1], littleList[2], littleList[3],
                                                      littleList[4], littleList[5], littleList[6], littleList[7], 
                                                      littleList[8])
            except IndexError:
                    body = body + '''<tr bgcolor=#FFFFFF><td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td></tr>'''
            except UnicodeDecodeError:
                    body = body + '''<tr bgcolor=#FFFFFF><td>UDE</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td><td>N/A</td><td>N/A</td><td>N/A</td>
                                <td>N/A</td></tr>'''
            
                            
        return body 
        
    def htmlDecode(self, fileName):
        """
        """
        
        f_name = os.path.join(self.resultPath+fileName)
        with open(f_name, "r+") as f:
            page = f.read()
            
        page = page.decode('utf-8')
        f.close()
        return page
        
    def loadCboxFiles(self):
        """
        """
        self.testCboxFile.Clear()
        self.testCboxFile.AppendItems(sorted(os.listdir(self.resultPath)))
        
    def testNodes(self):
        """
        """
        facilityMap_ = self.Parent.buildFacilityMap_()
        sortAll = []
        currValue = 0
        nodeCount = self.Parent.countAllNodes()
        
        for cell in facilityMap_:
            for phase in facilityMap_[cell]:
                for node in facilityMap_[cell][phase]:
                    longAddress = facilityMap_[cell][phase][node]

                    sortAll.append(self.Parent.testOneNode(cell, phase, node, longAddress))
                    currValue += 1
                    self.testGaugeTest.SetValue(round((currValue/float(nodeCount))*100,0))

        return sortAll

    def __del__( self ):
        pass
    
    def OnPrint(self, event):
        """
        """

    
    def OnButtonMakePressed(self, event):
        """
        """
        
        if self.isAllStopped == 1:
            resultYesNoDlg = wx.MessageDialog(self,"Тестът на всички управления изисква много време! Съгласни ли сте да продължите?", 'ASCS съобщение', wx.YES_NO)
            resultYesNo = resultYesNoDlg.ShowModal()
            resultYesNoDlg.Destroy()
            
            if resultYesNo == wx.ID_YES:
                msg = "Моля, почакайте извършва се тест на всички управления..."
                old_style = self.GetWindowStyle()
                self.SetWindowStyle(old_style | wx.STAY_ON_TOP)
                busyDlg = wx.BusyInfo(msg, self)
                self.Parent.SCS_Frame_statusbar.SetStatusText("Протича тест на всички управления...",0)
                body = self.transferListToHtml(self.Parent.testAllNodes())
            
                self.Parent.SCS_Frame_statusbar.SetStatusText("",0)
                busyDlg = None

                self.SetWindowStyle(old_style)
               
                self.testDlghtmlWin.SetPage("")
        
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                fileHtmlName = os.path.join(self.resultPath+"Test_"+st)
                fileHtml = open(fileHtmlName,"w+")
                stHtml = '<H3>%s</H3>' %st
                fileHtml.write(header_part1 + stHtml)
                fileHtml.write(header_part2)
                fileHtml.write(body)
                fileHtml.write(footer)
                fileHtml.close()
                self.loadCboxFiles()
       
                try:
                    self.testDlghtmlWin.SetStandardFonts()
                    self.testDlghtmlWin.SetPage(self.htmlDecode("Test_"+st))
                except IOError:
                    pass
            else:
                pass
        else:
            msgDlg = wx.MessageDialog(self, "Моля, спрете всички управления преди да направите тест!", 'ASCS съобщение', 
                                   wx.OK | wx.ICON_INFORMATION)
            msgDlg.ShowModal()
            msgDlg.Destroy()
            
    def OnButtonClosePressed(self, event):
        """
        """
        self.loadCboxFiles()
        self.Destroy()
        
    def OnButtonShowPressed(self, event):
        
        if self.testCboxFile.GetValue():
            self.testDlghtmlWin.SetStandardFonts()
            self.testDlghtmlWin.SetPage(self.htmlDecode(self.testCboxFile.GetValue()))
            
    def ifBusy(self, state):
        self.Hide()
        msg = "Please wait while we process your request..."
        if state == True:
            busyDlg = wx.BusyInfo(msg)
        else:
            busyDlg = None
        self.Show()
        
