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

""" This is GUI for ASCS """
""" Git """

import wxversion
wxversion.select('2.8-gtk2-unicode')
import wx
import icons
from sprinklercomm import *
import platform
import threading

try:
    from pubsub import setupkwargs
except ImportError:
    from wx.lib.pubsub import setupkwargs
try:
    from pubsub import pub
except ImportError:
    from wx.lib.pubsub import pub
    
import nodehistory as NH
from testResultDlgHtml import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from ledControlDialog import ledCtrlTimePanel
    
# Global variables for interface.py

FACILITY_TREE_XML = ET.ElementTree(file = 'facility.xml')
COMPORT_TREE_XML = ET.ElementTree(file = 'comport.xml')
COORDINATOR_TTY = '/dev/ttyUSB0'
NODE_ROWS = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17']
NODE_COLUMNS = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17']
TREECTRL_ELEMENT_SELECTED = ''
TREECTRL_PARENT_SELECTED = ''
TREECTRL_UPPARENT_SELECTED = ''
FACILITY_MAP = {}
FACILITY_MAP2 = {}
FACILITY_MAP_ = {}
GROUPS_RUN_TIME = 0
GROUPS_PAUSE_TIME = 0
GROUPS_DICT = {}
GROUPS_DICT2 = {}
GROUPS_DICT_ = {}
GROUPS_QTY = 1
GROUPS_QTY2 = 1
PREVIOUS_GROUP = []
PREVIOUS_GROUP2 = []
ISSTARTED = 1
ITEM_STATE = {}
ISALLSTOPPED = 1
ISFACILITYUPDATED = 0
ISLEDON = False

# Global variables end

################################################################################################
################################################################################################
def hiddenDiscoveryThreadBody(callback):
    """
    treaded function for node discovery
    """
    for i in range(10):
        #delay(500)
        print "I'm in new thread and working fine" , threading.currentThread().getName()
        #print "thread ID =" , threading.currentThread.ident()
        print "starting node_discovery()"
        node_discovery()
        print "finished node_discovery()"
        #delay(500)
        callback()
        
def cb_hiddenDiscoveryThread():
    """
        callback function for node discovery
    """
    print "cb_testThread, threadID = ", threading.currentThread().getName()

hiddenDiscoveryThread = threading.Thread(target=hiddenDiscoveryThreadBody, args=(cb_hiddenDiscoveryThread,))
    
###############################################################################################
###############################################################################################
 
hiddenXbeeChangeStateQueue = Queue.Queue()

class hiddenXbeeChangeStateThread(threading.Thread):
    """
        A thread class that will start/stop Xbee module and will return Xbee state
    """
   
    def __init__ (self, longAddress, pinXbee, statePin, q):
        self.longAddr = longAddress
        self.pin = pinXbee
        self.state = statePin
        self.q = q
        threading.Thread.__init__ (self)
   
    def run(self):
        result = hiddenXbeeChangeState(self.longAddr, self.pin, self.state)
        self.q.put(result)
     
##############################################################################################
##############################################################################################
    
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        hv = '0x' + hv
        lst.append(hv)

def SCS_ShowMessage(text, messageType):
    if messageType == 0:
        msgDlg = wx.MessageBox(str(text), 'ASCS съобщение', 
                      wx.OK | wx.ICON_INFORMATION)
    if messageType == 1:
        msgDlg = wx.MessageBox(str(text), 'ASCS съобщение', 
                      wx.YES_NO |wx.NO_DEFAULT | wx.ICON_INFORMATION)
        if msgDlg == wx.YES:
            return True
        else:
            return False
        
def get_selected_items(list_control):
        """
        Gets the selected items for the list control.
        Selection is returned as a list of selected indices,
        low to high.
        """

        selection = []

        # start at -1 to get the first selected item
        current = -1
        while True:
            next = GetNextSelected(list_control, current)
            if next == -1:
                return selection

            selection.append(next)
            current = next
        
def GetNextSelected(list_control, current):
    """Returns next selected item, or -1 when no more"""

    return list_control.GetNextItem(current,
                                wx.LIST_NEXT_ALL,
                                wx.LIST_STATE_SELECTED)
    
def processLongAddress(lineFromTree):
    """
    Returns long address from tree control line selected 
    """
    colon_sign = ":"
    return lineFromTree[lineFromTree.index(colon_sign) + len(colon_sign):].strip()

def processNodeName(lineFromTree):
    """
    Returns long address from tree control line selected (ValueError)
    """
    colon_sign = ":"
    try:
        return lineFromTree[:lineFromTree.index(colon_sign) - len(colon_sign)].strip()
    except ValueError:
        return ''
            

def parseXbeeIsResponse(xbee_response):
    """
        Returns dictionary with IO Status
    """

    global ITEM_STATE
    io_params = {}
    
    try:    
        io_params = xbee_response.get('parameter')[0]
    except TypeError:
        io_params = {}
        
    print io_params    
        
    try:
        num1=(io_params['adc-3']/float(1023))*6.5+6.8
        ITEM_STATE['ADC3']=round(num1,2)
    except KeyError:
        num1 = 0.00
        
    try:
        num2=(io_params['adc-2']/float(1023))*6.5+14.5
        ITEM_STATE['ADC2']=round(num2,2)
    except KeyError:
        num2 = 0.00
        
    try:
        ITEM_STATE['DO0']=io_params['dio-0']
    except KeyError:
        ITEM_STATE['DO0']=False
        
    try:
        ITEM_STATE['DO1']=io_params['dio-1']
    except KeyError:
        ITEM_STATE['DO1']=False
        
    try:
        ITEM_STATE['DI4']=io_params['dio-4']
    except KeyError:
        ITEM_STATE['DI4']=False
        
    return ITEM_STATE

def get_html_tbl(seq, col_count):
    if len(seq) % col_count:
        seq.extend([''] * (col_count - len(seq) % col_count))
    tbl_template = '<table>%s</table>' % ('<tr>%s</tr>' % ('<td>%s</td>' * col_count) * (len(seq)/col_count))
    return tbl_template % tuple(seq)


class SCS_GroupsFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        # begin SCS_GroupsFrame.__init__
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, wx.GetApp().TopWindow, *args, **kwargs)
        self.SetIcon(wx.Icon('fountain16_16_active.ico', wx.BITMAP_TYPE_ICO))
        
        wxID_SETLBOXGROUPS = wx.NewId()
        wxID_CHANGECELL = wx.NewId()
        wxID_CHANGEPHASE = wx.NewId()
        wxID_CHANGEPAUSE = wx.NewId()
        wxID_CHANGERUN = wx.NewId()
        
        self.groupCboxCell = wx.ComboBox(self, wxID_CHANGECELL, choices=[], style=wx.CB_DROPDOWN)
        self.groupCboxPhase = wx.ComboBox(self, wxID_CHANGEPHASE, choices=[], style=wx.CB_DROPDOWN)
        self.groupLabPauseTime = wx.StaticText(self, wx.ID_ANY, "Пауза: ")
        self.groupLabRunTime = wx.StaticText(self, wx.ID_ANY, "Работа: ")
        self.groupCboxPauseTime = wx.ComboBox(self, wxID_CHANGEPAUSE, choices=['0','1','2','3'], style=wx.CB_DROPDOWN)
        self.groupCboxPauseTime.SetToolTip(wx.ToolTip("изберете време за пауза"))
        self.groupCboxRunTime = wx.ComboBox(self, wxID_CHANGERUN, choices=['0','1','2','3','4','5','6','7','8','9','10'], style=wx.CB_DROPDOWN)
        self.groupCboxRunTime.SetToolTip(wx.ToolTip("изберете време за работа"))
        self.groupLboxGroups = wx.ListBox(self, id = wxID_SETLBOXGROUPS, choices=[], style=wx.LB_SINGLE | wx.LB_SORT)
        self.groupButtonGroupAdd = wx.Button(self, wx.ID_ADD, "")
        self.groupButtonGroupAdd.SetToolTip(wx.ToolTip("кликнете, за да добавите група"))
        self.groupButtonGroupRemove = wx.Button(self, wx.ID_REMOVE, "")
        self.groupButtonGroupRemove.SetToolTip(wx.ToolTip("кликнете, за да премахнете група"))
        self.sizerGroup_Node_staticbox = wx.StaticBox(self, wx.ID_ANY, "Група")
        self.groupLboxNodes = wx.ListBox(self, wx.ID_ANY, choices=[], style=wx.LB_SINGLE | wx.LB_SORT)
        self.groupCboxNodes = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.groupCboxNodes.SetToolTip(wx.ToolTip("изберете елемент за добавяне"))
        self.groupButtonNodeAdd = wx.Button(self, wx.ID_ADD, "")
        self.groupButtonNodeAdd.SetToolTip(wx.ToolTip("кликнете, за да добавите елемент към група"))
        self.groupButtonNodeRemove = wx.Button(self, wx.ID_REMOVE, "")
        self.groupButtonNodeRemove.SetToolTip(wx.ToolTip("кликнете, за да премахнете елемент от група"))
        self.sizerNodes_staticbox = wx.StaticBox(self, wx.ID_ANY, "Елементи")

        self.__set_properties()
        self.__do_layout()

# Bindings
        self.groupLboxGroups.Bind(wx.EVT_LISTBOX, self.OnMarkGroup, id=wxID_SETLBOXGROUPS)
        self.groupCboxCell.Bind(wx.EVT_TEXT, self.OnChangeSelCell, id=wxID_CHANGECELL)
        self.groupCboxPhase.Bind(wx.EVT_TEXT, self.OnChangeSelPhase, id=wxID_CHANGEPHASE)
        self.groupButtonNodeAdd.Bind(wx.EVT_BUTTON, self.OnNodeAdd, self.groupButtonNodeAdd)
        self.groupButtonNodeRemove.Bind(wx.EVT_BUTTON, self.OnNodeRemove, self.groupButtonNodeRemove)


    def __set_properties(self):
        # begin wxGlade: SCS_GroupsFrame.__set_properties
        self.SetTitle("Настройки на групите")
        self.SetSize((900, 500))
        self.groupLboxGroups.SetMinSize((800,150))
        self.groupLboxNodes.SetMinSize((800,150))
# Disable buttons for Add and Remove

        self.groupButtonGroupAdd.Disable()
        self.groupButtonGroupRemove.Disable()
        
