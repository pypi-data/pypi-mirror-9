"""test of PV widgets"""
import wx
import wx.lib.mixins.inspection
import epics
from epics.wx import EpicsFunction, PVFloatCtrl, PVSpinCtrl

pvname = 'Py:long2'
class TestPanel(wx.Panel):
    def __init__(self, parent=None, size=(400, 400)):
        wx.Panel.__init_(self, parent, -1, size=size)

        sizer = wx.GridBagSizer(5, 5)
        x = PVSpinCtrl(self, pvname, min_val=0, max_val=1000)
        t = wx.StaticText(self, label=pvname)
        sizer.Add(t, (0, 0), (1, 1))
        sizer.Add(x, (0, 1), (1, 1))
        self.SetSizer(sizer)
        ix, iy = self.GetBestSize()
        self.SetMinSize((ix+10, iy+10))
        self.SetSize((ix+15, iy+15))
        sizer.Fit(self)
        
class TestFrame(wx.Frame):
    def __init__(self, size=(-1, -1)):
        wx.Frame.__init__(self, parent=None, size=size)
        panel = TestPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Raise()
        
        
class TestApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def __init__(self, **kws):
        wx.App.__init__(self)

    def OnInit(self):
        self.Init()
        frame = TestFrame() 
        frame.Show()
        self.SetTopWindow(frame)
        self.ShowInspectionTool()
        return True

if __name__ == "__main__":
    TestApp().MainLoop()
