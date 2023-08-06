import webbrowser

import wx

from .._wxutils import ID, logger
from .about import AboutFrame


class App(wx.App):
    def OnInit(self):
        self.SetExitOnFrameDelete(False)
        self.SetAppName("Eelbrain")
        self.SetAppDisplayName("Eelbrain")

        # File Menu
        m = file_menu = wx.Menu()
        m.Append(wx.ID_OPEN, '&Open... \tCtrl+O')
        m.AppendSeparator()
        m.Append(wx.ID_CLOSE, '&Close Window \tCtrl+W')
        m.Append(wx.ID_SAVE, "Save \tCtrl+S")
        m.Append(wx.ID_SAVEAS, "Save As... \tCtrl+Shift+S")

        # Edit Menu
        m = edit_menu = wx.Menu()
        m.Append(ID.UNDO, '&Undo \tCtrl+Z')
        m.Append(ID.REDO, '&Redo \tCtrl+Shift+Z')
        m.AppendSeparator()
        m.Append(wx.ID_CUT, 'Cut \tCtrl+X')
        m.Append(wx.ID_COPY, 'Copy \tCtrl+C')
        m.Append(wx.ID_PASTE, 'Paste \tCtrl+V')
        m.AppendSeparator()
        m.Append(wx.ID_CLEAR, 'Cle&ar')

        # View Menu
        m = view_menu = wx.Menu()
        m.Append(ID.SET_VLIM, "Set Y-Axis Limit... \tCtrl+l", "Change the Y-"
                 "axis limit in epoch plots")
        m.Append(ID.SET_LAYOUT, "&Set Layout... \tCtrl+Shift+l", "Change the "
                 "page layout")
        m.AppendCheckItem(ID.PLOT_RANGE, "&Plot Data Range \tCtrl+r", "Plot "
                          "data range instead of individual sensor traces")

        # Go Menu
        m = go_menu = wx.Menu()
        m.Append(wx.ID_FORWARD, '&Forward \tCtrl+]', 'Go One Page Forward')
        m.Append(wx.ID_BACKWARD, '&Back \tCtrl+[', 'Go One Page Back')
        m.AppendSeparator()
        m.Append(ID.YIELD_TO_TERMINAL, '&Yield to Terminal \tAlt+Ctrl+Q')

        # Window Menu
        m = window_menu = wx.Menu()
        m.Append(ID.WINDOW_MINIMIZE, '&Minimize \tCtrl+M')
        m.Append(ID.WINDOW_ZOOM, '&Zoom')
        m.AppendSeparator()
        self.window_menu_window_items = []

        # Help Menu
        m = help_menu = wx.Menu()
        m.Append(ID.HELP_EELBRAIN, 'Eelbrain Help')
        m.Append(ID.HELP_PYTHON, "Python Help")
        m.AppendSeparator()
        m.Append(wx.ID_ABOUT, '&About Eelbrain')

        # Menu Bar
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "File")
        menu_bar.Append(edit_menu, "Edit")
        menu_bar.Append(view_menu, "View")
        menu_bar.Append(go_menu, "Go")
        menu_bar.Append(window_menu, "Window")
        menu_bar.Append(help_menu, self.GetMacHelpMenuTitleName())
        wx.MenuBar.MacSetCommonMenuBar(menu_bar)
        self.menubar = menu_bar

        # Bind Menu Commands
        self.Bind(wx.EVT_MENU_OPEN, self.OnMenuOpened)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnClear, id=wx.ID_CLEAR)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnOnlineHelp, id=ID.HELP_EELBRAIN)
        self.Bind(wx.EVT_MENU, self.OnOnlineHelp, id=ID.HELP_PYTHON)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.OnRedo, id=ID.REDO)
        self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnSetLayout, id=ID.SET_LAYOUT)
        self.Bind(wx.EVT_MENU, self.OnSetVLim, id=ID.SET_VLIM)
        self.Bind(wx.EVT_MENU, self.OnTogglePlotRange, id=ID.PLOT_RANGE)
        self.Bind(wx.EVT_MENU, self.OnUndo, id=ID.UNDO)
        self.Bind(wx.EVT_MENU, self.OnWindowMinimize, id=ID.WINDOW_MINIMIZE)
        self.Bind(wx.EVT_MENU, self.OnWindowZoom, id=ID.WINDOW_ZOOM)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnYieldToTerminal, id=ID.YIELD_TO_TERMINAL)

        # bind update UI
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIBackward, id=wx.ID_BACKWARD)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIClear, id=wx.ID_CLEAR)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUICopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUICut, id=wx.ID_CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIForward, id=wx.ID_FORWARD)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIPaste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIPlotRange, id=ID.PLOT_RANGE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIRedo, id=ID.REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUISave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUISaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUISetLayout, id=ID.SET_LAYOUT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUISetVLim, id=ID.SET_VLIM)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUIUndo, id=ID.UNDO)

        return True

    def _get_active_frame(self):
        win = wx.Window.FindFocus()
        return wx.GetTopLevelParent(win)
        for w in wx.GetTopLevelWindows():
            if hasattr(w, 'IsActive') and w.IsActive():
                return w
        return wx.GetActiveWindow()

    def _bash_ui(self, func, *args):
        "Launch a modal dialog based on terminal input"
        if self.IsMainLoopRunning():
            raise RuntimeError("MainLoop running")
        if not self.GetTopWindow():
            self.SetTopWindow(wx.Frame(None))
        wx.CallLater(10, func, *args)
        print "Please switch to the Python Application to provide input."
        self.MainLoop()
        return self._result

    def ask_for_dir(self, title="Select Folder", message="Please Pick a Folder",
                    must_exist=True):
        return self._bash_ui(self._ask_for_dir, title, message, must_exist)

    def _ask_for_dir(self, title, message, must_exist):
        style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        if must_exist:
            style = style | wx.DD_DIR_MUST_EXIST

        dialog = wx.DirDialog(None, message, name=title,
                              style=style)
        dialog.SetTitle(title)
        if dialog.ShowModal() == wx.ID_OK:
            self._result = dialog.GetPath()
        else:
            self._result = False
        self.ExitMainLoop()

    def ask_for_file(self, title, message, filetypes, directory, mult):
        return self._bash_ui(self._ask_for_file, title, message, filetypes,
                             directory, mult)

    def _ask_for_file(self, title, message, wildcard, directory, mult):
        """Returns path(s) or False.

        Parameters
        ----------
        ...
        directory : str
            Path to initial directory.

        Returns
        -------
        Result : list | str | None
            Paths(s) or False.
        """
        style = wx.FD_OPEN
        if mult:
            style = style | wx.FD_MULTIPLE
        dialog = wx.FileDialog(None, message, directory,
                               wildcard=wildcard, style=style)
        dialog.SetTitle(title)
        if dialog.ShowModal() == wx.ID_OK:
            if mult:
                self._result = dialog.GetPaths()
            else:
                self._result = dialog.GetPath()
        else:
            self._result = False
        self.ExitMainLoop()

    def ask_for_string(self, title, message, default=''):
        return self._bash_ui(self._ask_for_string, title, message, default)

    def _ask_for_string(self, title, message, default):
        dlg = wx.TextEntryDialog(None, message, title, default)
        if dlg.ShowModal() == wx.ID_OK:
            self._result = dlg.GetValue()
        else:
            self._result = False
        self.ExitMainLoop()

    def message_box(self, message, caption, style):
        return self._bash_ui(self._message_box, message, caption, style)

    def _message_box(self, message, caption, style):
        self._result = wx.MessageBox(message, caption, style)
        self.ExitMainLoop()

    def OnAbout(self, event):
        if hasattr(self, '_about_frame') and hasattr(self._about_frame, 'Raise'):
            self._about_frame.Raise()
        else:
            self._about_frame = AboutFrame(None)
            self._about_frame.Show()