# Fill of elements
        
        for group_cells in FACILITY_TREE_XML.iterfind('cell'):
            self.groupCboxCell.Append(group_cells.text.strip())

        self.groupCboxPhase.Append('Phase 1')
        self.groupCboxPhase.Append('Phase 2')
        
        self.groupCboxNodes.Clear()
        
        for row_temp in range(18):
            for col_temp in range(18):
                if row_temp <> 0 and col_temp <> 0:
                    node_temp = str(row_temp)+'.'+str(col_temp)
                    self.groupCboxNodes.Append(node_temp)

    def __do_layout(self):
        # begin wxGlade: SCSGroupsFrame.__do_layout
        sizerGroupFrame = wx.BoxSizer(wx.VERTICAL)
        self.sizerNodes_staticbox.Lower()
        sizerNodes = wx.StaticBoxSizer(self.sizerNodes_staticbox, wx.VERTICAL)
        sizeNodesButtons = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerGroup_Node_staticbox.Lower()
        sizerGroup_Node = wx.StaticBoxSizer(self.sizerGroup_Node_staticbox, wx.VERTICAL)
        sizerGroupsButtons = wx.BoxSizer(wx.HORIZONTAL)
        sizerCell_Phase = wx.BoxSizer(wx.HORIZONTAL)
        sizerCell_Phase.Add(self.groupCboxCell, 0, wx.ALL, 5)
        sizerCell_Phase.Add(self.groupCboxPhase, 0, wx.ALL, 5)
        sizerCell_Phase.Add(self.groupLabPauseTime, 0, wx.ALL, 5)
        sizerCell_Phase.Add(self.groupCboxPauseTime,0, wx.ALL, 5)
        sizerCell_Phase.Add(self.groupLabRunTime, 0, wx.ALL, 5)
        sizerCell_Phase.Add(self.groupCboxRunTime,0, wx.ALL, 5)
        sizerGroup_Node.Add(sizerCell_Phase, 0, wx.EXPAND, 0)
        sizerGroup_Node.Add(self.groupLboxGroups, 0, wx.ALL | wx.EXPAND, 5)
        sizerGroupsButtons.Add(self.groupButtonGroupAdd, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        sizerGroupsButtons.Add(self.groupButtonGroupRemove, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        sizerGroup_Node.Add(sizerGroupsButtons, 0, wx.EXPAND, 0)
        sizerGroupFrame.Add(sizerGroup_Node, 0, wx.EXPAND, 0)
        sizerNodes.Add(self.groupLboxNodes, 0, wx.ALL | wx.EXPAND, 5)
        sizerNodes.Add(self.groupCboxNodes, 0, wx.ALL, 5)
        sizeNodesButtons.Add(self.groupButtonNodeAdd, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        sizeNodesButtons.Add(self.groupButtonNodeRemove, 0, wx.ALL, 5)
        sizeNodesButtons.Add((20, 20), 0, wx.EXPAND, 5)
        sizerNodes.Add(sizeNodesButtons, 0, wx.EXPAND, 0)
        sizerGroupFrame.Add(sizerNodes, 0, wx.EXPAND, 0)
        self.SetSizer(sizerGroupFrame)
        self.Layout()
        
    def loadGroupLbox(self,cell_name,phase_name):
        
        self.groupLboxGroups.Clear()
                
        for groups_list in FACILITY_TREE_XML.iterfind('groups'):
            if groups_list.get('cell')==cell_name and groups_list.get('phase')==phase_name:
                for group in groups_list:
                    self.groupLboxGroups.Append(group.get('name')) 
                    
    def loadGroupNodesLbox(self, cell_name, phase_name, group_name):
        
        self.groupLboxNodes.Clear()
                
        for groups_list in FACILITY_TREE_XML.iterfind('groups'):
            if groups_list.get('cell')==cell_name and groups_list.get('phase')==phase_name:
                for group in groups_list:
                    if group.get('name')==group_name:
                        try:
                            for node in group:
                                self.groupLboxNodes.Append(node.text)
                        except TypeError:
                            print "greshka"

    def removeNodeLbox(self,cell_name, phase_name, group_name, node_name):
        """
        """
        for groups_list in FACILITY_TREE_XML.iterfind('groups'):
            if groups_list.get('cell')==cell_name and groups_list.get('phase')==phase_name:
                for group in groups_list:
                    if group.get('name')==group_name:
                        for node in group:
                            if node.tag == 'node' and node.text == node_name:
                                group.remove(node)
                                
        SCS_ShowMessage("Елементът е премахнат успешно!",0)

    def addNodeGroupLbox(self,cell_name, phase_name, group_name, node_name):
        """
        """
        for groups_list in FACILITY_TREE_XML.iterfind('groups'):
            if groups_list.get('cell')==cell_name and groups_list.get('phase')==phase_name:
                for group in groups_list:
                    if group.get('name')==group_name:
                        node_new=ET.SubElement(group, 'node')
                        node_new.text = node_name
                                
        SCS_ShowMessage("Елементът е добавен успешно!",0)

    def OnMarkGroup(self,event):
        group_name_sel = self.groupLboxGroups.GetString(self.groupLboxGroups.GetSelection())
        self.loadGroupNodesLbox(self.groupCboxCell.GetValue(),self.groupCboxPhase.GetValue(),group_name_sel)

    def OnChangeSelCell(self,event):
        self.loadGroupLbox(self.groupCboxCell.GetValue(),self.groupCboxPhase.GetValue())
            
    def OnChangeSelPhase(self,event):
        self.loadGroupLbox(self.groupCboxCell.GetValue(),self.groupCboxPhase.GetValue())

    def OnNodeAdd(self,event):
        self.addNodeGroupLbox(self.groupCboxCell.GetValue(),self.groupCboxPhase.GetValue(),self.groupLboxGroups.GetString(self.groupLboxGroups.GetSelection()),self.groupCboxNodes.GetValue())
        FACILITY_TREE_XML.write('facility.xml')
        self.loadGroupNodesLbox(self.groupCboxCell.GetValue(),self.groupCboxPhase.GetValue(),self.groupLboxGroups.GetString(self.groupLboxGroups.GetSelection()))
       
    def OnNodeRemove(self,event):
        self.removeNodeLbox(self.groupCboxCell.GetValue(),self.groupCboxPhase.GetValue(),self.groupLboxGroups.GetString(self.groupLboxGroups.GetSelection()),self.groupLboxNodes.GetString(self.groupLboxNodes.GetSelection()))
        FACILITY_TREE_XML.write('facility.xml')
        self.loadGroupNodesLbox(self.groupCboxCell.GetValue(),self.groupCboxPhase.GetValue(),self.groupLboxGroups.GetString(self.groupLboxGroups.GetSelection()))


class SCS_SysSettingsFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        # begin wxGlade: MyFrame.__init__
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        #kwargs["style"] = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.RESIZE_BORDER | wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, wx.GetApp().TopWindow, *args, **kwargs)
        self.SetIcon(wx.Icon('fountain16_16_active.ico', wx.BITMAP_TYPE_ICO))
        
        wxID_SETLBOXCOMPORT = wx.NewId()
        
        self.setLabCell = wx.StaticText(self, wx.ID_ANY, (" Клетка: "), style=wx.ST_NO_AUTORESIZE)
        self.setCboxCell = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.setLabPhase = wx.StaticText(self, wx.ID_ANY, (" Фаза: "), style=wx.ST_NO_AUTORESIZE)
        self.setCboxPhase = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.sizer_3_staticbox = wx.StaticBox(self, wx.ID_ANY, (" Топография: "))
        self.setLabComport = wx.StaticText(self, wx.ID_ANY, ("COM порт: "))
        self.setLboxComport = wx.ListBox(self, id=wxID_SETLBOXCOMPORT, choices=[], style=wx.LB_SINGLE | wx.LB_ALWAYS_SB | wx.LB_SORT)
        self.setRboxDatabits = wx.RadioBox(self, wx.ID_ANY, (" Битове за данни"), choices=[("7 бита"), ("8 бита")], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.setRboxParity = wx.RadioBox(self, wx.ID_ANY, (" Четност "), choices=[("None"), ("Even"), ("Mark"), ("Odd"), ("Space")], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.setRboxStopbits = wx.RadioBox(self, wx.ID_ANY, (" Стоп битове "), choices=[("1 bit"), ("2 bits")], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.setRboxFlowctrl = wx.RadioBox(self, wx.ID_ANY, (" Контрол на потока "), choices=[("None"), ("Hardware"), ("Xon/Xoff")], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.sizer_4_staticbox = wx.StaticBox(self, wx.ID_ANY, (" COM порт"))
        self.setButtonSave = wx.Button(self, wx.ID_SAVE, (""))
        self.setButtonCancel = wx.Button(self, wx.ID_CANCEL, (""))
        self.setButtonActivate = wx.Button(self, wx.ID_HOME, ("Активиране"))
        self.setButtonActivate.SetToolTip(wx.ToolTip("активира, избрания COM порт"))
        self.setLedPanel = ledCtrlTimePanel(self)        

        self.__set_properties()
        self.__do_layout()

        self.setLboxComport.Bind(wx.EVT_LISTBOX, self.OnMark, id=wxID_SETLBOXCOMPORT)
        self.setButtonCancel.Bind(wx.EVT_BUTTON, self.OnCancelPressed, id = wx.ID_CANCEL)

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Системни настройки")
        self.SetSize((600, 600))
        self.setRboxDatabits.SetSelection(0)
        self.setRboxParity.SetSelection(0)
        self.setRboxStopbits.SetSelection(0)
        self.setRboxFlowctrl.SetSelection(0)
        
        comPortList = getComPortListXML()
        for comPort in comPortList:
            self.setLboxComport.Append(comPort.get('name'))
        
    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_4_staticbox.Lower()
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
        self.sizer_3_staticbox.Lower()
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        sizer_3.Add(self.setLabCell, 0, wx.EXPAND, 1)
        sizer_3.Add(self.setCboxCell, 0, 0, 0)
        sizer_3.Add(self.setLabPhase, 0, 0, 1)
        sizer_3.Add(self.setCboxPhase, 0, 0, 0)
        sizer_3.Add((20, 20), 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_4.Add(self.setLabComport, 0, wx.ALL, 5)
        sizer_4.Add(self.setLboxComport, 0, wx.EXPAND | wx.ALL, 5)
        sizer_4.Add(self.setRboxDatabits, 0, wx.ALL, 5)
        sizer_4.Add(self.setRboxParity, 0, wx.ALL, 5)
        sizer_4.Add(self.setRboxStopbits, 0, wx.ALL, 5)
        sizer_4.Add(self.setRboxFlowctrl, 0, wx.ALL, 5)
        sizer_4.Add((20, 20), 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_4, 0, wx.EXPAND, 1)
        sizer_1.Add(self.setLedPanel, 0, wx.EXPAND, 0)        
        sizer_1.Add((20, 20), 0, 0, 0)
        sizer_2.AddSpacer(( 0, 0), 1, wx.EXPAND, 5 )
        sizer_2.Add(self.setButtonSave, 0, wx.ALL, 5)
        sizer_2.Add(self.setButtonCancel, 0, wx.ALL, 5)
        sizer_2.Add(self.setButtonActivate, 0, wx.ALL, 5)
        sizer_1.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.SetSizeHints(self)
        self.Layout()
        self.Centre()
    
    def OnMark(self, event):
        com_port_sel = self.setLboxComport.GetStringSelection()
        com_port_tree = ET.ElementTree(file = 'comport.xml')

        com_port_root = com_port_tree.getroot()
        
        for com_port in com_port_tree.iterfind('com[@name="%s"]' %com_port_sel):
#            com_port_tags = [com_port.tag for com_port in com_port.iter()]
            for com_port_tag in com_port.iter():
                if com_port_tag.tag == "active":
                    self.SetTitle("Системни настройки [ %s ]" %com_port_tag.text )    
                if com_port_tag.tag == "cell":
                    print com_port_tag.tag,":",com_port_tag.text                                    
                if com_port_tag.tag == "phase":
                    print com_port_tag.tag,":",com_port_tag.text            

                if com_port_tag.tag == "databits":
                    if com_port_tag.text == "7":
                        self.setRboxDatabits.SetSelection(0)
                    elif com_port_tag.text == "8":
                        self.setRboxDatabits.SetSelection(1)

                if com_port_tag.tag == "parity":
                    if com_port_tag.text == "None":
                        self.setRboxParity.SetSelection(0)
                    elif com_port_tag.text == "Even":
                        self.setRboxParity.SetSelection(1)
                    elif com_port_tag.text == "Mark":
                        self.setRboxParity.SetSelection(2)
                    elif com_port_tag.text == "Odd":
                        self.setRboxParity.SetSelection(3)
                    elif com_port_tag.text == "Space":
                        self.setRboxParity.SetSelection(4)

                if com_port_tag.tag == "stopbits":
                    if com_port_tag.text == "1":
                        self.setRboxStopbits.SetSelection(0)
                    elif com_port_tag.text == "2":
                        self.setRboxStopbits.SetSelection(1)
                        
                if com_port_tag.tag == "flowcontrol":
                    if com_port_tag.text == "None":
                        self.setRboxFlowctrl.SetSelection(0)
                    elif com_port_tag.text == "Software":
                        self.setRboxFlowctrl.SetSelection(1)
                    elif com_port_tag.text == "Xon/Xoff":
                        self.setRboxFlowctrl.SetSelection(2)

    def OnCancelPressed(self, event):
        """
        """
        self.Close()

class SCS_AddFrame(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        # begin wxGlade: SCS_AddFrame.__init__
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, wx.GetApp().TopWindow, *args, **kwargs)
        self.SetIcon(wx.Icon('fountain16_16_active.ico', wx.BITMAP_TYPE_ICO))
        self.addButtonDiscover = wx.Button(self, wx.ID_FIND)
        self.addButtonClear = wx.Button(self, wx.ID_CLEAR)
        self.button_3 = wx.Button(self, wx.ID_ANY, ("Резерв"))
        self.button_3.Hide()
        
# Fill combo boxes with mysql query => tuple  => list
        cellsList = ['Cell 1', 'Cell 2']
        phasesList = ['Phase 1', 'Phase 2']

        wxID_ADDCHANGECELL = wx.NewId()
        wxID_ADDCHANGEPHASE = wx.NewId()
        wxID_ADDCHANGECOLUMN = wx.NewId()
        wxID_ADDCHANGEROW = wx.NewId()
     
        self.label_cell = wx.StaticText(self, wx.ID_ANY, ("Клетка: "))
        self.addCboxCell = wx.ComboBox(self,  wxID_ADDCHANGECELL, choices=cellsList, style=wx.CB_DROPDOWN | wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)        
        self.addCboxCell.SetToolTip(wx.ToolTip("изберете клетка"))
        self.label_phase = wx.StaticText(self, wx.ID_ANY, ("Фаза: "))
        self.addCboxPhase = wx.ComboBox(self, wxID_ADDCHANGEPHASE, choices=phasesList, style=wx.CB_DROPDOWN | wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT)
        self.addCboxPhase.SetToolTip(wx.ToolTip("изберете фаза"))         

        self.addLabColumn = wx.StaticText(self, wx.ID_ANY, ("Колона: "))
        self.addCboxColumn = wx.ComboBox(self, wxID_ADDCHANGECOLUMN, choices=NODE_COLUMNS, style=wx.CB_DROPDOWN | wx.CB_DROPDOWN | wx.CB_READONLY )        
        self.addCboxColumn.SetToolTip(wx.ToolTip("изберете колона [задължително]"))
        self.addLabRow = wx.StaticText(self, wx.ID_ANY, ("Ред: "))
        self.addCboxRow = wx.ComboBox(self, wxID_ADDCHANGEROW, choices=NODE_ROWS, style=wx.CB_DROPDOWN | wx.CB_DROPDOWN | wx.CB_READONLY )
        self.addCboxRow.SetToolTip(wx.ToolTip("изберете ред [задължително]"))  

        self.addLboxDiscovered = wx.ListCtrl(self, wx.ID_ANY,  style=wx.LC_REPORT |wx.BORDER_SUNKEN)
        self.addLboxDiscovered.InsertColumn(0, 'Адрес')
        self.addLboxDiscovered.InsertColumn(1, 'Идентификатор', width=125)
        self.addLboxDiscovered.InsertColumn(2, 'Кратък адрес', width=125)
        
        self.addLboxFacility = wx.ListBox(self, wx.ID_ANY,  style=wx.LC_REPORT |wx.BORDER_SUNKEN)
        
        self.addButtonSave = wx.Button(self, wx.ID_SAVE)
        self.addButtonClose = wx.Button(self, wx.ID_CLOSE)
        self.button_9 = wx.Button(self, wx.ID_ANY, ("Резерв"))
        self.button_9.Hide()

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnDiscover, self.addButtonDiscover)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.addButtonClear)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnMarkLeft, self.addLboxDiscovered)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnMarkRight, self.addLboxFacility)
        self.Bind(wx.EVT_BUTTON, self.OnSave, id = wx.ID_SAVE)
        self.Bind(wx.EVT_BUTTON, self.OnClosePressed, id = wx.ID_CLOSE)
        self.addCboxCell.Bind(wx.EVT_TEXT, self.OnChangeSelAddCell, id=wxID_ADDCHANGECELL)
        self.addCboxPhase.Bind(wx.EVT_TEXT, self.OnChangeSelAddPhase, id=wxID_ADDCHANGEPHASE)
        self.addCboxColumn.Bind(wx.EVT_TEXT, self.OnChangeSelAddColumn, id=wxID_ADDCHANGECOLUMN)
        self.addCboxRow.Bind(wx.EVT_TEXT, self.OnChangeSelAddRow, id=wxID_ADDCHANGEROW)        
        # end wxGlade
     
    def __set_properties(self):
        self.SetTitle(("Добавяне / Откриване"))
        self.SetSize((900, 500))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("fountain16_16_active.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

    def __do_layout(self):
        # begin wxGlade: SCS_AddFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.addButtonDiscover, 0, wx.ALL, 5)
        sizer_2.Add(self.addButtonClear, 0, wx.ALL, 5)
        sizer_2.Add(self.button_3, 0, wx.ALL, 5)
        sizer_2.Add((5, 20), 1, wx.ALL, 0)
        sizer_2.Add(self.label_cell,0,wx.ALL|wx.EXPAND,5)
        sizer_2.Add(self.addCboxCell, 0, wx.ALL | wx.EXPAND, 5)
        sizer_2.Add(self.label_phase,0,wx.ALL|wx.EXPAND,0)
        sizer_2.Add(self.addCboxPhase, 0, wx.ALL | wx.EXPAND, 5)
        sizer_2.Add(self.addLabColumn, 0, wx.ALL, 5)
        sizer_2.Add(self.addCboxColumn, 0, wx.ALL, 5)
        sizer_2.Add(self.addLabRow, 0, wx.ALL, 5)
        sizer_2.Add(self.addCboxRow, 0, wx.ALL, 5)
        sizer_1.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 0)
        sizer_3.Add(self.addLboxDiscovered, 1, wx.ALL | wx.EXPAND, 0)
        sizer_4.Add((20, 20), 1, 0, 0)
        sizer_4.Add((20, 20), 1, 0, 0)
        sizer_3.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 0)
        sizer_3.Add(self.addLboxFacility, 1, wx.ALL | wx.EXPAND, 0)
        sizer_1.Add(sizer_3, 1, wx.ALL | wx.EXPAND, 0)
        sizer_5.Add((20, 20), 1, 0, 0)
        sizer_5.Add(self.addButtonSave, 0, wx.ALL, 5)
        sizer_5.Add(self.addButtonClose    , 0, wx.ALL, 5)
        sizer_5.Add(self.button_9, 0, wx.ALL, 5)
        sizer_1.Add(sizer_5, 0, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

# Node discovery procedure start.

    def loadFacilityNodesLbox(self, cell_name, phase_name, col_num, row_num):
        
        self.addLboxFacility.Clear()

        if cell_name.strip()<>'' and phase_name.strip()<>'' and col_num.strip()<>'' and row_num.strip()<>'':
            for cell_ in FACILITY_TREE_XML.iterfind('cell'):
                if cell_.get('name')==cell_name:
                    for phase_ in cell_:
                        if phase_.get('name')==phase_name:
                            for node_ in phase_:
                                name_node = col_num +"."+ row_num
                                if node_.get('name')== name_node:
                                    self.addLboxFacility.Append(node_.text.strip())
        else:
            SCS_ShowMessage("Някои от задължителните полета не са дефинирани (Клетка,Фаза,Колона,Ред)!",0)

    def addNodeAddtoXML(self, col_num, row_num, cell_name, phase_name, node_address, node_sp):
        
        node_list = []
                
        for cell in FACILITY_TREE_XML.iterfind('cell'):
            if cell.get('name')==cell_name:
                for phase in cell:
                    if phase.get('name')==phase_name:
                        for node in phase:
                            node_list.append(node.get('name'))
                        print node_list
                        
        node_number = "%s.%s" %(col_num, row_num)
        if node_number in node_list:
            hasNode = True
        else:
            hasNode = False
        
        for cell in FACILITY_TREE_XML.iterfind('cell'):
            if cell.get('name')==cell_name:
                for phase in cell:
                    if phase.get('name') == phase_name:
                        for node in phase:
                            if hasNode and node.get('name')==node_number:
                                print node.text,":", node.get('name')
                                node.text = node_address
                                node.set('sp',node_sp)
                                message_text = "%s.%s = %s!" %(col_num, row_num, node.text)
                                SCS_ShowMessage(message_text.decode('utf-8'),0)
                            if not hasNode:
                                node_new=ET.SubElement(phase, 'node')
                                node_new.set('name',col_num+"."+row_num)
                                node_new.set('mode',"0")
                                node_new.text = node_address
                                if node_new.text == '':
                                    SCS_ShowMessage("Празен елемент е добавен към структурата!",0)
                                    break
                                else:
                                    SCS_ShowMessage("Новият елемент е добавен успешно!",0)
                                    break
                            
    def OnChangeSelAddCell(self, event):
        pass

    def OnChangeSelAddPhase(self, event):
        pass

    def OnChangeSelAddColumn(self, event):
        pass
    
    def OnChangeSelAddRow(self, event):
        self.loadFacilityNodesLbox(self.addCboxCell.GetValue(),self.addCboxPhase.GetValue(),self.addCboxColumn.GetValue(),self.addCboxRow.GetValue())
    

    def OnDiscover(self, event):

        
        self.addLboxDiscovered.DeleteAllItems()
        self.addLboxDiscovered.InsertStringItem(0,"None")
        msg = "Моля, почакайте извършва се откриване на инсталирани управления..."
        old_style = self.GetWindowStyle()
        self.SetWindowStyle(old_style | wx.STAY_ON_TOP)
        busyDlg = wx.BusyInfo(msg, self)
        xbeeNDresult = node_discovery()
        busyDlg = None
        self.SetWindowStyle(old_style)    
        
#################################  За корекция Attribute Error ##################################################

        if type(xbeeNDresult) is list:
            for node_response in xbeeNDresult:
                try:
                    node_parameter_dict = node_response.get('parameter')
#                 print node_parameter_dict
                    source_addr_long_form = ''.join("{:02X}".format(ord(c)) for c in node_parameter_dict.get("source_addr_long"))
#                 print ''.join("{:02X}".format(ord(c)) for c in '\x00\x13\xa2\x00@\x9c0\x03')
                    source_addr_form = ':'.join("{:02X}".format(ord(c)) for c in node_parameter_dict.get("source_addr"))
                    pos = self.addLboxDiscovered.InsertStringItem(0, ''+ source_addr_long_form)
                    self.addLboxDiscovered.SetStringItem(pos, 1, node_parameter_dict.get("node_identifier"))
                    self.addLboxDiscovered.SetStringItem(pos, 2, source_addr_form)
                    print pos
                except AttributeError:
                    print "AttributeError"
        else:
            SCS_ShowMessage("Не е получен коректен резултат!",0)
            

    def OnClear(self, event):  # wxGlade: SCS_AddFrame.<event_handler>
        self.addLboxDiscovered.DeleteAllItems()


    def OnMarkLeft(self, event):  # wxGlade: SCS_AddFrame.<event_handler>
        print "Event handler 'OnMarkLeft' not implemented!"
        event.Skip()

    def OnMarkRight(self, event):  # wxGlade: SCS_AddFrame.<event_handler>
        event.Skip()

    def OnSave(self, event):
        """ 
        Moves selected row to right 
        """
        
        global ISFACILITYUPDATED
        
        node_id = get_selected_items(self.addLboxDiscovered)
        
        try:
            node_source_addr_long = self.addLboxDiscovered.GetItemText(node_id[0])
            node_name_sp = self.addLboxDiscovered.GetItem(node_id[0],1).GetText()
        except IndexError:
            SCS_ShowMessage("Няма избран елемент!",0)
            node_source_addr_long = ''
            
            
        node_cell = self.addCboxCell.GetString(self.addCboxCell.GetSelection())
        node_phase = self.addCboxPhase.GetString(self.addCboxPhase.GetSelection())
        node_column = self.addCboxColumn.GetString(self.addCboxColumn.GetSelection())
        node_row = self.addCboxRow.GetString(self.addCboxRow.GetSelection())
        if node_cell=='' or node_phase=='' or node_column=='' or node_row=='':
            SCS_ShowMessage("Има непопълнено задължително поле (Клетка, Фаза, Колона, Ред)!!!",0)
        else:
            self.addNodeAddtoXML(node_column, node_row, node_cell, node_phase, node_source_addr_long, node_name_sp)
            node_number = "%s.%s" %(node_column, node_row)
            NH.updateName(node_cell, node_phase, node_number, node_name_sp)
            print node_number
            FACILITY_TREE_XML.write('facility.xml')
            ISFACILITYUPDATED = 1
            self.loadFacilityNodesLbox(self.addCboxCell.GetValue(),self.addCboxPhase.GetValue(),self.addCboxColumn.GetValue(),self.addCboxRow.GetValue())        
        
    def OnClosePressed(self, event):  # wxGlade: SCS_AddFrame.<event_handler>

        self.Close()
        
# End of SCS_AddFrame...
        
class SCS_AboutFrame(wx.Frame):
    
    def __init__(self, *args, **kwargs):
        # begin wxGlade: SCS_AboutFrame.__init__
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, wx.GetApp().TopWindow, *args, **kwargs)
        self.bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("irrigation_about.png", wx.BITMAP_TYPE_ANY))
        self.label_name = wx.StaticText(self, wx.ID_ANY, ("ASCS ver.: 0.8.1\n\nGNU Public License\n\nAutor: dipl.eng. Svilen Zlatev\n\n(c)2013  Pronix1 Ltd."), style=wx.ALIGN_CENTRE)
        self.aboutTextCtrl = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.TE_LINEWRAP)
        self.button_1 = wx.Button(self, wx.ID_OK)
        self.SetIcon(wx.Icon('fountain16_16_active.ico', wx.BITMAP_TYPE_ICO))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_1)
        
