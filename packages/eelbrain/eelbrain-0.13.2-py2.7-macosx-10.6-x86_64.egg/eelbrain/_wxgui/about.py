"About dialog for Eelbrain"

import wx

from .. import __version__
from .._wxutils import Icon


class AboutFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "", style=wx.CLOSE_BOX)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        img = Icon('eelbrain160')
        bmp = wx.StaticBitmap(self, -1, img)
        sizer.Add(bmp, 0, wx.LEFT | wx.TOP | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL,
                  40)

        txt = "Eelbrain"
        text = wx.StaticText(self, -1, txt)
        font = text.GetFont()
        font.SetFaceName(".LucidaGrandeUI")
        font.SetPointSize(30)
        text.SetFont(font)
        sizer.Add(text, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 10)

        txt = "Version %s" % __version__
        text = wx.StaticText(self, -1, txt)
        font = text.GetFont()
        font.SetFaceName(".LucidaGrandeUI")
        font.SetPointSize(12)
        text.SetFont(font)
        text.SetForegroundColour(wx.Colour(120, 120, 120))
        sizer.Add(text, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 10)

        sizer.AddSpacer((300, 40))
        self.Fit()
        self.Center(wx.CENTER_ON_SCREEN | wx.HORIZONTAL)