#             frame.SetFocus()

    def OnClear(self, event):
        frame = self._get_active_frame()
        frame.OnClear(event)

    def OnCloseWindow(self, event):
        frame = self._get_active_frame()
        logger.debug("Close %r" % frame)
        if frame is not None:
            frame.Close()

    def OnCopy(self, event):
        win = wx.Window.FindFocus()
        logger.debug("Copy %r" % win)
        win.Copy()
#
    def OnCut(self, event):
        win = wx.Window.FindFocus()
        logger.debug("Cut %r" % win)
        win.Cut()

    def OnMenuOpened(self, event):
        "Updates window names in the window menu"
        menu = event.GetMenu()
        if menu.GetTitle() == 'Window':
            # clear old entries
            while self.window_menu_window_items:
                item = self.window_menu_window_items.pop()
                menu.RemoveItem(item)
                self.Unbind(wx.EVT_MENU, id=item.GetId())
            # add new entries
            for window in wx.GetTopLevelWindows():
                id_ = window.GetId()
                if id_ < 0:
                    continue
                item = menu.Append(id_, window.GetTitle())
                self.Bind(wx.EVT_MENU, self.OnWindowRaise, id=id_)
                self.window_menu_window_items.append(item)

    def OnOnlineHelp(self, event):
        "Called from the Help menu to open external resources"
        Id = event.GetId()
        if Id == ID.HELP_EELBRAIN:
            webbrowser.open("https://pythonhosted.org/eelbrain/")
        elif Id == ID.HELP_PYTHON:
            webbrowser.open("http://docs.python.org/2.7/")
        else:
            raise RuntimeError("Invalid help ID")

    def OnOpen(self, event):
        frame = self._get_active_frame()
        frame.OnOpen(event)

    def OnPaste(self, event):
        win = wx.Window.FindFocus()
        logger.debug("Paste %r" % win)
        win.Paste()

    def OnQuit(self, event):
        logger.debug("OnQuit %s", event)
        for win in wx.GetTopLevelWindows():
            if not win.Close():
                return
        self.ExitMainLoop()

    def OnRedo(self, event):
        frame = self._get_active_frame()
        frame.OnRedo(event)

    def OnSave(self, event):
        frame = self._get_active_frame()
        frame.OnSave(event)

    def OnSaveAs(self, event):
        frame = self._get_active_frame()
        frame.OnSaveAs(event)

    def OnSetVLim(self, event):
        frame = self._get_active_frame()
        frame.OnSetVLim(event)

    def OnSetLayout(self, event):
        frame = self._get_active_frame()
        frame.OnSetLayout(event)

    def OnTogglePlotRange(self, event):
        frame = self._get_active_frame()
        frame.OnTogglePlotRange(event)

    def OnUndo(self, event):
        frame = self._get_active_frame()
        frame.OnUndo(event)

    def OnUpdateUIBackward(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIBackward'):
            frame.OnUpdateUIBackward(event)
        else:
            event.Enable(False)

    def OnUpdateUIClear(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIClear'):
            frame.OnUpdateUIClear(event)
        else:
            event.Enable(False)

    def OnUpdateUIClose(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIClose'):
            frame.OnUpdateUIClose(event)
        else:
            event.Enable(False)

    def OnUpdateUICopy(self, event):
        win = wx.Window.FindFocus()
        event.Enable(win and hasattr(win, 'CanCopy') and win.CanCopy())

    def OnUpdateUICut(self, event):
        win = wx.Window.FindFocus()
        event.Enable(win and hasattr(win, 'CanCut') and win.CanCut())

    def OnUpdateUIForward(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIForward'):
            frame.OnUpdateUIForward(event)
        else:
            event.Enable(False)

    def OnUpdateUIOpen(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIOpen'):
            frame.OnUpdateUIOpen(event)
        else:
            event.Enable(False)

    def OnUpdateUIPaste(self, event):
        win = wx.Window.FindFocus()
        event.Enable(win and hasattr(win, 'CanPaste') and win.CanPaste())

    def OnUpdateUIPlotRange(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIPlotRange'):
            frame.OnUpdateUIPlotRange(event)
        else:
            event.Check(False)
            event.Enable(False)

    def OnUpdateUIRedo(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIRedo'):
            frame.OnUpdateUIRedo(event)
        else:
            event.Enable(False)

    def OnUpdateUISave(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUISave'):
            frame.OnUpdateUISave(event)
        else:
            event.Enable(False)

    def OnUpdateUISaveAs(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUISaveAs'):
            frame.OnUpdateUISaveAs(event)
        else:
            event.Enable(False)

    def OnUpdateUISetLayout(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUISetLayout'):
            frame.OnUpdateUISetLayout(event)
        else:
            event.Enable(False)

    def OnUpdateUISetVLim(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUISetVLim'):
            frame.OnUpdateUISetVLim(event)
        else:
            event.Enable(False)

    def OnUpdateUIUndo(self, event):
        frame = self._get_active_frame()
        if frame and hasattr(frame, 'OnUpdateUIUndo'):
            frame.OnUpdateUIUndo(event)
        else:
            event.Enable(False)

    def OnWindowMinimize(self, event):
        frame = self._get_active_frame()
        if frame:
            frame.Iconize()

    def OnWindowRaise(self, event):
        id_ = event.GetId()
        window = wx.FindWindowById(id_)
        window.Raise()

    def OnWindowZoom(self, event):
        frame = self._get_active_frame()
        if frame:
            frame.Maximize()

    def OnYieldToTerminal(self, event):
        self.ExitMainLoop()


def get_app():
    app = wx.GetApp()
    if app is None or not isinstance(app, App):
        logger.debug("Initializing Eelbrain App")
        app = App()
    return app


def run():
    app = get_app()
    if not app.IsMainLoopRunning():
        print "Starting GUI. Quit the Python application to return to the shell..."
        app.MainLoop()