# Sysytem description
        self.aboutTextCtrl.AppendText("Платформа: " + platform.platform() + "\n")   
        self.aboutTextCtrl.AppendText("Машина: " + platform.machine() + "\n")        
        self.aboutTextCtrl.AppendText("Процесор: " + platform.processor() + "\n")                           
        self.aboutTextCtrl.AppendText("Uname: " + str(platform.uname()))     
# End System description
        
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: SCS_AboutFrame.__set_properties
        self.SetTitle("Относно ASCS")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("fountain16_16_active.ico", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.aboutTextCtrl.SetMinSize((484, 80))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SCS_AboutFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.bitmap_1, 0, 0, 0)
        sizer_1.Add(self.label_name, 0, wx.ALL | wx.EXPAND, 0)
        sizer_1.Add(self.aboutTextCtrl, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_1.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.Centre()
        # end wxGlade

    def OnOK(self, event):  # wxGlade: SCS_AboutFrame.<event_handler>
        print "Event handler 'OnOK' not implemented!"
        self.Close()
#    event.Skip()
     

class SCS_TreeCtrl(wx.TreeCtrl):
    """Define general tree control"""
    def __init__(self, parent, *args, **kwargs):
        wx.TreeCtrl.__init__(self, parent, *args, **kwargs)

        # Tree XML implementation
        
        self.loadXMLtoTree()

        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        
    #===========================================================================
    # loadXMLtoTree
    #===========================================================================
    def loadXMLtoTree(self):
        """
        """
        self.DeleteAllItems()
        self.CollapseAll()
        isz = (32,32)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(icons.antenna32_32_ico.GetBitmap())
        fldropenidx = il.Add(icons.antenna32_32_ico.GetBitmap())
        self.startedXbee     = il.Add(icons.fountain32_32_active_ico.GetBitmap())
        self.stoppedXbee    = il.Add(icons.fountain32_32_unactive__ico.GetBitmap())
        self.errorXbee = il.Add(icons.fountain32_32_error_ico.GetBitmap())
        self.disconnectedXbee = il.Add(icons.fountain32_32_disconnected_ico.GetBitmap())

        self.SetImageList(il)
        self.il = il
        
        wdf_root = FACILITY_TREE_XML.getroot()

        self.root = self.AddRoot(wdf_root.text.strip())
        self.SetPyData(self.root, None)
        self.SetItemImage(self.root, fldridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(self.root, fldropenidx, wx.TreeItemIcon_Expanded)

        for wdf_cells in FACILITY_TREE_XML.iterfind('cell'):
            child = self.AppendItem(self.root, wdf_cells.text.strip()) #.text.strip()
            self.SetPyData(child, None)
            self.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
            self.SetItemImage(child, fldropenidx, wx.TreeItemIcon_Expanded)

            for wdf_phases in wdf_cells:
                last = self.AppendItem(child, wdf_phases.text.strip())
                self.SetPyData(last, None)
                self.SetItemImage(last, fldridx, wx.TreeItemIcon_Normal)
                self.SetItemImage(last, fldropenidx, wx.TreeItemIcon_Expanded)
                
                for wdf_node in wdf_phases:
                    print wdf_node.get('name')
                    node_params = wdf_node.get('name') + ' : ' + wdf_node.text.strip()
                    item = self.AppendItem(last,  node_params)
                    self.SetPyData(item, None)
                    self.SetItemImage(item, self.stoppedXbee, wx.TreeItemIcon_Normal)
#                     self.SetItemImage(item, smileidx, wx.TreeItemIcon_Selected)
                    
        self.ExpandAll()
        
    #===========================================================================
    # changeItemColor
    #===========================================================================
    def changeItemColor(self, longAddress, itemColor):
        """
        """
        root = self.GetRootItem()
        (child_1, cookie_1) = self.GetFirstChild(root)
        while child_1.IsOk():
            (child_2, cookie_2) = self.GetFirstChild(child_1)
            while child_2.IsOk():
                (child_3, cookie_3) = self.GetFirstChild(child_2)
                while child_3.IsOk():
                    try:
                        itemLongAddress = processLongAddress(self.GetItemText(child_3))
                    except ValueError:
                        pass
                    if itemLongAddress == longAddress:
                        self.SetItemTextColour(child_3, itemColor)
                    (child_3, cookie_3) = self.GetNextChild(child_2, cookie_3)                
                
                (child_2, cookie_2) = self.GetNextChild(child_1, cookie_2)  
            (child_1, cookie_1) = self.GetNextChild(root, cookie_1)
            
    #===========================================================================
    # changeItemImage
    #===========================================================================
    def changeItemImage(self, longAddress, itemImage):
        """
        """
        root = self.GetRootItem()
        (child_1, cookie_1) = self.GetFirstChild(root)
        while child_1.IsOk():
            (child_2, cookie_2) = self.GetFirstChild(child_1)
            while child_2.IsOk():
                (child_3, cookie_3) = self.GetFirstChild(child_2)
                while child_3.IsOk():
                    try:
                        itemLongAddress = processLongAddress(self.GetItemText(child_3))
                    except ValueError:
                        pass
                    if itemLongAddress == longAddress:
                        self.SetItemImage(child_3, itemImage)
                    (child_3, cookie_3) = self.GetNextChild(child_2, cookie_3)                
                
                (child_2, cookie_2) = self.GetNextChild(child_1, cookie_2)  
            (child_1, cookie_1) = self.GetNextChild(root, cookie_1)

    #===========================================================================
    # OnLeftDClick
    #===========================================================================
    def OnLeftDClick(self, event):
        """
        """
        global TREECTRL_ELEMENT_SELECTED
 
        try:
            long_address = processLongAddress(TREECTRL_ELEMENT_SELECTED)
            msg = {}
            pub.sendMessage(("show.mainframe"), state = msg)
            
            if long_address != 'None':
                xbee_state = xbee_is(long_address.decode('hex'))
            else:
                xbee_state = {}
                
            if xbee_state:
                msg = parseXbeeIsResponse(xbee_state)
                pub.sendMessage(("show.mainframe"), state = msg)
            else:
                msg = {}
                pub.sendMessage(("show.mainframe"), state = msg)                
                SCS_ShowMessage("Xbee: Изтекло време за отговор!",0)
        except ValueError:
            SCS_ShowMessage("Няма избран валиден елемент!",0)

    #===========================================================================
    # OnSize
    #===========================================================================
    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

    #===========================================================================
    # OnItemExpanded
    #===========================================================================
    def OnItemExpanded(self, event):
        item = event.GetItem()
        if item:
            pass
            # self.WriteText("OnItemExpanded: %s\n" % self.tree.GetItemText(item))

    #===========================================================================
    # OnItemCollapsed
    #===========================================================================
    def OnItemCollapsed(self, event):
        item = event.GetItem()
        if item:
            pass
            # self.WriteText("OnItemCollapsed: %s\n" % self.tree.GetItemText(item))

    #===========================================================================
    # OnSelChanged
    #===========================================================================
    def OnSelChanged(self, event):
        
        global TREECTRL_ELEMENT_SELECTED 
        global TREECTRL_PARENT_SELECTED
        global TREECTRL_UPPARENT_SELECTED
                
        self.item = event.GetItem()
        self.parent = self.GetItemParent(self.item)
        self.upparent = self.GetItemParent(self.parent)

        if self.item:
            TREECTRL_ELEMENT_SELECTED = self.GetItemText(self.item)
            
        if self.parent:
            TREECTRL_PARENT_SELECTED = self.GetItemText(self.parent)
        
        if self.upparent:
            TREECTRL_UPPARENT_SELECTED = self.GetItemText(self.upparent)
            
        msg = {}
        pub.sendMessage('show.mainframe', state = msg)
        
        events_dict = NH.getNHEvents(TREECTRL_UPPARENT_SELECTED, TREECTRL_PARENT_SELECTED, processNodeName(TREECTRL_ELEMENT_SELECTED))
        infobox = {}
        version = NH.getNHVersion(TREECTRL_UPPARENT_SELECTED, TREECTRL_PARENT_SELECTED, processNodeName(TREECTRL_ELEMENT_SELECTED))
        node_name = NH.getNHName(TREECTRL_UPPARENT_SELECTED, TREECTRL_PARENT_SELECTED, processNodeName(TREECTRL_ELEMENT_SELECTED))
        infobox['version']= version
        infobox['name'] = node_name
        pub.sendMessage('show.history', events_d = events_dict)
        pub.sendMessage('show.version', infob = infobox)

    #===========================================================================
    # OnActivate
    #===========================================================================
    def OnActivate(self, event):
        if self.item:
            print("OnActivate: %s\n" % self.GetItemText(self.item))


#===============================================================================
# SCS_MainFrame
#===============================================================================
class SCS_MainFrame(wx.Frame):
    """
        Главния работен панел с дефинирани таймери и т.н.
    """

    ID_TIMER1 = 2000
    ID_TIMER2 = 2001
    
    
    
    def __init__(self, *args, **kwargs):
        """Create the SCS_Frame."""
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetIcon(wx.Icon('fountain16_16_active.ico', wx.BITMAP_TYPE_ICO))
        
        self.resultPath = "./testresults/"
        
        pub.subscribe(self.showItemInfo, ("show.mainframe"))
        pub.subscribe(self.showItemHistory, ("show.history"))
        pub.subscribe(self.showItemVersion, ("show.version"))
        
        self.timer1 = wx.Timer(self, SCS_MainFrame.ID_TIMER1)
        self.Bind(wx.EVT_TIMER, self.updateTimer1, id=SCS_MainFrame.ID_TIMER1)
        self.timer2 = wx.Timer(self, SCS_MainFrame.ID_TIMER2)
        self.Bind(wx.EVT_TIMER, self.updateTimer2, id=SCS_MainFrame.ID_TIMER2)
        
        self.Bind(wx.EVT_ENTER_WINDOW, self.onEnterWindow, self)        
        
        # Build the menu bar ---------------------------------------------------
        MenuBar = wx.MenuBar()
        #System menu build 
        SystemMenu = wx.Menu()
        item = SystemMenu.Append(wx.ID_FIND, text = "Добавяне/Откриване")
        self.Bind(wx.EVT_MENU, self.OnDiscover, item)
        item = SystemMenu.Append(wx.ID_ANY, text = "Настройки")
        self.Bind(wx.EVT_MENU, self.OnSettings, item)
        item = SystemMenu.Append(wx.ID_ANY, text = "Тест управления")
        self.Bind(wx.EVT_MENU, self.onTest, item)
        item = SystemMenu.Append(wx.ID_EXIT, text="Изход\tAlt-X")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        MenuBar.Append(SystemMenu,"Система")
        GroupsMenu = wx.Menu()
        item = GroupsMenu.Append(wx.ID_ANY, text = "Настройки")
        self.Bind(wx.EVT_MENU, self.OnGroupsSet, item)
        MenuBar.Append(GroupsMenu, "Групи")
        HlpMenu = wx.Menu()
        item = HlpMenu.Append(wx.ID_ANY, text = "Скрито търсене")
        self.Bind(wx.EVT_MENU, self.OnHiddenDiscovery, item)
        item = HlpMenu.Append(wx.ID_ANY, text = "Скрито IS")
        self.Bind(wx.EVT_MENU, self.OnHiddenXbeeChangeState, item)
        item = HlpMenu.Append(wx.ID_ANY, text = "Скрито PIN")
        self.Bind(wx.EVT_MENU, self.OnHiddenXbeePin, item)
        item = HlpMenu.Append(wx.ID_ABOUT, text="Относно")
        self.Bind(wx.EVT_MENU, self.OnGenAbout, item)
        MenuBar.Append(HlpMenu,"Помощ")
        self.SetMenuBar(MenuBar)
        # End of MenuBar -------------------------------------------------------

        # Start Buttons and split windows section ------------------------------
        self.mainButtonStart = wx.Button(self, wx.ID_ANY, label = "Старт")
        self.mainButtonStart.SetToolTip(wx.ToolTip("Стартира избрания елемент"))
        self.mainButtonStop = wx.Button(self, wx.ID_ANY, label = "Стоп")
        self.mainButtonStop.SetToolTip(wx.ToolTip("Спира избрания елемент"))
        self.mainButtonStopAll = wx.Button(self, wx.ID_ANY, label = "Спри всички")
        self.mainButtonStopAll.SetToolTip(wx.ToolTip("Спира всички"))
        self.mainButtonPause = wx.Button(self, wx.ID_ANY, label = "Пауза")
        self.mainButtonPause.SetToolTip(wx.ToolTip("Пауза на всички"))
        self.mainButtonTest = wx.Button(self, wx.ID_ANY, label = "Тест")
        self.mainButtonTest.SetToolTip(wx.ToolTip("Тест на всички управления"))
        self.mainLedButtonCtrl = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap( u".//images/light_bulb_off.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW)
        self.mainLedButtonCtrl.SetToolTip(wx.ToolTip("LED контрол"))      
        self.window_1 = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER)
        self.window_1_pane_1 = wx.Panel(self.window_1, wx.ID_ANY)
        self.Sp_TreeCtrl = SCS_TreeCtrl(self.window_1_pane_1, wx.ID_ANY, style=wx.TR_HAS_BUTTONS
                                                                                | wx.TR_LINES_AT_ROOT
                                                                                | wx.TR_DEFAULT_STYLE
                                                                                | wx.SUNKEN_BORDER)

        self.window_1_pane_2 = wx.Panel(self.window_1, wx.ID_ANY)
        self.notebook_1 = wx.Notebook(self.window_1_pane_2, wx.ID_ANY, style=0)
        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, wx.ID_ANY)
        
        self.Sp_TreeCtrl.ExpandAll()
#----------------------------------------------------------------------------------------------------        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        tabNodeSZBoxer = wx.StaticBox( self.notebook_1_pane_1, wx.ID_ANY, u" Състояние " )
        tabNodeSZBoxer.Lower()
        
        tabNodeSZ = wx.StaticBoxSizer(tabNodeSZBoxer , wx.VERTICAL )
                
        tabNodeSZ1 = wx.GridSizer( 2, 3, 3, 3 )
        
        tabNodeValveSZ = wx.StaticBoxSizer(wx.StaticBox( self.notebook_1_pane_1, wx.ID_ANY, u"Клапан"), wx.VERTICAL | wx.ALL)
         
        tabNodeValveSZ1 = wx.BoxSizer( wx.VERTICAL)
        
        self.tabNodeValveBmp = wx.StaticBitmap( self.notebook_1_pane_1, wx.ID_ANY, wx.Bitmap( u".//images/magnet.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeValveSZ1.Add( self.tabNodeValveBmp, 0, wx.ALL | wx.EXPAND, 5 )
         
        tabNodeValveSZ2 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeValveL1 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Сигнал към кл.:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeValveL1.Wrap( -1 )
        tabNodeValveSZ2.Add( self.tabNodeValveL1, 0, wx.ALL, 5 )
         
        self.tabNodeValveL2 = wx.StaticText(self.notebook_1_pane_1, wx.ID_ANY, u"ИЗКЛ.", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeValveL2.Wrap( -1 )
        self.tabNodeValveL2.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
         
        tabNodeValveSZ2.Add( self.tabNodeValveL2, 0, wx.ALL, 5 )
         
        tabNodeValveSZ1.Add( tabNodeValveSZ2, 0, wx.EXPAND, 5 )
         
        tabNodeValveSZ3 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeValveL3 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Сигнал от кл.:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeValveL3.Wrap( -1 )
        tabNodeValveSZ3.Add( self.tabNodeValveL3, 0, wx.ALL, 5 )
         
        self.tabNodeValveL4 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"ИЗКЛ.", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeValveL4.Wrap( -1 )
        self.tabNodeValveL4.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
         
        tabNodeValveSZ3.Add( self.tabNodeValveL4, 0, wx.ALL, 5 )
         
         
        tabNodeValveSZ1.Add( tabNodeValveSZ3, 0, wx.EXPAND, 5 )
         
         
        tabNodeValveSZ.Add( tabNodeValveSZ1, 0, wx.EXPAND, 5 )
         
         
        tabNodeSZ1.Add( tabNodeValveSZ, 0, wx.EXPAND, 5 )
         
        tabNodeBatSZ = wx.StaticBoxSizer( wx.StaticBox( self.notebook_1_pane_1, wx.ID_ANY, u" Акумулатор " ), wx.VERTICAL )
         
        tabNodeBatSZ1 = wx.BoxSizer( wx.VERTICAL )
         
        self.tabNodeBatBmp = wx.StaticBitmap( self.notebook_1_pane_1, wx.ID_ANY, wx.Bitmap( u".//images/battery.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeBatSZ1.Add( self.tabNodeBatBmp, 0, wx.ALL, 5 )
         
        tabNodeBatSZ2 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeBatL1 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Напрежение:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeBatL1.Wrap( -1 )
        tabNodeBatSZ2.Add( self.tabNodeBatL1, 0, wx.ALL, 5 )
         
        self.tabNodeBatL2 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeBatL2.Wrap( -1 )
        self.tabNodeBatL2.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
         
        tabNodeBatSZ2.Add( self.tabNodeBatL2, 0, wx.ALL, 5 )
         
        self.tabNodeBatL3 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Vdc", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeBatL3.Wrap( -1 )
        tabNodeBatSZ2.Add( self.tabNodeBatL3, 0, wx.ALL, 5 )
         
         
        tabNodeBatSZ1.Add( tabNodeBatSZ2, 0, wx.EXPAND, 5 )
         
        tabNodeBatSZ3 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeBatG1 = wx.Gauge( self.notebook_1_pane_1, wx.ID_ANY, 14, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.tabNodeBatG1.SetValue( 0 ) 
        tabNodeBatSZ3.Add( self.tabNodeBatG1, 1, wx.ALL, 5 )
         
         
        tabNodeBatSZ1.Add( tabNodeBatSZ3, 0, wx.EXPAND, 5 )
         
         
        tabNodeBatSZ.Add( tabNodeBatSZ1, 0, wx.EXPAND, 5 )
         
         
        tabNodeSZ1.Add( tabNodeBatSZ, 0, wx.EXPAND, 5 )
         
        tabNodeSolarSZ = wx.StaticBoxSizer( wx.StaticBox( self.notebook_1_pane_1, wx.ID_ANY, u"Слънчев панел" ), wx.VERTICAL )
         
        tabNodeSolarSZ1 = wx.BoxSizer( wx.VERTICAL )
         
        self.tabNodeSolarBmp = wx.StaticBitmap( self.notebook_1_pane_1, wx.ID_ANY, wx.Bitmap( u".//images/solar.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeSolarSZ1.Add( self.tabNodeSolarBmp, 0, wx.ALL, 5 )
         
        tabNodeSolarSZ2 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeSolarL1 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Напрежение:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeSolarL1.Wrap( -1 )
        tabNodeSolarSZ2.Add( self.tabNodeSolarL1, 0, wx.ALL, 5 )
         
        self.tabNodeSolarL2 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeSolarL2.Wrap( -1 )
        self.tabNodeSolarL2.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
         
        tabNodeSolarSZ2.Add( self.tabNodeSolarL2, 0, wx.ALL, 5 )
         
        self.tabNodeSolarL3 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Vdc", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeSolarL3.Wrap( -1 )
        tabNodeSolarSZ2.Add( self.tabNodeSolarL3, 0, wx.ALL, 5 )
         
         
        tabNodeSolarSZ1.Add( tabNodeSolarSZ2, 0, wx.EXPAND, 5 )
         
        tabNodeSolarSZ3 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeSolarG1 = wx.Gauge( self.notebook_1_pane_1, wx.ID_ANY, 21, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        self.tabNodeSolarG1.SetValue( 0 ) 
        tabNodeSolarSZ3.Add( self.tabNodeSolarG1, 1, wx.ALL, 5 )
         
         
        tabNodeSolarSZ1.Add( tabNodeSolarSZ3, 1, wx.EXPAND, 5 )
         
         
        tabNodeSolarSZ.Add( tabNodeSolarSZ1, 0, wx.EXPAND, 5 )
         
         
        tabNodeSZ1.Add( tabNodeSolarSZ, 0, wx.EXPAND, 5 )
         
        tabNodeLedSZ = wx.StaticBoxSizer( wx.StaticBox( self.notebook_1_pane_1, wx.ID_ANY, u"LED" ), wx.VERTICAL )
         
        tabNodeLedSZ1 = wx.BoxSizer( wx.VERTICAL )
         
        self.tabNodeLedBmp = wx.StaticBitmap( self.notebook_1_pane_1, wx.ID_ANY, wx.Bitmap( u".//images/led.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeLedSZ1.Add( self.tabNodeLedBmp, 0, wx.ALL, 5 )
         
        tabNodeLedSZ2 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeLedL1 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Състояние:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeLedL1.Wrap( -1 )
        tabNodeLedSZ2.Add( self.tabNodeLedL1, 0, wx.ALL, 5 )
         
        self.tabNodeLedL2 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"ИЗКЛ.", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeLedL2.Wrap( -1 )
        self.tabNodeLedL2.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
         
        tabNodeLedSZ2.Add( self.tabNodeLedL2, 0, wx.ALL, 5 )
        tabNodeLedSZ1.Add( tabNodeLedSZ2, 0, wx.EXPAND, 5 )

        tabNodeLedSZ.Add( tabNodeLedSZ1, 0, wx.EXPAND, 5 )
         
        tabNodeSZ1.Add( tabNodeLedSZ, 1, wx.EXPAND, 5 )

        tabNodeLedSZ3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.tabNodeLedTog = wx.ToggleButton( self.notebook_1_pane_1, wx.ID_ANY, u"Включи", wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeLedSZ3.Add( self.tabNodeLedTog, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        tabNodeLedSZ1.Add( tabNodeLedSZ3, 1, wx.EXPAND, 5 )
         
        tabNodeShockSZ = wx.StaticBoxSizer( wx.StaticBox( self.notebook_1_pane_1, wx.ID_ANY, u"Шок сензор" ), wx.VERTICAL )
         
        tabNodeShockSZ1 = wx.BoxSizer( wx.VERTICAL )
         
        self.tabNodeShockBmp = wx.StaticBitmap( self.notebook_1_pane_1, wx.ID_ANY, wx.Bitmap( u".//images/tornado.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeShockSZ1.Add( self.tabNodeShockBmp, 0, wx.ALL, 5 )
         
        tabNodeShockSZ2 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeShockL1 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Състояние:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeShockL1.Wrap( -1 )
        tabNodeShockSZ2.Add( self.tabNodeShockL1, 0, wx.ALL, 5 )
         
        self.tabNodeShockL2 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"ИЗКЛ.", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeShockL2.Wrap( -1 )
        self.tabNodeShockL2.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
         
        tabNodeShockSZ2.Add( self.tabNodeShockL2, 0, wx.ALL, 5 )
        
        tabNodeShockSZ1.Add( tabNodeShockSZ2, 1, wx.EXPAND, 5 )
        
        tabNodeShockSZ3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.tabNodeShockTog = wx.ToggleButton( self.notebook_1_pane_1, wx.ID_ANY, u"Включи", wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeShockSZ3.Add( self.tabNodeShockTog, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        
        tabNodeShockSZ1.Add( tabNodeShockSZ3, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
         
        tabNodeShockSZ.Add( tabNodeShockSZ1, 0, wx.EXPAND, 5 )
         
        tabNodeSZ1.Add( tabNodeShockSZ, 1, wx.EXPAND, 5 )
         
        tabNodeInfoSZ = wx.StaticBoxSizer( wx.StaticBox( self.notebook_1_pane_1, wx.ID_ANY, u" Информация " ), wx.VERTICAL )
         
        tabNodeInfoSZ1 = wx.BoxSizer( wx.VERTICAL )
         
        self.tabNodeInfoBmp = wx.StaticBitmap( self.notebook_1_pane_1, wx.ID_ANY, wx.Bitmap( u".//images/information.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        tabNodeInfoSZ1.Add( self.tabNodeInfoBmp, 0, wx.ALL, 5 )
         
        tabNodeInfoSZ2 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeInfoL1 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Версия:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL1.Wrap( -1 )
        tabNodeInfoSZ2.Add( self.tabNodeInfoL1, 0, wx.ALL, 5 )
         
        self.tabNodeInfoL2 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"1.0", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL2.Wrap( -1 )
        self.tabNodeInfoL2.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
         
        tabNodeInfoSZ2.Add( self.tabNodeInfoL2, 0, wx.ALL, 5 )
         
        tabNodeInfoSZ1.Add( tabNodeInfoSZ2, 1, wx.EXPAND, 5 )
         
        tabNodeInfoSZ3 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeInfoL3 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"HW:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL3.Wrap( -1 )
        tabNodeInfoSZ3.Add( self.tabNodeInfoL3, 0, wx.ALL, 5 )
          
        self.tabNodeInfoL4 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"XXXXXX", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL4.Wrap( -1 )
        self.tabNodeInfoL4.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
          
        tabNodeInfoSZ3.Add( self.tabNodeInfoL4, 0, wx.ALL, 5 )
         
        tabNodeInfoSZ1.Add( tabNodeInfoSZ3, 1, wx.EXPAND, 5 )
         
        tabNodeInfoSZ4 = wx.BoxSizer( wx.HORIZONTAL )
         
        self.tabNodeInfoL5 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"SW:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL5.Wrap( -1 )
        tabNodeInfoSZ4.Add( self.tabNodeInfoL5, 0, wx.ALL, 5 )
          
        self.tabNodeInfoL6 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"XXXXXX", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL6.Wrap( -1 )
        self.tabNodeInfoL6.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
          
        tabNodeInfoSZ4.Add( self.tabNodeInfoL6, 0, wx.ALL, 5 )
         
        tabNodeInfoSZ1.Add( tabNodeInfoSZ4, 1, wx.EXPAND, 5 )
        
        tabNodeInfoSZ5 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.tabNodeInfoL7 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"Име:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL7.Wrap( -1 )
        self.tabNodeInfoL7.SetFont( wx.Font( 10, 74, 90, 90, False, "Sans" ) )
        
        tabNodeInfoSZ5.Add( self.tabNodeInfoL7, 0, wx.ALL, 5 )
        
        self.tabNodeInfoL8 = wx.StaticText( self.notebook_1_pane_1, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tabNodeInfoL8.Wrap( -1 )
        self.tabNodeInfoL8.SetFont( wx.Font( 10, 74, 90, 92, False, "Sans" ) )
        
        tabNodeInfoSZ5.Add( self.tabNodeInfoL8, 0, wx.ALL, 5 )
        
        tabNodeInfoSZ1.Add( tabNodeInfoSZ5, 1, wx.EXPAND, 5 )
         
        tabNodeInfoSZ.Add( tabNodeInfoSZ1, 0, wx.EXPAND, 5 )
         
        tabNodeSZ1.Add( tabNodeInfoSZ, 1, wx.EXPAND, 5 )
         
        tabNodeSZ.Add( tabNodeSZ1, 1, wx.EXPAND, 5 )
        
        self.SetSizerAndFit(tabNodeSZ )

#         self.Layout()
        
        self.Centre( wx.BOTH )

# End Notebook Panel 1

# Begin Notebook Panel 2

        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.mainTextChangeLog = wx.TextCtrl(self.notebook_1_pane_2, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_AUTO_URL| wx.TE_READONLY | wx.TE_BESTWRAP)
        self.mainTextChangeLog.LoadFile(".//ChangeLog.txt")
        
# End Notebook Panel 2

# Begin Notebook Panel 3

        self.notebook_1_pane_3 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.mainLCtrlHistory = wx.ListCtrl( self.notebook_1_pane_3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_REPORT|wx.LC_SORT_DESCENDING )
        self.mainLCtrlHistory.InsertColumn(0, u"Дата и час:", width=100)
        self.mainLCtrlHistory.InsertColumn(1, u"Бележка", width=400)
        self.mainNBHLnote = wx.StaticText( self.notebook_1_pane_3, wx.ID_ANY, u"Бележка:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.mainTCtrlHistroy = wx.TextCtrl( self.notebook_1_pane_3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_AUTO_URL|wx.TE_WORDWRAP )
        self.mainTCtrlHistroy.SetMinSize( wx.Size( -1,-1 ) )
        self.mainCheckBoxVersion = wx.CheckBox( self.notebook_1_pane_3, wx.ID_ANY, u"Промяна на версията", wx.DefaultPosition, wx.DefaultSize, wx.CHK_2STATE )   
        mainCBoxVersionChoices = ['None','1.0','2.0','3.0','4.0','5.0']
        self.mainCBoxVersion = wx.ComboBox( self.notebook_1_pane_3, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, mainCBoxVersionChoices, wx.CB_READONLY|wx.CB_SORT )
        self.mainCBoxVersion.SetSelection( 0 )
        self.mainCBoxVersion.SetToolTipString( u"изберете версия на управлението" )
        self.mainCBoxVersion.SetMinSize( wx.Size( 100,-1 ) )
        self.mainSTextVersion = wx.StaticText( self.notebook_1_pane_3, wx.ID_ANY, u"Версия:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.mainSTextVersion.Wrap( -1 )
        self.mainNBHBSave = wx.Button( self.notebook_1_pane_3, wx.ID_SAVE, u"")
        self.mainNBHBSpare = wx.Button( self.notebook_1_pane_3, wx.ID_ANY, u"Резерв")
        self.mainNBHBSpare.Hide()
        self.mainNBHLnote.Wrap( -1 )
        
# End Notebook Panel 3

        self.notebook_1_pane_4 = wx.Panel(self.notebook_1, wx.ID_ANY)
# End         
        self.tabNodeButSave = wx.Button(self, wx.ID_SAVE, (""))
        self.tabNodeButCancel = wx.Button(self, wx.ID_CANCEL, ("Отмяна"))
        self.tabNodeButSpare = wx.Button(self, wx.ID_ANY, ("Резерв"))
        self.tabNodeButSpare.Hide()
        
        self.mainCBoxVersion.Disable()
        self.mainSTextVersion.Disable()

# End Buttons and split windows section --------------------------------

# Create StatusBar start
        self.SCS_Frame_statusbar = self.CreateStatusBar(3, 0)
        self.SCS_Frame_statusbar.SetStatusWidths([-1, -1, 100])
        self.SCS_Frame_statusbar.SetStatusText("Свързан",2)
# Create StatusBar end

        self.__set_properties()
        self.__do_layout()
        
# Bindings

        self.Bind(wx.EVT_BUTTON, self.OnButtonStartPressed, self.mainButtonStart)
        self.Bind(wx.EVT_BUTTON, self.OnButtonStopPressed, self.mainButtonStop)
        self.Bind(wx.EVT_BUTTON, self.OnButtonStopAllPressed, self.mainButtonStopAll)
        self.Bind(wx.EVT_BUTTON, self.OnButtonPausePressed, self.mainButtonPause)
        self.Bind(wx.EVT_BUTTON, self.OnButtonTestPressed, self.mainButtonTest)
        self.Bind(wx.EVT_BUTTON, self.OnButtonHSavePressed, self.mainNBHBSave)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckHistory, self.mainCheckBoxVersion)
        self.Bind(wx.EVT_BUTTON, self.OnButtonLedCtrlPressed, self.mainLedButtonCtrl)
        
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleShock, self.tabNodeShockTog)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleLed, self.tabNodeLedTog)
        
    def __set_properties(self):
        self.mainLCtrlHistory.SetMinSize((500,420))
        self.tabNodeButSave.Disable()
        self.tabNodeButCancel.Disable()
        self.tabNodeButSpare.Disable()
        
    def __do_layout(self):
        # Sizers for Split Panels
        mainMainSizer = wx.BoxSizer(wx.VERTICAL)  # glawen
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL) # tozi s butonite save ++
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL) # tozi s notebooka
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL) # goren panel s butoni
        sizer_4.Add(self.mainButtonStart, 0, wx.ALL, 5)
        sizer_4.Add(self.mainButtonStop, 0, wx.ALL, 5)
        sizer_4.Add(self.mainButtonStopAll, 0, wx.ALL, 5)
        sizer_4.Add(self.mainButtonPause, 0, wx.ALL, 5)
        sizer_4.Add(self.mainButtonTest,0,wx.ALL, 5)
        sizer_4.Add(self.mainLedButtonCtrl,0,wx.ALL, 5)
        sizer_4.Add((20, 20), 1, wx.EXPAND, 0)
        
        mainMainSizer.Add(sizer_4, 0, wx.ALL | wx.EXPAND, 0)
        
        sizer_5.Add(self.Sp_TreeCtrl, 1, wx.EXPAND, 0)
        self.window_1_pane_1.SetSizer(sizer_5)
    
        
        self.notebook_1.AddPage(self.notebook_1_pane_1, ("Настройки"))

        tabChangeLog = wx.BoxSizer(wx.VERTICAL)
        tabChangeLog.Add(self.mainTextChangeLog,1,wx.EXPAND, 3)
        self.notebook_1_pane_2.SetSizer(tabChangeLog)
        self.notebook_1.AddPage(self.notebook_1_pane_2, text = "Списък с промени")
        
        tabSZHistory = wx.BoxSizer(wx.VERTICAL)
        tabSZHistory.Add( self.mainLCtrlHistory, 0, wx.ALL|wx.EXPAND, 5 )
        tabSZHistory.Add( self.mainNBHLnote, 0, wx.ALL, 5 )
        tabSZHistory.Add( self.mainTCtrlHistroy, 0, wx.ALL|wx.EXPAND, 5 )
        tabSZHistory.Add(self.mainCheckBoxVersion, 0, wx.ALL, 5)
        
        tabSZHistVer = wx.BoxSizer(wx.HORIZONTAL)
        tabSZHistVer.Add(self.mainSTextVersion, 0, wx.ALL, 5)
        tabSZHistVer.Add( self.mainCBoxVersion, 0, wx.ALL, 5 )
        tabSZHistory.Add(tabSZHistVer, 1, wx.EXPAND, 5 )
        
        tabSZHistoryButtons = wx.BoxSizer(wx.HORIZONTAL)
        tabSZHistoryButtons.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )        
        tabSZHistoryButtons.Add( self.mainNBHBSave, 0, wx.ALL, 5 )
        tabSZHistoryButtons.Add( self.mainNBHBSpare, 0, wx.ALL, 5 )
        tabSZHistory.Add(tabSZHistoryButtons, 2, wx.EXPAND, 5 )
             
        self.notebook_1_pane_3.SetSizer(tabSZHistory)
        self.notebook_1.AddPage(self.notebook_1_pane_3, text = "История на операциите")
        
        sizer_6.Add(self.notebook_1, 1, wx.EXPAND, 0)
        self.window_1_pane_2.SetSizer(sizer_6)
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2)
        
        mainMainSizer.Add(self.window_1, 1, wx.ALL | wx.EXPAND, 3)
        
        sizer_7.Add((20, 20), 1, wx.EXPAND, 0)
        sizer_7.Add(self.tabNodeButSave, 0, wx.ALL, 5)
        sizer_7.Add(self.tabNodeButCancel, 0, wx.ALL, 5)
        sizer_7.Add(self.tabNodeButSpare, 0, wx.ALL, 5)
        mainMainSizer.Add(sizer_7, 0, wx.EXPAND, 0)
        self.SetSizer(mainMainSizer)
        mainMainSizer.Fit(self)
        self.Layout()
        
    def countAllNodes(self):
        """
        """
        global FACILITY_MAP_
        
        self.buildFacilityMap_()

        nodeCount = 0
       
        for cell in FACILITY_MAP_:
            for phase in FACILITY_MAP_[cell]:
                for node in FACILITY_MAP_[cell][phase]:
                    nodeCount += 1
                    
        return nodeCount

    def testOneNode(self, cell, phase, node, longAddress):
        """
        """
        littleList = []
        
        littleList.append(cell)
        littleList.append(phase)
        littleList.append(node)
        littleList.append(longAddress)
                    
        if longAddress != 'None':
            state = xbee_is(longAddress.decode('hex'))
            state = xbee_is(longAddress.decode('hex'))
            if state:
                littleList.append('намерено')
            else:
                littleList.append('не е намерено')
        else:
            littleList.append('няма монтирано управление!')
            state = {}
                        
        if state:
            try:
                if state.get('parameter')[0].get('dio-0'):
                    littleList.append('ВКЛ.') 
                else:
                    littleList.append('ИЗКЛ.')
            except (KeyError, TypeError):
                pass
                        
            try:
                if state.get('parameter')[0].get('dio-1'):
                    littleList.append('ВКЛ.') 
                else:
                    littleList.append('ИЗКЛ.')
            except (KeyError, TypeError):
                pass
                        
            try:
                if state.get('parameter')[0].get('dio-4'):
                    littleList.append('ВКЛ.') 
                else:
                    littleList.append('ИЗКЛ.')
            except (KeyError, TypeError):
                pass                      

            try:
                num1=(state.get('parameter')[0].get('adc-3')/float(1023))*6.5+6.8
                littleList.append(str(round(num1,2)))
            except (KeyError, TypeError):
                littleList.append('N/A')
                
            try:
                num2=(state.get('parameter')[0].get('adc-2')/float(1023))*6.5+6.8
                littleList.append(str(round(num2,2)))
            except (KeyError, TypeError):
                littleList.append('N/A')
        else:
            littleList.append('N/A')
            littleList.append('N/A')
            littleList.append('N/A')
            littleList.append('N/A')
            littleList.append('N/A')
       
        return littleList        
        
    def testAllNodes(self):
        """
            Tests all Nodes and returns list with result
        """
        global FACILITY_MAP_        
        self.buildFacilityMap_()
        
        sortAll = []
        currValue = 0
        msg = [0,0]
        nodeCount = self.countAllNodes()
        
        for cell in FACILITY_MAP_:
            for phase in FACILITY_MAP_[cell]:
                for node in FACILITY_MAP_[cell][phase]:
                    longAddress = FACILITY_MAP_[cell][phase][node]
                    
                    sortAll.append(self.testOneNode(cell, phase, node, longAddress))
        
        pub.sendMessage(("show.testGauge"), state = [1,1])

        return sortAll

    def buildFacilityMap_(self):
        """
            New procedure for whole facility
        """
        global FACILITY_TREE_XML
        global FACILITY_MAP_
        global GROUPS_DICT_
        FACILITY_MAP_ = {}
        GROUPS_DICT_ = {}
        phase_dict = {}
        node_dict = {}
        node_list = []
        groups_gen_dict = {}
                      
        for wdf_cells in FACILITY_TREE_XML.findall('cell'):
            for wdf_phases in wdf_cells:
                for wdf_nodes in wdf_phases:
                    n_name = wdf_nodes.get('name')
                    a_name = wdf_nodes.text.strip()
                    node_dict[n_name]=a_name
                phase_dict[wdf_phases.get('name')]=node_dict
                node_dict = {}
            FACILITY_MAP_[wdf_cells.get('name')] = phase_dict
            phase_dict = {}
        print FACILITY_MAP_
        
        phase_dict = {}
                
        for wdf_groups in FACILITY_TREE_XML.iterfind('groups'):
            for wdf_group in wdf_groups:
                for wdf_node in wdf_group:
                    node_list.append(wdf_node.text)
                groups_gen_dict[wdf_group.get('name')] = node_list
                node_list=[]        
            phase_dict[wdf_groups.get('phase')] = groups_gen_dict
            GROUPS_DICT_[wdf_groups.get('cell')] = phase_dict
            groups_gen_dict = {}
            phase_dict = {}
        print "GR_:>", GROUPS_DICT_
        
        return FACILITY_MAP_
    
    def lightAllLeds(self, state):
        """
        """
        global FACILITY_MAP
        global FACILITY_MAP2
    
        self.buildFacilityMap('Cell 1','Phase 1')
        if state == 'OFF':
            self.SCS_Frame_statusbar.SetStatusText("Протича изключване на всички LED от Клетка 1...",0)
        if state == 'ON':
            self.SCS_Frame_statusbar.SetStatusText("Протича включване на всички LED от Клетка 1...",0)
        for node in FACILITY_MAP:
            print FACILITY_MAP.get(node)
            if FACILITY_MAP.get(node)!='None':
                xbee_pin(FACILITY_MAP.get(node).decode('hex'),'D1',state)
                xbee_pin(FACILITY_MAP.get(node).decode('hex'),'D1',state)
                xbee_is(FACILITY_MAP.get(node).decode('hex'))
         
        self.buildFacilityMap2('Cell 2', 'Phase 1')
        if state == 'OFF':
            self.SCS_Frame_statusbar.SetStatusText("Протича изключване на всички LED от Клетка 2...",0)
        if state == 'ON':
            self.SCS_Frame_statusbar.SetStatusText("Протича включване на всички LED от Клетка 2...",0)
        for node in FACILITY_MAP2:
            print FACILITY_MAP2.get(node)
            if FACILITY_MAP2.get(node)!='None':
                xbee_pin(FACILITY_MAP2.get(node).decode('hex'),'D1',state)
                xbee_pin(FACILITY_MAP2.get(node).decode('hex'),'D1',state)
                xbee_is(FACILITY_MAP2.get(node).decode('hex'))
                
        self.SCS_Frame_statusbar.SetStatusText("",0)
        
    def OnHiddenDiscovery(self, event):
        """
        """
        print "Skrit find..."
        if ISALLSTOPPED:
            global hiddenDiscoveryThread
            hiddenDiscoveryThread.start()
            print "On hidden" , threading.currentThread().getName()
            return
        else:
            SCS_ShowMessage("Автоматичния режим е стартиран! Първо спрете всички управления!",0) 
        return
    
        node_discovery()
        q = Queue.Queue()
        if ISALLSTOPPED:
            threadDiscovery = threading.Thread(target = hiddenNodediscovery, args=(q,))
            threadDiscovery.daemon = True
            threadDiscovery.start()
            result = q.get()
            print "Towa e threading resultat: ", result
        else:
            print "W momenta rabotqt uprawleniq!!!"
            
    def OnHiddenXbeeChangeState(self, event):
        
        global hiddenXbeeChangeStateQueue
        
        hiddenXbeeCS = hiddenXbeeChangeStateThread('0013A200406E980D', 'D0', 'ON', hiddenXbeeChangeStateQueue)
        hiddenXbeeCS.start()
        print "OnHiddenXbeeChangeState: ", threading.currentThread().getName()
        while not hiddenXbeeChangeStateQueue.empty():
            print "Queue: ", hiddenXbeeChangeStateQueue.get()
        print "While is ended"
        
#         stateDict = hiddenDiscoveryThread('0013A200406E980F', 'D0', 'ON') #0013A200406E980F
#         print stateDict

        
    def OnHiddenXbeePin(self, event):
        print "HXBPIN"


    def OnButtonLedCtrlPressed(self, event):
        """
        """
        global ISLEDON
        
        if not ISLEDON:
            self.mainLedButtonCtrl.SetBitmapLabel(wx.Bitmap( u".//images/light_bulb_on.png", wx.BITMAP_TYPE_ANY ))
            msg = "Моля, почакайте, извършва се изключване на всички LED..."
            busyDlg = wx.BusyInfo(msg, self)            
            self.lightAllLeds('ON')
            ISLEDON = True
            busyDlg = None
        else:
            self.mainLedButtonCtrl.SetBitmapLabel(wx.Bitmap( u".//images/light_bulb_off.png", wx.BITMAP_TYPE_ANY ))
            msg = "Моля, почакайте, извършва се изключване на всички LED..."
            busyDlg = wx.BusyInfo(msg, self)
            self.lightAllLeds('OFF')            
            ISLEDON = False
            busyDlg = None            
        
    def OnCheckHistory(self, event):
        """
        """
        if event.IsChecked():
            self.mainCBoxVersion.Enable()
            self.mainSTextVersion.Enable()
        else:
            self.mainCBoxVersion.Disable()
            self.mainSTextVersion.Disable()
        event.Skip()
        
    def onTest(self, event):
        """
        """
        
#         global TREECTRL_ELEMENT_SELECTED
#         global TREECTRL_PARENT_SELECTED
#         global TREECTRL_UPPARENT_SELECTED
        global ISALLSTOPPED
        
        dlg = testResultDlgHtml(wx.GetApp().TopWindow, [], ISALLSTOPPED)
        dlg.ShowModal()
        dlg.Destroy()
        
    def onEnterWindow(self, event):
        """
        """
        
        global ISFACILITYUPDATED
        
        if ISFACILITYUPDATED:
            self.Sp_TreeCtrl.loadXMLtoTree()
            ISFACILITYUPDATED = 0
        else:
            pass
            
    def showItemHistory(self, events_d):
        """
        """
        
        self.mainLCtrlHistory.DeleteAllItems()
        
        try:
            if events_d:
                if events_d != {}:
                    sorted_events = events_d.items()
                    sorted_events.sort()
                    self.mainLCtrlHistory.DeleteAllItems()
                    self.mainTCtrlHistroy.Clear()
                    for dates, event in sorted_events:
                        pos = self.mainLCtrlHistory.InsertStringItem(0, dates)
                        self.mainLCtrlHistory.SetStringItem(pos, 1, unicode(event))
        except:
            try:
                if events_d != {}:
                    sorted_events = events_d.items()
                    sorted_events.sort()
                    self.mainLCtrlHistory.DeleteAllItems()
                    self.mainTCtrlHistroy.Clear()
                    for dates, event in sorted_events:
                        pos = self.mainLCtrlHistory.InsertStringItem(0, dates)
                        self.mainLCtrlHistory.SetStringItem(pos, 1, unicode(event))
            except:
                print "Value error!"
                
    def showItemVersion(self, infob):
        """
        """
       
        try:
            if infob['version']!='':
                self.tabNodeInfoL2.SetLabel(u"%s" %infob['version'])
            else:
                self.tabNodeInfoL2.SetLabel("N/A")
        except AttributeError:
            if infob['version']!='':
                self.tabNodeInfoL2.SetLabel(u"%s" %infob['version'])
            else:
                self.tabNodeInfoL2.SetLabel("N/A")

        try:
            if infob['name']!='':
                self.tabNodeInfoL8.SetLabel(u"%s" %infob['name'])
            else:
                self.tabNodeInfoL8.SetLabel("N/A")
        except AttributeError:
            if infob['name']!='':
                self.tabNodeInfoL8.SetLabel(u"%s" %infob['name'])
            else:
                self.tabNodeInfoL8.SetLabel("N/A")                
                    

    def showItemInfo(self, state):
        """
        """
        try:       
            if state:
                if state['DO0']==True:
                    self.tabNodeValveBmp.Enable()
                    self.tabNodeValveL1.Enable()
                    self.tabNodeValveL2.Enable()
                    self.tabNodeValveL2.SetLabel("ВКЛ.")
                    self.tabNodeValveL4.Enable()
                else:
                    self.tabNodeValveBmp.Enable()
                    self.tabNodeValveL1.Enable()
                    self.tabNodeValveL2.Enable()
                    self.tabNodeValveL2.SetLabel("ИЗКЛ.")
                    self.tabNodeValveL4.Enable()
                
                if state['DO1']==True:
                    self.tabNodeLedBmp.Enable()
                    self.tabNodeLedL1.Enable()
                    self.tabNodeLedL2.Enable()
                    self.tabNodeLedL2.SetLabel("ВКЛ.")
                    self.tabNodeLedTog.SetValue(0)
                    self.tabNodeLedTog.Enable()
                else:
                    self.tabNodeLedBmp.Enable()
                    self.tabNodeLedL1.Enable()
                    self.tabNodeLedL2.Enable()
                    self.tabNodeLedL2.SetLabel("ИЗКЛ.")
                    self.tabNodeLedTog.SetValue(1)
                    self.tabNodeLedTog.Enable()

                if state['DI4']==False:
                    self.tabNodeValveL3.Enable()
                    self.tabNodeValveL4.Enable()
                    self.tabNodeValveL4.SetLabel("ВКЛ.")
                else:
                    self.tabNodeValveL3.Enable()
                    self.tabNodeValveL4.Enable()
                    self.tabNodeValveL4.SetLabel("ИЗКЛ.")                
            
                realBatVoltage = float(state['ADC3'])
            
                voltageSign = "%.2f"
                self.tabNodeBatL1.Enable()
                self.tabNodeBatL2.SetLabel(voltageSign %realBatVoltage)
                self.tabNodeBatL2.Enable()
                self.tabNodeBatL3.Enable()
                self.tabNodeBatBmp.Enable()
                self.tabNodeBatG1.SetValue(realBatVoltage)
                
                realSolarVoltage = float(state['ADC2'])
            
                voltageSign = "%.2f"
                self.tabNodeSolarL1.Enable()
                self.tabNodeSolarL2.SetLabel(voltageSign %realSolarVoltage)
                self.tabNodeSolarL2.Enable()
                self.tabNodeSolarL3.Enable()
                self.tabNodeSolarBmp.Enable()
                self.tabNodeSolarG1.SetValue(realSolarVoltage)

            else:
                self.tabNodeValveBmp.Disable()
                self.tabNodeValveL1.Disable()
                self.tabNodeValveL2.Disable()
                self.tabNodeValveL3.Disable()
                self.tabNodeValveL4.Disable()
                self.tabNodeBatBmp.Disable()
                self.tabNodeBatG1.SetValue(0)
                self.tabNodeBatG1.Disable()
                self.tabNodeBatL1.Disable()
                self.tabNodeBatL2.Disable()
                self.tabNodeBatL3.Disable()
                self.tabNodeLedBmp.Disable()
                self.tabNodeLedL1.Disable()
                self.tabNodeLedL2.Disable()
                self.tabNodeLedTog.Disable()
                self.tabNodeSolarBmp.Disable()
                self.tabNodeSolarG1.SetValue(0)
                self.tabNodeSolarG1.Disable()
                self.tabNodeSolarL1.Disable()
                self.tabNodeSolarL2.Disable()
                self.tabNodeSolarL3.Disable()
                self.tabNodeShockBmp.Disable()
                self.tabNodeShockL1.Disable()
                self.tabNodeShockL2.Disable()
                self.tabNodeShockTog.Disable()
                
        except AttributeError:
            
            if state:
                if state['DO0']==True:
                    self.tabNodeValveBmp.Enable()
                    self.tabNodeValveL1.Enable()
                    self.tabNodeValveL2.Enable()
                    self.tabNodeValveL2.SetLabel("ВКЛ.")
                    self.tabNodeValveL4.Enable()
                else:
                    self.tabNodeValveBmp.Enable()
                    self.tabNodeValveL1.Enable()
                    self.tabNodeValveL2.Enable()
                    self.tabNodeValveL2.SetLabel("ИЗКЛ.")
                    self.tabNodeValveL4.Enable()
                
                if state['DO1']==True:
                    self.tabNodeLedBmp.Enable()
                    self.tabNodeLedL1.Enable()
                    self.tabNodeLedL2.Enable()
                    self.tabNodeLedL2.SetLabel("ВКЛ.")
                    self.tabNodeLedTog.SetValue(1)
                    self.tabNodeLedTog.Enable()
                else:
                    self.tabNodeLedBmp.Enable()
                    self.tabNodeLedL1.Enable()
                    self.tabNodeLedL2.Enable()
                    self.tabNodeLedL2.SetLabel("ИЗКЛ.")
                    self.tabNodeLedTog.SetValue(0)
                    self.tabNodeLedTog.Enable()

                if state['DI2']==False:
                    self.tabNodeValveL3.Enable()
                    self.tabNodeValveL4.Enable()
                    self.tabNodeValveL4.SetLabel("ВКЛ.")
                else:
                    self.tabNodeValveL3.Enable()
                    self.tabNodeValveL4.Enable()
                    self.tabNodeValveL4.SetLabel("ИЗКЛ.")               
                        
                realBatVoltage = float(state['ADC3'])
            
                voltageSign = "%.2f"
                self.tabNodeBatL1.Enable()
                self.tabNodeBatL2.SetLabel(voltageSign %realBatVoltage)
                self.tabNodeBatL2.Enable()
                self.tabNodeBatL3.Enable()
                self.tabNodeBatBmp.Enable()
                self.tabNodeBatG1.SetValue(realBatVoltage)
                
                realSolarVoltage = float(state['ADC2'])
            
                voltageSign = "%.2f"
                self.tabNodeSolarL1.Enable()
                self.tabNodeSolarL2.SetLabel(voltageSign %realSolarVoltage)
                self.tabNodeSolarL2.Enable()
                self.tabNodeSolarL3.Enable()
                self.tabNodeSolarBmp.Enable()
                self.tabNodeSolarG1.SetValue(realSolarVoltage)                
            else:
                self.tabNodeValveBmp.Disable()
                self.tabNodeValveL1.Disable()
                self.tabNodeValveL2.Disable()
                self.tabNodeValveL3.Disable()
                self.tabNodeValveL4.Disable()
                self.tabNodeBatBmp.Disable()
                self.tabNodeBatG1.SetValue(0)
                self.tabNodeBatG1.Disable()
                self.tabNodeBatL1.Disable()
                self.tabNodeBatL2.Disable()
                self.tabNodeBatL3.Disable()
                self.tabNodeLedBmp.Disable()
                self.tabNodeLedL1.Disable()
                self.tabNodeLedL2.Disable()
                self.tabNodeLedTog.Disable()
                self.tabNodeSolarBmp.Disable()
                self.tabNodeSolarG1.SetValue(0)
                self.tabNodeSolarG1.Disable()
                self.tabNodeSolarL1.Disable()
                self.tabNodeSolarL2.Disable()
                self.tabNodeShockBmp.Disable()
                self.tabNodeShockL1.Disable()
                self.tabNodeShockL2.Disable()
                self.tabNodeShockTog.Disable()                    

    def buildFacilityMap(self, cell_name, phase_name):
        """
            Builds facility map on Cell 1
        """
        
        global FACILITY_TREE_XML
        global FACILITY_MAP
               
        for wdf_cells in FACILITY_TREE_XML.iterfind('cell[@name="%s"]' %cell_name):
            for wdf_phase in wdf_cells.iterfind('phase[@name="%s"]' %phase_name):
                for wdf_node in wdf_phase:
                    FACILITY_MAP[wdf_node.get('name')]=wdf_node.text.strip()
        
    def buildFacilityMap2(self, cell_name, phase_name):
        """
            Builds facility map on Cell 2
        """
        
        global FACILITY_TREE_XML
        global FACILITY_MAP2
               
        for wdf_cells in FACILITY_TREE_XML.iterfind('cell[@name="%s"]' %cell_name):
            for wdf_phase in wdf_cells.iterfind('phase[@name="%s"]' %phase_name):
                for wdf_node in wdf_phase:
                    FACILITY_MAP2[wdf_node.get('name')]=wdf_node.text.strip()

    def processingGroups(self, cell_name, phase_name):
        """ 
            Processing Groups and make GROUPS_DICT
        """
        global GROUPS_DICT
        global GROUPS_DICT2
     
        if cell_name == 'Cell 1':
            GROUPS_DICT={}
            node_list=[]
            for wdf_groups in FACILITY_TREE_XML.iterfind('groups'):
                if wdf_groups.get('cell')==cell_name and wdf_groups.get('phase')==phase_name and len(wdf_groups)<>0:
                    for wdf_group in wdf_groups:
                        for wdf_node in wdf_group:
                            node_list.append(wdf_node.text)
                        GROUPS_DICT[wdf_group.get('name')]=node_list
                        node_list=[]
                else:
                    pass
                
        if cell_name == 'Cell 2':
            GROUPS_DICT2={}
            node_list=[]
            for wdf_groups in FACILITY_TREE_XML.iterfind('groups'):
                if wdf_groups.get('cell')==cell_name and wdf_groups.get('phase')==phase_name and len(wdf_groups)<>0:
                    for wdf_group in wdf_groups:
                        for wdf_node in wdf_group:
                            node_list.append(wdf_node.text)
                        GROUPS_DICT2[wdf_group.get('name')]=node_list
                        node_list=[]
                else:
                    pass
                            
        print "GD:>", GROUPS_DICT
        print "GD2:>", GROUPS_DICT2
        
        if len(GROUPS_DICT)<>0 or len(GROUPS_DICT2):
            return True
        else:
            return False
        
    def stopGroup(self, itemList):
        
        global PREVIOUS_GROUP
        
        if itemList:
            for node in itemList:
                print "Now stopping %s" %node
                xbeeState = hiddenXbeeChangeState(node,"D0","OFF")
                if xbeeState == 1:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 2:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.disconnectedXbee)            
                elif xbeeState == 3:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.RED)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.startedXbee)
                elif xbeeState == 4:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.stoppedXbee)            
                elif xbeeState == 5:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 6:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 7:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 8:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)
                else:
#             try:
#                 self.showItemInfo(False,{})
#             except TypeError:
#                 pass               
#             SCS_ShowMessage("Xbee: Изтекло време за отговор!",0)
#             self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.disconnectedXbee)
        
        PREVIOUS_GROUP = []
        
    def stopGroup2(self, itemList):
        
        global PREVIOUS_GROUP2
        
        if itemList:
            for node in itemList:
                print "Now stopping %s" %node
                xbeeState = hiddenXbeeChangeState(node,"D0","OFF")
                if xbeeState == 1:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 2:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.disconnectedXbee)            
                elif xbeeState == 3:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.RED)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.startedXbee)
                elif xbeeState == 4:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.stoppedXbee)            
                elif xbeeState == 5:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 6:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 7:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 8:
                    self.Sp_TreeCtrl.changeItemColor(node, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.errorXbee)
                else:
#             try:
#                 self.showItemInfo(False,{})
#             except TypeError:
#                 pass               
#             SCS_ShowMessage("Xbee: Изтекло време за отговор!",0)
#             self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(node, self.Sp_TreeCtrl.disconnectedXbee)                
        
        PREVIOUS_GROUP2 = []
        
    #===========================================================================
    # startItem
    #===========================================================================
    def startItem(self, longItemAddress):
        """ Starts selected item """
        
        print "Starting %s" %longItemAddress
        xbeeState = hiddenXbeeChangeState(longItemAddress,"D0","ON")
        if xbeeState == 1:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 2:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.disconnectedXbee)            
        elif xbeeState == 3:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.RED)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.startedXbee)
        elif xbeeState == 4:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.stoppedXbee)            
        elif xbeeState == 5:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 6:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 7:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 8:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)
        else:
            try:
                self.showItemInfo(False,{})
            except TypeError:
                pass               
            SCS_ShowMessage("Xbee: Изтекло време за отговор!",0)
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.disconnectedXbee)
        
    #===========================================================================
    # stopItem
    #===========================================================================
    def stopItem(self, longItemAddress):
        """ Stops selected item """
        
        print "Stopping %s" %longItemAddress
        xbeeState = hiddenXbeeChangeState(longItemAddress,"D0","OFF")
        if xbeeState == 1:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 2:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.disconnectedXbee)            
        elif xbeeState == 3:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.RED)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.startedXbee)
        elif xbeeState == 4:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.stoppedXbee)            
        elif xbeeState == 5:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 6:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 7:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)            
        elif xbeeState == 8:
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.errorXbee)
        else:
            try:
                self.showItemInfo(False,{})
            except TypeError:
                pass               
            SCS_ShowMessage("Xbee: Изтекло време за отговор!",0)
            self.Sp_TreeCtrl.changeItemColor(longItemAddress, wx.BLACK)
            self.Sp_TreeCtrl.changeItemImage(longItemAddress, self.Sp_TreeCtrl.disconnectedXbee)

    #===========================================================================
    # startGroup
    #===========================================================================
    def startGroup(self, group_name):
        """ Start current group (Cell 1)"""
        global GROUPS_DICT
        global GROUPS_QTY
        global PREVIOUS_GROUP

        self.SCS_Frame_statusbar.SetStatusText("%s работи в момента..." %group_name,0)
        self.stopGroup(PREVIOUS_GROUP)
        for node in range(len(GROUPS_DICT[group_name])):
            try:
                if FACILITY_MAP[GROUPS_DICT[group_name][node]] != 'None':
                    print "Now is running %s" %FACILITY_MAP[GROUPS_DICT[group_name][node]]
                    xbeeState = hiddenXbeeChangeState(FACILITY_MAP[GROUPS_DICT[group_name][node]],"D0","ON")
                    PREVIOUS_GROUP.append(FACILITY_MAP[GROUPS_DICT[group_name][node]])
                    if xbeeState == 1:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 2:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.disconnectedXbee)            
                    elif xbeeState == 3:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.RED)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.startedXbee)
                    elif xbeeState == 4:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.stoppedXbee)            
                    elif xbeeState == 5:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 6:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 7:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 8:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP[GROUPS_DICT[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.errorXbee)
                    else:
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP[GROUPS_DICT[group_name][node]], self.Sp_TreeCtrl.errorXbee)
            except KeyError:
                print "Node is unavilable!"
                self.SCS_Frame_statusbar.SetStatusText("...",0) 
        
        print PREVIOUS_GROUP
        
    def startGroup2(self, group_name):
        """ Start current group (Cell 2)"""
        global GROUPS_DICT2
        global GROUPS_QTY2
        global PREVIOUS_GROUP2

        self.SCS_Frame_statusbar.SetStatusText("%s работи в момента..." %group_name,0)
        self.stopGroup2(PREVIOUS_GROUP2)
        for node in range(len(GROUPS_DICT2[group_name])):
            try:
                if FACILITY_MAP2[GROUPS_DICT2[group_name][node]] != 'None':
                    print "Now is running %s" %FACILITY_MAP2[GROUPS_DICT2[group_name][node]]
                    xbeeState = hiddenXbeeChangeState(FACILITY_MAP2[GROUPS_DICT2[group_name][node]],"D0","ON")
                    PREVIOUS_GROUP2.append(FACILITY_MAP2[GROUPS_DICT2[group_name][node]])
                    if xbeeState == 1:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 2:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.disconnectedXbee)            
                    elif xbeeState == 3:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.RED)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.startedXbee)
                    elif xbeeState == 4:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.stoppedXbee)            
                    elif xbeeState == 5:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 6:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 7:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.errorXbee)            
                    elif xbeeState == 8:
                        self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], wx.BLACK)
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.errorXbee)
                    else:
                        self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2[GROUPS_DICT2[group_name][node]], self.Sp_TreeCtrl.errorXbee)
            except KeyError:
                print "Node is unavilable!"
                self.SCS_Frame_statusbar.SetStatusText("...",0) 
        
        print PREVIOUS_GROUP2
                
    def updateTimer1(self, event):
        """ Updates Timer for runnig sprinklers """
        
        global GROUPS_QTY
        global GROUPS_DICT
        print "\nupdated_T1: ",
        print time.ctime()
    
        try:
            group_actual = GROUPS_DICT['Group %s' %str(GROUPS_QTY)]
            if len(group_actual)<>0:
                print "Startira pylna grupa"
                self.startGroup('Group %s' %str(GROUPS_QTY))         
                GROUPS_QTY = GROUPS_QTY + 1            
            else:
                print "Prazna grupa"
                GROUPS_QTY = GROUPS_QTY + 1
        except KeyError:
            print "KeyError pri timer 1"
            GROUPS_QTY = GROUPS_QTY + 1

        if GROUPS_QTY > len(GROUPS_DICT):
            GROUPS_QTY = 1
            
    def updateTimer2(self, event):
        """
        """
        global GROUPS_QTY2
        global GROUPS_DICT2
        print "\nupdated_T2: ",
        print time.ctime()
    
        try:
            group_actual = GROUPS_DICT2['Group %s' %str(GROUPS_QTY2)]
            if len(group_actual)<>0:
                self.startGroup2('Group %s' %str(GROUPS_QTY2))         
                GROUPS_QTY2 = GROUPS_QTY2 + 1            
            else:
                GROUPS_QTY2 = GROUPS_QTY2 + 1
        except KeyError:
            GROUPS_QTY2 = GROUPS_QTY2 + 1

        if GROUPS_QTY2 > len(GROUPS_DICT2):
            GROUPS_QTY2 = 1
    
    def num(self,s):
        try:
            return int(s)
        except ValueError:
            return float(s)            
            
    def OnQuit(self, event=None):
        """Exit application."""
        if self.timer1.IsRunning():
            self.timer1.Stop()
        else:
            pass
        if self.timer2.IsRunning():
            self.timer2.Stop()
        else:
            pass        
        self.Close()
        
    def stopCellPhase(self, cell_name, phase_name):

        global PREVIOUS_GROUP
        global PREVIOUS_GROUP2
        
        if self.timer1.IsRunning():
            self.timer1.Stop()
        if self.timer2.IsRunning():
            self.timer2.Stop()
            
        self.stopGroup(PREVIOUS_GROUP)
        self.stopGroup2(PREVIOUS_GROUP2)
    
    def stopAll(self):
        """
        """
        global FACILITY_MAP
        global ISALLSTOPPED
        global FACILITY_MAP2        
    
        self.buildFacilityMap('Cell 1','Phase 1')
        self.SCS_Frame_statusbar.SetStatusText("Протича спиране на всички управления от Клетка 1...",0)
        for node in FACILITY_MAP:
            print FACILITY_MAP.get(node)
            if FACILITY_MAP.get(node)!='None':
                xbeeState = hiddenXbeeChangeState(FACILITY_MAP.get(node),"D0","OFF")
                if xbeeState == 1:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 2:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.disconnectedXbee)            
                elif xbeeState == 3:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.RED)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.startedXbee)
                elif xbeeState == 4:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.stoppedXbee)            
                elif xbeeState == 5:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 6:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 7:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 8:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.errorXbee)
                else:
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP.get(node), self.Sp_TreeCtrl.disconnectedXbee)
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP.get(node), wx.BLACK)
        
        self.buildFacilityMap2('Cell 2', 'Phase 1')
        self.SCS_Frame_statusbar.SetStatusText("Протича спиране на всички управления от Клетка 2...",0)
        for node in FACILITY_MAP2:
            print FACILITY_MAP2.get(node)
            if FACILITY_MAP2.get(node)!='None':
                xbeeState = hiddenXbeeChangeState(FACILITY_MAP2.get(node),"D0","OFF")
                if xbeeState == 1:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 2:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.disconnectedXbee)            
                elif xbeeState == 3:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.RED)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.startedXbee)
                elif xbeeState == 4:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.stoppedXbee)            
                elif xbeeState == 5:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 6:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 7:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.errorXbee)            
                elif xbeeState == 8:
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.errorXbee)
                else:
                    self.Sp_TreeCtrl.changeItemImage(FACILITY_MAP2.get(node), self.Sp_TreeCtrl.disconnectedXbee)
                    self.Sp_TreeCtrl.changeItemColor(FACILITY_MAP2.get(node), wx.BLACK)
                
        self.SCS_Frame_statusbar.SetStatusText("Всички управления са спрени!",0)
        ISALLSTOPPED = 1

    def OnPrograms(self,event=None):
        pass

    def OnDiscover(self,event=None):
        self.add_frame = SCS_AddFrame()
        self.add_frame.Show()

    def OnSettings(self,event=None):
        self.sys_frame = SCS_SysSettingsFrame()
        self.sys_frame.Show()    
    
    def OnGenAbout(self,event=None):
        """Bring up a wx.MessageDialog with a useless message."""
        self.about_frame = SCS_AboutFrame()
        self.about_frame.Show()
        
    def OnToggleShock(self, event):  # wxGlade: MyFrame.<event_handler>
        print "Event handler 'OnToggle' not implemented!"
        if self.tabNodeShockTog.GetValue():
            self.tabNodeShockTog.SetLabel("Изключи")
        else:
            self.tabNodeShockTog.SetLabel("Включи")
        event.Skip()
        
    def OnToggleLed(self, event):  # wxGlade: MyFrame.<event_handler>
        print "Event handler 'OnToggle' not implemented!"
        if self.tabNodeLedTog.GetValue():
            self.tabNodeLedTog.SetLabel("Изключи")
        else:
            self.tabNodeLedTog.SetLabel("Включи")
        event.Skip()    
   
    def OnGroupsSet(self, event):
        self.groups_settings = SCS_GroupsFrame()
        self.groups_settings.Show()    
        
    def OnButtonStartPressed(self, event):
        global TREECTRL_ELEMENT_SELECTED
        global TREECTRL_PARENT_SELECTED
        global ISSTARTED
        global ISALLSTOPPED
        
        ISSTARTED = 1
        ISALLSTOPPED = 0
        
        if TREECTRL_ELEMENT_SELECTED.startswith('Phase 1') and TREECTRL_PARENT_SELECTED.startswith('Cell 1'):
            self.buildFacilityMap(TREECTRL_PARENT_SELECTED.strip(), TREECTRL_ELEMENT_SELECTED.strip())
            self.SCS_Frame_statusbar.SetStatusText("Създава карта на съоръжението Cell 1...",0)   
            if self.timer1.IsRunning():
                pass
            else:
                print "starting timer1..."
                if self.processingGroups(TREECTRL_PARENT_SELECTED.strip(), TREECTRL_ELEMENT_SELECTED.strip()) is True:
                    self.SCS_Frame_statusbar.SetStatusText("Протича обработка на групата Cell 1...",0)   
                    self.timer1.Start(180000)
                elif self.timer1.IsRunning():
                    self.timer1.Stop()
                else:
                    SCS_ShowMessage("Няма дефинирани групи за този елемент!",0)
        elif TREECTRL_PARENT_SELECTED.startswith('Phase'):
                self.SCS_Frame_statusbar.SetStatusText("Starting Cell 1%s" %processLongAddress(TREECTRL_ELEMENT_SELECTED),0)
                self.startItem(processLongAddress(TREECTRL_ELEMENT_SELECTED))
        else:
            pass
            
        if TREECTRL_ELEMENT_SELECTED.startswith('Phase 1') and TREECTRL_PARENT_SELECTED.startswith('Cell 2'):
            self.buildFacilityMap2(TREECTRL_PARENT_SELECTED.strip(), TREECTRL_ELEMENT_SELECTED.strip())
            self.SCS_Frame_statusbar.SetStatusText("Създава карта на съоръжението Cell 2...",0)   
            if self.timer2.IsRunning():
                pass
            else:
                print "starting timer2..."
                if self.processingGroups(TREECTRL_PARENT_SELECTED.strip(), TREECTRL_ELEMENT_SELECTED.strip()) is True:
                    self.SCS_Frame_statusbar.SetStatusText("Протича обработка на групата Cell 2...",0)   
                    self.timer2.Start(180000)
                elif self.timer2.IsRunning():
                    self.timer2.Stop()
                else:
                    SCS_ShowMessage("Няма дефинирани групи за този елемент!",0)
        elif TREECTRL_PARENT_SELECTED.startswith('Phase'):
                self.SCS_Frame_statusbar.SetStatusText("Starting Cell 2 %s" %processLongAddress(TREECTRL_ELEMENT_SELECTED),0)
                self.startItem(processLongAddress(TREECTRL_ELEMENT_SELECTED))
        else:
            pass
   
    def OnButtonStopPressed(self, event):
        global TREECTRL_ELEMENT_SELECTED         
        global GROUPS_QTY
        global GROUPS_DICT
        global FACILITY_MAP
        global ISSTARTED
        
        ISSTARTED = 0
        GROUPS_QTY = 1
        GROUPS_DICT = {}
        FACILITY_MAP = {}        
        
        if TREECTRL_ELEMENT_SELECTED.startswith('Phase'):
            if self.timer1.IsRunning():
                self.timer1.Stop()
                self.stopCellPhase('Cell 1', 'Phase 1')
                self.SCS_Frame_statusbar.SetStatusText("Елементът е спрян",0)
            else:
                pass
        elif TREECTRL_PARENT_SELECTED.startswith('Phase'):
            self.SCS_Frame_statusbar.SetStatusText("Stopping %s" %processLongAddress(TREECTRL_ELEMENT_SELECTED),0)
            self.stopItem(processLongAddress(TREECTRL_ELEMENT_SELECTED))
            SCS_ShowMessage("STOP: %s" %TREECTRL_ELEMENT_SELECTED,0)
        else:
            SCS_ShowMessage("Моля, изберете фаза или Д.А.!",0)
           
        self.SCS_Frame_statusbar.SetStatusText("",0)
            
    def OnButtonStopAllPressed(self, event):
        global TREECTRL_ELEMENT_SELECTED
        global ISSTARTED
        global ISALLSTOPPED
        
        ISSTARTED = 0
        ISALLSTOPPED = 1
