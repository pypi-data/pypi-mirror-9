
import wx
import sys
import epics
from epics.wx import EpicsFunction, DelayedEpicsCallback
from epics.ca import withInitialContext

class PVDisplay(wx.Frame):
    def __init__(self, pvname, parent=None, **kwds):
        wx.Frame.__init__(self, parent, wx.ID_ANY, '',
                         wx.DefaultPosition, wx.Size(-1,-1),**kwds)
        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        self.pvname = pvname

        self.SetTitle("%s" % pvname)
        
        self.sizer = wx.GridBagSizer(3, 2)
        panel = wx.Panel(self)
        name        = wx.StaticText(panel, label=pvname,        size=(85,-1))
        self.value  = wx.StaticText(panel, label='unconnected', size=(85,-1))
        self.info   = wx.StaticText(panel, label='-- ' ,        size=(400,300))        
        self.info.SetFont(wx.Font(10,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        self.sizer.Add(name,       (0, 0), (1, 1),     wx.EXPAND, 1)
        self.sizer.Add(self.value, (0, 1), (1, 1), wx.ALIGN_RIGHT|wx.EXPAND, 1)
        self.sizer.Add(self.info,  (1, 1), (2, 2), wx.ALIGN_LEFT|wx.EXPAND, 1)

        panel.SetSizer(self.sizer)

        self.s1 = wx.BoxSizer(wx.VERTICAL)
        self.s1.Add(panel, 1, wx.EXPAND, 2)
        self.s1.Fit(self)
      
        self.needs_info = None
        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
                  
        self.Refresh()
        self.connect_pv()
        
    @EpicsFunction
    def connect_pv(self):
        self.pv = epics.PV(self.pvname, connection_callback=self.onConnect,
                           callback=self.onPV_value)

    @EpicsFunction
    def onTimer(self, evt):
        if self.need_info and self.pv.connected:
            self.info.SetLabel(self.pv.info)
            self.timer.Stop()
            self.needs_info = False
        
    @DelayedEpicsCallback
    def onConnect(self, **kws):
        self.need_info = True
        self.timer.Start(25)
                

    @DelayedEpicsCallback
    def onPV_value(self, name=None, value=None, char_value=None, **kws):
        self.value.SetLabel('   %s' % char_value)
        self.need_info = True
        self.timer.Start(25)
        

