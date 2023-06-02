import wx

from module import gui


if __name__ == "__main__":
    app = wx.App()
    frame = gui.MyFrame()
    frame.Show()
    app.MainLoop()