# Must be unified
        if self.timer1.IsRunning():
            self.timer1.Stop()
        else:
            pass
        if self.timer2.IsRunning():
            self.timer2.Stop()
        else:
            pass
        
        self.stopAll()
        self.SCS_Frame_statusbar.SetStatusText("Всички управления са спрени!",0)

    def OnButtonPausePressed(self, event):
        global TREECTRL_ELEMENT_SELECTED         
        
        if TREECTRL_ELEMENT_SELECTED <> '':
            if self.timer1.IsRunning():
                self.timer1.Stop()
            else:
                pass
            SCS_ShowMessage("%s is paused" %TREECTRL_ELEMENT_SELECTED,0)
            self.SCS_Frame_statusbar.SetStatusText("%s е в пауза..." %TREECTRL_ELEMENT_SELECTED,0)
        else:
            SCS_ShowMessage("Не е избран подходящ елемент!",0)

    def OnButtonTestPressed(self, event):

        global ISALLSTOPPED
        
        dlg = testResultDlgHtml(wx.GetApp().TopWindow, [], ISALLSTOPPED)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnButtonHSavePressed(self, event):
        """
        """
        global TREECTRL_ELEMENT_SELECTED
        global TREECTRL_PARENT_SELECTED
        global TREECTRL_UPPARENT_SELECTED
        
        text = self.mainTCtrlHistroy.GetValue()
        version = self.mainCBoxVersion.GetValue()
        
        try:
            nodeName = processNodeName(TREECTRL_ELEMENT_SELECTED)
            if nodeName <> '':
                if self.mainCheckBoxVersion.IsChecked():
                    text = u'Смяна на версията'
                    NH.updateVersion(TREECTRL_UPPARENT_SELECTED, TREECTRL_PARENT_SELECTED, nodeName, unicode(version))
                NH.addEvent(TREECTRL_UPPARENT_SELECTED, TREECTRL_PARENT_SELECTED, nodeName, unicode(text))
            else:
                SCS_ShowMessage("Не е избран подходящ елемент!", 0)
        except:
            SCS_ShowMessage("Не е избран подходящ елемент!",0)
            
        events_dict = NH.getNHEvents(TREECTRL_UPPARENT_SELECTED, TREECTRL_PARENT_SELECTED, processNodeName(TREECTRL_ELEMENT_SELECTED))
        version  = NH.getNHVersion(TREECTRL_UPPARENT_SELECTED, TREECTRL_PARENT_SELECTED, processNodeName(TREECTRL_ELEMENT_SELECTED))
        
        self.showItemHistory(events_dict)
        self.showItemVersion(str(version))
                
        self.mainTCtrlHistroy.SetValue('')  
