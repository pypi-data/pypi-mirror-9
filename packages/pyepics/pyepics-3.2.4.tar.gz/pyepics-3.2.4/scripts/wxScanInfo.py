#!/usr/bin/python
#
# test creating pvs in separate Frame

import wx
import sys
import epics
from epics.wx import EpicsFunction, DelayedEpicsCallback
from pvdisplay import PVDisplay

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()
ID_FREAD = wx.NewId()
ID_FSAVE = wx.NewId()
ID_CONF  = wx.NewId()

class NameCtrl(wx.TextCtrl):
    def __init__(self, owner, panel,  value='',
                 action=None, **kws):
        self.owner = owner
        self.action = action
        wx.TextCtrl.__init__(self, panel, wx.ID_ANY,
                             style=wx.TE_PROCESS_ENTER,
                             value='', **kws)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, event):
        key   = event.GetKeyCode()
        entry = wx.TextCtrl.GetValue(self).strip()
        pos   = wx.TextCtrl.GetSelection(self)
        if key == wx.WXK_RETURN and self.action is not None:
            self.action(entry, wid=self.GetId())
        event.Skip()

    def onText(self, event):
        entry = wx.TextCtrl.GetValue(self).strip()
        pos   = wx.TextCtrl.GetSelection(self)
        event.Skip()

        
class ProbeFrame(wx.Frame):
    def __init__(self, parent=None, **kwds):

        wx.Frame.__init__(self, parent, wx.ID_ANY, '',
                         wx.DefaultPosition, wx.Size(-1,-1),**kwds)
        self.SetTitle("Probe Epics Records:")

        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel = wx.Panel(self)
        label = wx.StaticText(panel, label='PV Name:')
        self.pvname = NameCtrl(panel, panel, value='', size=(175,-1),
                               action=self.onName)

        sizer.Add(label,       0, wx.ALIGN_LEFT, 1)
        sizer.Add(self.pvname, 1, wx.EXPAND, 1)
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(panel)
        s.Fit(self)
        self.Refresh()

    def onName(self, value, wid=None, **kws):
        PVDisplay(value, parent=self).Show()

if __name__ == '__main__':
    app = wx.App(redirect=False)
    ProbeFrame().Show()
    app.MainLoop()


