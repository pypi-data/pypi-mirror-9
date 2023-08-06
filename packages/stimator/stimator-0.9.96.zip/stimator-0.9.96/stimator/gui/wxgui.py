# -*- coding: utf8 -*-
"""wxPython GUI for S-timator."""


import sys
import os
import os.path
import thread
import traceback
import keyword
import resultsframe
import wx
import wx.aui
import wx.lib.newevent
import resultsframe
import stimator.modelparser
import stimator.estimation
import stimator.dynamics
from stimator import __version__
import images
from wx.py.shell import Shell

## try:
##     from agw import aui
##     from agw.aui import aui_switcherdialog as ASD
## except ImportError: # if it's not there locally, try the wxPython lib.
##     import wx.lib.agw.aui as aui
##     from wx.lib.agw.aui import aui_switcherdialog as ASD

ABOUT_TEXT = __doc__ + "\n\nVersion %s, %s" % (__version__.fullversion, __version__.date)

demoText = """\
#Write your model here...
"""

##------------- NewEvent objects and a EVT binder functions


ID_File_New = wx.NewId()
ID_File_Open = wx.NewId()
ID_File_Save_As = wx.NewId()
ID_File_Exit = wx.NewId()

ID_File_OpenScript = wx.NewId()

ID_Actions_RunModel = wx.NewId()
ID_Actions_RunScript = wx.NewId()
ID_Actions_FindParameters = wx.NewId()
ID_Actions_StopComputation = wx.NewId()
ID_Actions_StopScript = wx.NewId()

ID_CreatePerspective = wx.NewId()
ID_CopyPerspective = wx.NewId()

ID_TransparentHint = wx.NewId()
ID_VenetianBlindsHint = wx.NewId()
ID_RectangleHint = wx.NewId()
ID_NoHint = wx.NewId()
ID_HintFade = wx.NewId()
ID_AllowFloating = wx.NewId()
ID_NoVenetianFade = wx.NewId()
ID_TransparentDrag = wx.NewId()
ID_AllowActivePane = wx.NewId()
ID_NoGradient = wx.NewId()
ID_VerticalGradient = wx.NewId()
ID_HorizontalGradient = wx.NewId()

ID_Settings = wx.NewId()
ID_About = wx.NewId()
ID_FirstPerspective = ID_CreatePerspective+1000

(EndComputationEvent, EVT_END_COMPUTATION) = wx.lib.newevent.NewEvent()
(MsgEvent, EVT_MSG) = wx.lib.newevent.NewEvent()
(EndScriptEvent, EVT_END_SCRIPT) = wx.lib.newevent.NewEvent()

scriptglock = thread.allocate_lock()

debug = 1

##------------- child of Shell

class MyShell(Shell):
    pass
##------------- Main frame class

class MyFrame(wx.Frame):

    def __init__(self, parent, id=-1, title="S-timator", 
                pos=(0,0),
                size=wx.DefaultSize, style= wx.DEFAULT_FRAME_STYLE |
                                        wx.SUNKEN_BORDER |
                                        wx.CLIP_CHILDREN):

        print "Starting s-timator wxPython GUI"
        print
        print 'Python version'
        print sys.version
        print 'wx version'
        print wx.VERSION
        print '\nInitializing wx widgets...'

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)
        
        # init variables
        self._perspectives = []
        self.n = 0
        self.x = 0
        self.ui = gui_facade(self, scriptglock)

        self.nplots = 0
        self.fileName = None
        self.scriptfileName = None
        
        self.originaldir = os.getcwd()
        self.cwd = os.getcwd()
        self.oldcwd = self.cwd
        try:
            mydir = os.path.dirname(os.path.abspath(__file__))
        except:
            mydir = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.chdir(mydir)
        os.chdir('../examples/model_files')
        self.exampledir = os.getcwd()
        print 'Working folder:',self.exampledir
        self.cwd = os.getcwd()
        self.oldcwd = self.cwd


        self.optimizerThread = None
        self.calcscriptThread = None
        self.stop_script = False
        
        self.SetIcon(images.getMondrianIcon())
        self.SetBackgroundColour(wx.Colour(229, 229, 229))

        # create menu
        mb = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()

        file_menu.Append(ID_File_New, '&New\tCtrl-N', 'New')
        file_menu.Append(ID_File_Open, '&Open\tCtrl-O', 'Open')
        file_menu.Append(wx.ID_SAVE, '&Save\tCtrl-S', 'Save')
        file_menu.Append(ID_File_Save_As, 'Save &As\tCtrl-A', 'Save As')
        file_menu.AppendSeparator()
##         file_menu.Append(ID_File_OpenScript, 'Open S&cript', 'Open script')
##         file_menu.Append(ID_Actions_RunScript, 'Run Script', 'Run Script')
##         file_menu.AppendSeparator()
        file_menu.Append(ID_File_Exit, 'E&xit\tAlt-X', 'Exit')

        # Edit menu
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_UNDO, 'Undo\tCtrl-Z', 'Undo')
        edit_menu.Append(wx.ID_REDO, 'Redo\tCtrl-Y', 'Redo')
        edit_menu.Append(wx.ID_CUT, 'Cut\tCtrl-X', 'Cut')
        edit_menu.Append(wx.ID_COPY, '&Copy\tCtrl-C', 'Copy')
        edit_menu.Append(wx.ID_PASTE, 'Paste\tCtrl-V', 'Paste')

        help_menu = wx.Menu()
        help_menu.Append(ID_About, "About...")
        
        mb.Append(file_menu, "File")
        mb.Append(edit_menu, "Edit")
        mb.Append(help_menu, "Help")
        self.mb = mb
        
        self.SetMenuBar(mb)

        # statusbar configuration
        self.mainstatusbar = wx.StatusBar(self, -1)
        self.mainstatusbar.SetFieldsCount(2)
        self.mainstatusbar.SetStatusText("S-timator %s"%(__version__.fullversion), 0)
        self.mainstatusbar.SetStatusText("", 1)
        self.SetStatusBar(self.mainstatusbar)

        # min size for the frame itself isn't completely done.
        # see the end up FrameManager::Update() for the test
        # code. For now, just hard code a frame minimum size
        self.SetMinSize(wx.Size(400, 300))

        # create some toolbars

        tb2 = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER)
        tb2.SetToolBitmapSize(wx.Size(30,30))
        tb2.AddTool(ID_File_Open, images.getdi_folderBitmap(), shortHelpString="Open")
##         tb2.AddTool(ID_File_OpenScript, images.getdi_folderprocessBitmap(), shortHelpString="Open script")
        tb2.AddTool(wx.ID_SAVE, images.getdi_saveBitmap(), shortHelpString="Save")
        tb2.AddSeparator()
        tb2.AddTool(wx.ID_CUT, images.getdi_cutBitmap(), shortHelpString="Cut")
        tb2.AddTool(wx.ID_COPY, images.getdi_copyBitmap(), shortHelpString="Copy")
        tb2.AddTool(wx.ID_PASTE, images.getdi_pasteBitmap(), shortHelpString="Paste")
        tb2.AddSeparator()
        tb2.AddTool(wx.ID_UNDO, images.get_rt_undoBitmap(), shortHelpString="Undo")
        tb2.AddTool(wx.ID_REDO, images.get_rt_redoBitmap(), shortHelpString="Redo")
        tb2.AddSeparator()
        
        tb2.AddTool(ID_Actions_RunModel, images.getdi_runBitmap(), shortHelpString="Run Model")
        tb2.AddTool(ID_Actions_FindParameters, images.getdi_flagBitmap(), shortHelpString="Find Parameters")

##         tb2.AddSeparator()
##         tb2.AddTool(ID_Actions_RunScript, images.getdi_processBitmap(), shortHelpString="Run Script")
        tb2.AddTool(ID_Actions_StopComputation, images.getdi_processdeleteBitmap(), shortHelpString="Stop Script")
##         tb2.AddSeparator()
        buttonId = wx.NewId()
        b = wx.Button(tb2, buttonId, "Example", (20, 20), style=wx.NO_BORDER|wx.BU_EXACTFIT )
        tb2.AddControl(b)
        self.Bind(wx.EVT_BUTTON, self.OnExampleButton, b)
        
        tb2.Realize()
        self.tb2 = tb2

        self.Bind(wx.EVT_MENU, self.OnOpenScript, id=ID_File_OpenScript)
        self.Bind(wx.EVT_MENU, self.OnComputeButton, id=ID_Actions_FindParameters)
        self.Bind(wx.EVT_MENU, self.OnRunScript, id=ID_Actions_RunScript)
        self.Bind(wx.EVT_MENU, self.OnRunButton, id=ID_Actions_RunModel)
        self.Bind(wx.EVT_MENU, self.OnStopScript, id=ID_Actions_StopComputation)

                      
        # add the toolbars to the manager
        self._mgr.AddPane(tb2, wx.aui.AuiPaneInfo().
                          Name("tb2").Caption("Toolbar 2").
                          ToolbarPane().Top().Row(1).
                          LeftDockable(False).RightDockable(False))

        sz = self.GetClientSize()
##         lcs = {'ui': self.ui, 'st':stimator, 'clear': self.ui.clear}
##         self.shell = MyShell(parent=self, locals=lcs)
##         self._mgr.AddPane(self.shell, wx.aui.AuiPaneInfo().
##                           Name("shell").Caption("Shell").
##                           Bottom().Layer(0).Row(0).Position(0).MinSize(wx.Size(200,sz.y/2)).CloseButton(True).MaximizeButton(True))

        # create  center pane

        self._notebook_style = (wx.aui.AUI_NB_DEFAULT_STYLE | 
                                wx.aui.AUI_NB_TAB_EXTERNAL_MOVE | 
                                wx.NO_BORDER)
        self._notebook_style &= ~(wx.aui.AUI_NB_CLOSE_BUTTON |
                                  wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB |
                                  wx.aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.nb = wx.aui.AuiNotebook(self, style=self._notebook_style)
        ed = self.CreateEditor()
        self.nb.AddPage(ed, "Model")
##         indx = self.nb.GetPageIndex(self.ModelEditor)
##         self.nb.SetCloseButton(indx, False)
        lcs = {'ui': self.ui, 'st':stimator, 'clear': self.ui.clear}
        self.shell = MyShell(parent=self, locals=lcs)
        self.nb.AddPage(self.shell, "Shell")
        
##         page = wx.TextCtrl(self.nb, -1, demoText, style=wx.TE_MULTILINE)
##         self.nb.AddPage(page, "Welcome")

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)
        wx.CallAfter(self.nb.SendSizeEvent)
            
        self._mgr.AddPane(self.nb, wx.aui.AuiPaneInfo().Name("model_editor").Caption(" ").
                          Center().Layer(0).Row(0).Position(0).MinSize(wx.Size(sz.x,sz.y/2)).CloseButton(False).MaximizeButton(False))
                        

        # make some default perspectives
        
        perspective_all = self._mgr.SavePerspective()
        
        all_panes = self._mgr.GetAllPanes()
        
        for ii in xrange(len(all_panes)):
            if not all_panes[ii].IsToolbar():
                all_panes[ii].Hide()
                
        self._mgr.GetPane("model_editor").Show()
        self._mgr.GetPane("shell").Show()
##         self._mgr.GetPane("script_editor").Show()

        perspective_default = self._mgr.SavePerspective()


        self._perspectives.append(perspective_default)
        self._perspectives.append(perspective_all)

        flag = wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE
        self._mgr.SetFlags(self._mgr.GetFlags() ^ flag)

        # "commit" all changes made to FrameManager   
        self._mgr.Update()

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Show How To Use The Closing Panes Event
        self.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

        self.Bind(wx.EVT_MENU, self.OnNewMenu, id=ID_File_New)
        self.Bind(wx.EVT_MENU, self.OnOpenMenu, id=ID_File_Open)
        self.Bind(wx.EVT_MENU, self.OnSaveMenu, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveAsMenu, id=ID_File_Save_As)
        self.Bind(wx.EVT_MENU, self.OnClose, id=ID_File_Exit)

        self.Bind(wx.EVT_MENU, self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.OnCutSelection, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnCopySelection, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=wx.ID_PASTE)

        self.Bind(wx.EVT_MENU, self.OnCreatePerspective, id=ID_CreatePerspective)
        self.Bind(wx.EVT_MENU, self.OnCopyPerspective, id=ID_CopyPerspective)

        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_AllowFloating)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_TransparentHint)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_VenetianBlindsHint)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_RectangleHint)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_NoHint)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_HintFade)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_NoVenetianFade)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_TransparentDrag)
        self.Bind(wx.EVT_MENU, self.OnManagerFlag, id=ID_AllowActivePane)
        
        self.Bind(wx.EVT_MENU, self.OnGradient, id=ID_NoGradient)
        self.Bind(wx.EVT_MENU, self.OnGradient, id=ID_VerticalGradient)
        self.Bind(wx.EVT_MENU, self.OnGradient, id=ID_HorizontalGradient)
        self.Bind(wx.EVT_MENU, self.OnExitMenu, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAboutMenu, id=ID_About)

        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_File_New)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_File_Open)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_File_Save_As)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_TransparentHint)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_VenetianBlindsHint)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_RectangleHint)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_NoHint)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_HintFade)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_AllowFloating)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_NoVenetianFade)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_TransparentDrag)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_AllowActivePane)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_NoGradient)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_VerticalGradient)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=ID_HorizontalGradient)
    
        self.Bind(wx.EVT_MENU_RANGE, self.OnRestorePerspective, id=ID_FirstPerspective,
                  id2=ID_FirstPerspective+1000)

        self.Bind(EVT_MSG, self.OnMsg)
        self.Bind(EVT_END_COMPUTATION, self.OnEndComputation)
        self.Bind(EVT_END_SCRIPT, self.OnEndScript)
        wx.Log_SetActiveTarget(MyLog(self.shell))
        #self.ModelEditor.GotoPos(self.ModelEditor.GetLastPosition())
        #self.ModelEditor.SetFocus()
        print 'wx widgets initialized'


##------------- Write funcs

    def WriteText(self, text):
        wx.LogMessage(text)

    def write(self, txt):
        self.WriteText(txt)

##-------------- Dialogs

    def MessageDialog(self, text, title):
        messageDialog = wx.MessageDialog(self, text, title, wx.OK | wx.ICON_INFORMATION)
        messageDialog.ShowModal()
        messageDialog.Destroy()

    def OkCancelDialog(self, text, title):
        dialog = wx.MessageDialog(self, text, title, wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
        result = dialog.ShowModal()
        dialog.Destroy()
        if result == wx.ID_OK:
            return True
        else:
            return False

    def SelectFileDialog(self, IsOpen=True, defaultDir=None, defaultFile=None, wildCard=None):
        if defaultDir == None:
            defaultDir = "."
        if defaultFile == None:
            defaultFile = ""
        if wildCard == None:
            wildCard = "*.*"
        osflag = wx.SAVE
        if IsOpen: osflag = wx.OPEN|wx.FILE_MUST_EXIST

        fileName = None
        fileDialog = wx.FileDialog(self, "Choose a file", defaultDir, defaultFile, wildCard, osflag)
        result = fileDialog.ShowModal()
        if result == wx.ID_OK:
            fileName = fileDialog.GetPath()
        fileDialog.Destroy()
        return fileName

    def SelectFilesDialog(self, IsOpen=True, defaultDir=None, defaultFile=None, wildCard=None):
        if defaultDir == None:
            defaultDir = "."
        if defaultFile == None:
            defaultFile = ""
        if wildCard == None:
            wildCard = "*.*"
        fileNames = None
        fileDialog = wx.FileDialog(self, "Choose some files", defaultDir, defaultFile, wildCard, wx.OPEN|wx.MULTIPLE|wx.FILE_MUST_EXIST)
        result = fileDialog.ShowModal()
        if result == wx.ID_OK:
            fileNames = fileDialog.GetPaths()
        fileDialog.Destroy()
        return fileNames

    def OpenFileError(self, fileName):
        wx.LogMessage('Open file error.')
        self.MessageDialog("Error opening file '%s'!" % fileName, "Error")

    def SaveFileError(self, fileName):
        wx.LogMessage('Save file error.')
        self.MessageDialog("Error saving file '%s'!" % fileName, "Error")


##---------------- Utility functions

    def GetModelFileDir(self, editor):
        if editor == self.ModelEditor:
            filename = self.fileName
##         if editor == self.ScriptEditor:
##             filename = self.scriptfileName
        if filename is not None:
            return os.path.split(filename)[0]
        return "."

    def GetFileName(self, editor):
        if editor == self.ModelEditor:
            filename = self.fileName
##         if editor == self.ScriptEditor:
##             filename = self.scriptfileName
        if filename is not None:
            return os.path.split(filename)[1]
        return ""

    def SaveFile(self, fileName, editor):
        sucess = editor.SaveFile(fileName)
        if sucess:
            self.setTitle2File(self.GetFileName(editor), editor)
        return sucess

    def setTitle2File(self, filename, editor):
        if len(filename) > 0:
            filename = ' [%s]'%filename
        if editor == self.ModelEditor:
            self._mgr.GetPane("model_editor").Caption("Model"+filename)
##         if editor == self.ScriptEditor:
##             self._mgr.GetPane("script_editor").Caption("Script"+filename)
        self._mgr.Update()
    
    def OpenFile(self, fileName, editor):
        sucess = editor.LoadFile(fileName)
        if sucess:
            if editor == self.ModelEditor:
                self.fileName = fileName
##             if editor == self.ScriptEditor:
##                 self.scriptfileName = fileName
            self.setTitle2File(self.GetFileName(editor), editor)
        return sucess

##---------------- Event handlers

    def updateButtons(self):
        canUndo = False
        canRedo = False
        canSave = False
        canCutCopy = False
        canPaste = False
        win = wx.Window.FindFocus()
        if isinstance(win, resultsframe.SDLeditor):
            canUndo = win.CanUndo()
            canRedo = win.CanRedo()
            canSave = win.IsModified()
            canCutCopy = win.IsSelecting()
            canPaste = win.CanPaste()
        self.tb2.EnableTool(wx.ID_UNDO, canUndo)
        self.tb2.EnableTool(wx.ID_REDO, canRedo)
        self.tb2.EnableTool(wx.ID_SAVE, canSave)
        self.tb2.EnableTool(wx.ID_CUT, canCutCopy)
        self.tb2.EnableTool(wx.ID_COPY, canCutCopy)
        self.tb2.EnableTool(wx.ID_PASTE, canPaste)
        self.mb.Enable(wx.ID_UNDO, canUndo)
        self.mb.Enable(wx.ID_REDO, canRedo)
        self.mb.Enable(wx.ID_SAVE, canSave)
        self.mb.Enable(wx.ID_CUT, canCutCopy)
        self.mb.Enable(wx.ID_COPY, canCutCopy)
        self.mb.Enable(wx.ID_PASTE, canPaste)

    def GetActivePaneName(self):
        for p in self._mgr.GetAllPanes():
            if p.HasFlag(wx.aui.AuiPaneInfo.optionActive):
                print 'active pane:', p.name
                return p.name

    def GetActiveEditor(self):
        #gwin = self.GetActivePaneName()
        gwin = self.nb.GetSelection()
        if gwin == 0:
            win = self.ModelEditor
        else:
            win = None
##         if gwin not in ["script_editor", "model_editor"]:
##             return None
##         if gwin == "model_editor":
##             win = self.ModelEditor
##         if gwin == "script_editor":
##             win = self.ScriptEditor
        return win
            
    
    def OnNewMenu(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        if win.GetModify():
            if not self.OkCancelDialog("New file - abandon changes?", "New File"):
                return
        win.SetText("")
        if win == self.ModelEditor:
            self.fileName = None
##         if win == self.ScriptEditor:
##             self.scriptfileName = None
        self.setTitle2File(self.GetFileName(win), win)
        win.SetFocus()

    def OnOpenMenu(self, event):
        win = self.ModelEditor
        if win.GetModify():
            if not self.OkCancelDialog("Open file - abandon changes?", "Open File"):
                return
        fileName = self.SelectFileDialog(True, self.GetModelFileDir(win))
        if fileName is not None:
            if self.OpenFile(fileName, win) is False:
                self.OpenFileError(fileName)
        win.SetFocus()
    
    def OnOpenScript(self, event):
        win = self.ScriptEditor
        if win.GetModify():
            if not self.OkCancelDialog("Open file - abandon changes?", "Open File"):
                return
        fileName = self.SelectFileDialog(True, self.GetModelFileDir(win))
        if fileName is not None:
            if self.OpenFile(fileName, win) is False:
                self.OpenFileError(fileName)
        win.SetFocus()

    def OnExampleButton(self, event):
        if self.ModelEditor.GetModify():
            if not self.OkCancelDialog("Open file - abandon changes?", "Open File"):
                return
        fileName = os.path.join(self.exampledir,'glxs_hta.mdl')
        if not os.path.exists(fileName) or not os.path.isfile(fileName):
            self.MessageDialog("File \n%s\ndoes not exist"% fileName, "Error")
            return
        if self.OpenFile(fileName, self.ModelEditor) is False:
            self.OpenFileError(fileName)
        self.ModelEditor.SetFocus()
        
    def OnSaveMenu(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        if win == self.ModelEditor:
            filename = self.fileName
##         if win == self.ScriptEditor:
##             filename = self.scriptfileName
        if filename is None:
            self.OnSaveAsMenu(event)
            return
        if self.SaveFile(filename, win) is not True:
            self.SaveFileError(filename)
        win.SetFocus()

    def OnSaveAsMenu(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        fileName = self.SelectFileDialog(False, self.GetModelFileDir(win),self.GetFileName(win))
        if fileName is not None:
            if self.SaveFile(fileName, win) is not True:
                self.SaveFileError(fileName)
                return
            if win == self.ModelEditor:
                self.fileName = fileName
##             if win == self.ScriptEditor:
##                 self.scriptfileName = fileName
        win.SetFocus()

    def OnCutSelection(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        win.Cut()

    def OnCopySelection(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        win.Copy()

    def OnPaste(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        win.Paste()

    def OnUndo(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        win.Undo()

    def OnRedo(self, event):
        win = self.GetActiveEditor()
        if win is None:
            return
        win.Redo()

    def OnPaneClose(self, event):
        caption = event.GetPane().caption
        if caption in ["Tree Pane", "Dock Manager Settings", "Fixed Pane","script_editor", "model_editor"]:
            msg = "Are You Sure You Want To Close This Pane?"
            dlg = wx.MessageDialog(self, msg, "AUI Question",
                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                event.Veto()
            dlg.Destroy()

    def OnClose(self, event):
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()

    def OnExitMenu(self, event):
        self.Close()

    def OnAboutMenu(self, event):
        self.MessageDialog(ABOUT_TEXT, "About S-timator")
        pass

    def GetDockArt(self):
        return self._mgr.GetArtProvider()

    def DoUpdate(self):
        self._mgr.Update()

    def OnEraseBackground(self, event):
        event.Skip()

    def OnSize(self, event):
        event.Skip()

##     def OnSettings(self, event):
##         # show the settings pane, and float it
##         floating_pane = self._mgr.GetPane("settings").Float().Show()
##         if floating_pane.floating_pos == wx.DefaultPosition:
##             floating_pane.FloatingPosition(self.GetStartPosition())
##         self._mgr.Update()


    def OnGradient(self, event):
        gradient = 0
        if event.GetId() == ID_NoGradient:
            gradient = wx.aui.AUI_GRADIENT_NONE
        elif event.GetId() == ID_VerticalGradient:
            gradient = wx.aui.AUI_GRADIENT_VERTICAL
        elif event.GetId() == ID_HorizontalGradient:
            gradient = wx.aui.AUI_GRADIENT_HORIZONTAL
        self._mgr.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE, gradient)
        self._mgr.Update()


    def OnManagerFlag(self, event):
        flag = 0
        eid = event.GetId()

        if eid in [ ID_TransparentHint, ID_VenetianBlindsHint, ID_RectangleHint, ID_NoHint ]:
            flags = self._mgr.GetFlags()
            flags &= ~wx.aui.AUI_MGR_TRANSPARENT_HINT
            flags &= ~wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT
            flags &= ~wx.aui.AUI_MGR_RECTANGLE_HINT
            self._mgr.SetFlags(flags)

        if eid == ID_AllowFloating:
            flag = wx.aui.AUI_MGR_ALLOW_FLOATING
        elif eid == ID_TransparentDrag:
            flag = wx.aui.AUI_MGR_TRANSPARENT_DRAG
        elif eid == ID_HintFade:
            flag = wx.aui.AUI_MGR_HINT_FADE
        elif eid == ID_NoVenetianFade:
            flag = wx.aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE
        elif eid == ID_AllowActivePane:
            flag = wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE
        elif eid == ID_TransparentHint:
            flag = wx.aui.AUI_MGR_TRANSPARENT_HINT
        elif eid == ID_VenetianBlindsHint:
            flag = wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT
        elif eid == ID_RectangleHint:
            flag = wx.aui.AUI_MGR_RECTANGLE_HINT
        
        self._mgr.SetFlags(self._mgr.GetFlags() ^ flag)


    def OnUpdateUI(self, event):
        flags = self._mgr.GetFlags()
        eid = event.GetId()
        
        if eid == ID_NoGradient:
            event.Check(self._mgr.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE) == wx.aui.AUI_GRADIENT_NONE)

        elif eid == ID_VerticalGradient:
            event.Check(self._mgr.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE) == wx.aui.AUI_GRADIENT_VERTICAL)

        elif eid == ID_HorizontalGradient:
            event.Check(self._mgr.GetArtProvider().GetMetric(wx.aui.AUI_DOCKART_GRADIENT_TYPE) == wx.aui.AUI_GRADIENT_HORIZONTAL)

        elif eid == ID_AllowFloating:
            event.Check((flags & wx.aui.AUI_MGR_ALLOW_FLOATING) != 0)

        elif eid == ID_TransparentDrag:
            event.Check((flags & wx.aui.AUI_MGR_TRANSPARENT_DRAG) != 0)

        elif eid == ID_TransparentHint:
            event.Check((flags & wx.aui.AUI_MGR_TRANSPARENT_HINT) != 0)

        elif eid == ID_VenetianBlindsHint:
            event.Check((flags & wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT) != 0)

        elif eid == ID_RectangleHint:
            event.Check((flags & wx.aui.AUI_MGR_RECTANGLE_HINT) != 0)

        elif eid == ID_NoHint:
            event.Check(((wx.aui.AUI_MGR_TRANSPARENT_HINT |
                          wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT |
                          wx.aui.AUI_MGR_RECTANGLE_HINT) & flags) == 0)

        elif eid == ID_HintFade:
            event.Check((flags & wx.aui.AUI_MGR_HINT_FADE) != 0);

        elif eid == ID_NoVenetianFade:
            event.Check((flags & wx.aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE) != 0);
        else:
            self.updateButtons()

    def OnCreatePerspective(self, event):
        dlg = wx.TextEntryDialog(self, "Enter a name for the new perspective:", "AUI Test")
        dlg.SetValue(("Perspective %d")%(len(self._perspectives)+1))
        if dlg.ShowModal() != wx.ID_OK:
            return
        if len(self._perspectives) == 0:
            self._perspectives_menu.AppendSeparator()
        self._perspectives_menu.Append(ID_FirstPerspective + len(self._perspectives), dlg.GetValue())
        self._perspectives.append(self._mgr.SavePerspective())


    def OnCopyPerspective(self, event):
        s = self._mgr.SavePerspective()
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(s))
            wx.TheClipboard.Close()
        
    def OnRestorePerspective(self, event):
        self._mgr.LoadPerspective(self._perspectives[event.GetId() - ID_FirstPerspective])

    def GetStartPosition(self):
        self.x = self.x + 20
        x = self.x
        pt = self.ClientToScreen(wx.Point(0, 0))
        return wx.Point(pt.x + x, pt.y + x)

    def CreateEditor(self):
        global ID_ME; ID_ME = wx.NewId()
        ed = resultsframe.SDLeditor(self, ID_ME , self)
        self.ModelEditor = ed
        
        ed.SetText(demoText)
        ed.EmptyUndoBuffer()
        # Set up the numbers in the margin for margin #1
        ed.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        # Reasonable value for, say, 4-5 digits using a mono font (40 pix)
        ed.SetMarginWidth(1, 40)
        ed.SetSelBackground(True, 'PLUM')
        ed.SetWrapMode(True)
        ed.SetKeyWords(0, "variables find timecourse rate generations genomesize popsize in reaction title")
        return ed

    def CreateLog(self):
        global ID_LT; ID_LT = wx.NewId()
        ed = resultsframe.SDLeditor(self, ID_LT , self, size = wx.Size(300,800))
        self.LogText = ed
        ed.SetText(u"")
        ed.EmptyUndoBuffer()
        ed.SetIndentationGuides(False)
        if wx.Platform == '__WXMSW__':
            face = 'Courier New'
            pb = 10
        else:
            face = 'Courier'
            pb = 12

        ed.StyleClearAll()
        ed.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "size:%d,face:%s" % (pb, face))
        ed.StyleSetSpec(wx.stc.STC_P_WORD, "fore:#00007F,bold")
        ed.SetSelBackground(True, 'PLUM')
        ed.SetWrapMode(True)
        ed.SetKeyWords(0, "TIMECOURSES OPTIMIZATION PARAMETERS")
        return ed

    def CreateResPanel(self, model, solver):
        self.nplots += 1
        name = "results%d"%self.nplots
        plotpanel = resultsframe.YetAnotherPlot(self, color=[255.0]*3, size=wx.Size(800, 500))
        plotpanel.model = model
        plotpanel.solver = solver
        self._mgr.AddPane(plotpanel, wx.aui.AuiPaneInfo().
                          Name(name).Caption("Results").
                          DestroyOnClose().
                          Dockable(False).Float().Show().CloseButton(True).MaximizeButton(True))
##                           Bottom().Layer(0).Row(0).Position(1).CloseButton(True).MaximizeButton(True))
        plotpanel.draw()

    def CreateResPanelFromFigure(self, figure):
        self.nplots += 1
        name = "results%d"%self.nplots
        plotpanel = resultsframe.PlotPanelFromFigure(self, figure, color=[255.0]*3, size=wx.Size(800, 500))
        self._mgr.AddPane(plotpanel, wx.aui.AuiPaneInfo().
                          Name(name).Caption("Results").
                          DestroyOnClose().
                          Dockable(False).Float().Show().CloseButton(True).MaximizeButton(True))
##                           Bottom().Layer(0).Row(0).Position(1).CloseButton(True).MaximizeButton(True))

    def CreateTreeCtrl(self):
        tree = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.Size(160, 250),
                           wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        root = tree.AddRoot("AUI Project")
        items = []

        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16,16)))
        tree.AssignImageList(imglist)

        items.append(tree.AppendItem(root, "Item 1", 0))
        items.append(tree.AppendItem(root, "Item 2", 0))
        items.append(tree.AppendItem(root, "Item 3", 0))
        items.append(tree.AppendItem(root, "Item 4", 0))
        items.append(tree.AppendItem(root, "Item 5", 0))

        for ii in xrange(len(items)):
            id = items[ii]
            tree.AppendItem(id, "Subitem 1", 1)
            tree.AppendItem(id, "Subitem 2", 1)
            tree.AppendItem(id, "Subitem 3", 1)
            tree.AppendItem(id, "Subitem 4", 1)
            tree.AppendItem(id, "Subitem 5", 1)
        tree.Expand(root)
        return tree

    def IndicateError(self, expt):
        #self.MessageDialog("The model description contains errors.\nThe computation was aborted.", "Error")
        if expt.physloc.nstartline == expt.physloc.nendline:
            locmsg = "Error in line %d of model definition\n" % (expt.physloc.nendline+1)
        else:
            locmsg = "Error in lines %d-%d of model definition\n" % (expt.physloc.nstartline+1,expt.physloc.nendline+1)
        self.shell.write(os.linesep)
        self.write(locmsg)
        self.write(str(expt))
        self.ModelEditor.SetSelection(expt.physloc.start, expt.physloc.end)
        self.shell.prompt()

    def OnStopScript(self,event):
        if (self.calcscriptThread is None) and (self.optimizerThread is None):
            print self.calcscriptThread
            print self.optimizerThread
            self.MessageDialog("S-timator is NOT performing a computation!", "Error")
            return
        if self.calcscriptThread is not None:
            scriptglock.acquire()
            self.stop_script = True
            scriptglock.release()
            return
        if self.optimizerThread is not None:
            self.optimizerThread.Stop()
    

    def OnComputeButton(self, event):
        if (self.optimizerThread is not None) or (self.optimizerThread is not None):
           self.MessageDialog("S-timator is performing a computation!\nPlease wait.", "Error")
           return
        #self._mgr.GetPane("results").Hide()
        self._mgr.Update()

        textlines = [self.ModelEditor.GetLine(i) for i in range(self.ModelEditor.GetLineCount())]
        
        oldout = sys.stdout #parser may need to print messages
        sys.stdout = self
        try:
            self.model = stimator.modelparser.read_model(textlines)
            self.tc = self.model.metadata['timecourses']
            self.optSettings = self.model.metadata['optSettings']
            if self.model.metadata.get('title','') == "":
               self.model.metadata['title'] = self.GetFileName(self.ModelEditor)
        except stimator.modelparser.StimatorParserError, expt:
                self.IndicateError(expt)
                sys.stdout = oldout
                return

        ntcread = self.tc.loadTimeCourses (self.GetModelFileDir(self.ModelEditor), names = self.tc.defaultnames, verbose=True)
        if ntcread == 0:
           sys.stdout = oldout
           return
        
        sys.stdout = oldout
        
        self.oldout = sys.stdout
        sys.stdout = MyWriter(self)
        solver = stimator.estimation.DeODEOptimizer(self.model,
                                               self.optSettings, 
                                               self.tc, None, None, 
                                               self.finalTick)
                                               #, self.msgTick, 
                                               #  self.finalTick)
        self.optimizerThread=CalcOptmThread()
        self.optimizerThread.Start(solver)
        
    def OnRunButton(self, event):
        if (self.optimizerThread is not None) or (self.optimizerThread is not None):
           self.MessageDialog("S-timator is performing a computation!\nPlease wait.", "Error")
           return
        self._mgr.Update()

        textlines = [self.ModelEditor.GetLine(i) for i in range(self.ModelEditor.GetLineCount())]
        #self.nb.SetSelection(1)
        
        oldout = sys.stdout #parser may need to print messages
        sys.stdout = self
        try:
            self.model = stimator.modelparser.read_model(textlines)
            self.tc = self.model.metadata['timecourses']
            self.optSettings = self.model.metadata['optSettings']
            if self.model.metadata.get('title','') == "":
               self.model.metadata['title'] = self.GetFileName(self.ModelEditor)
        except stimator.modelparser.StimatorParserError, expt:
                self.IndicateError(expt)
                sys.stdout = oldout
                return

        solution = stimator.dynamics.solve(self.model)
        sys.stdout = oldout
        newfig = resultsframe.newFigure()
        
        #stimator.dynamics.plot(solution, figure=newfig)
        solution.plot(figure=newfig)
        self.CreateResPanelFromFigure(newfig)
        self._mgr.Update()

    def OnMsg(self, evt):
        self.write(evt.msg)

    def OnEndComputation(self, evt):
        sys.stdout = self.oldout
        self.PostProcessEnded(aborted = (evt.exitCode == -1))
        self.optimizerThread = None

    def PostProcessEnded(self, aborted = False):
        solver = self.optimizerThread.solver        
        if aborted:
            self.write("\nOptimization aborted by user!")
        else:
            self.write(solver.reportFinalString())
            reportText = solver.optimum.info()
            self.write(reportText)
            self.CreateResPanel(self.model, solver)
        
        self.shell.prompt()
        self._mgr.Update()

    def msgTick(self, msg):
        evt = MsgEvent(msg = msg+'\n')
        wx.PostEvent(self, evt)

    def finalTick(self, exitCode):
        evt = EndComputationEvent(exitCode = exitCode)
        wx.PostEvent(self, evt)

    def endScript(self):
        evt = EndScriptEvent()
        wx.PostEvent(self, evt)

    def OnEndScript(self, event):
        for f in self.ui.figures:
            self.CreateResPanelFromFigure(f)
        self._mgr.Update()
        self.shell.prompt()
        self.calcscriptThread = None
        self.ui.reset()

    def OnRunScript(self, event):
        if (self.optimizerThread is not None) or (self.optimizerThread is not None):
           self.MessageDialog("S-timator is performing a computation!\nPlease wait.", "Error")
           return

        self.write('\n')
        self.ui.reset()
        oldout = sys.stdout
        self.oldcwd = os.getcwd()
        swd = self.GetModelFileDir(self.ScriptEditor)
        if swd == '.':
            self.cwd = os.getcwd()
        else:
            self.cwd = swd
        os.chdir(self.cwd)
        codelines = "\n".join([self.ScriptEditor.
                GetLine(i).
                rstrip() 
                for i in range(self.ScriptEditor.GetLineCount())])
        cbytes = compile(codelines,'<string>', 'exec')
        lcls = {}
        lcls['ui'] = self.ui
        sys.stdout = MyWriter(self)
        self.calcscriptThread=CalcScriptThread()
        self.calcscriptThread.Start(cbytes, lcls, self)
##         sys.stdout = MyImmediateWriter(self)
##         try:
##             exec cbytes in lcls
##         except:
##             print 'Interrupted'
##         #execfile('bof2.py')
##         sys.stdout = oldout
##         self.shell.prompt()

##------------- a facade, available to scripts to control the GUI
class gui_facade(object):
    def __init__(self, sframe, glock):
        self.sframe = sframe
        self.glock = glock
        self.reset()
    def reset(self):
        self.nticks = 0
        self.maxticks = 50
        self.figures = []
    def checkpoint(self):
        self.glock.acquire()
        mustexit = self.sframe.stop_script
        self.sframe.stop_script = False
        self.glock.release()
        if mustexit:
            raise ScriptInterruptSignal()
    
    def set_model_text(self,text):
        self.sframe.ModelEditor.SetText(text)
        
    def load_model(self,filename):
        self.sframe.OpenFile(filename, self.sframe.ModelEditor)
        return self.model()
    
    def clear(self):
        self.sframe.shell.clear()

    def model(self):
        textlines = [self.sframe.ModelEditor.GetLine(i) for i in range(self.sframe.ModelEditor.GetLineCount())]
        try:
            model = stimator.modelparser.read_model(textlines)
        except stimator.modelparser.StimatorParserError, expt:
                print "In file", filename, ':'
                self.sframe.IndicateError(expt)
                raise ScriptModelError()
        return model

    def ok_cancel(self,title,text):
        res = self.sframe.OkCancelDialog(title,text)
        return res
    
    def demo_plot(self):
        self.figures.append(resultsframe.newDemoFigure())
    
    def new_figure(self):
        newfig = resultsframe.newFigure()
        self.figures.append(newfig)
        return newfig
        

##------------- Writer classes

class MyWriter(object):
    def __init__(self, output_window):
        self.owin = output_window

    def write(self, txt):
        evt = MsgEvent(msg = txt)
        wx.PostEvent(self.owin, evt)

class MyImmediateWriter(object):
    def __init__(self, output_window):
        self.owin = output_window

    def write(self, txt):
        self.owin.write(txt)
        self.owin.Update()

class MyLog(wx.PyLog):
    def __init__(self, textCtrl, logTime=0):
        wx.PyLog.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogString(self, message, timeStamp):
        if self.tc:
            self.tc.AppendText(message)
            self.tc.GotoLine(self.tc.GetLineCount())

##------------- Computation thread classes

class ScriptInterruptSignal(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "Script interrupted by user"

class ScriptModelError(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ""

class CalcScriptThread:

    def Start(self, code, lcls, caller):
        self.code = code
        self.lcls = lcls
        self.caller = caller
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        while self.keepGoing:
            try:
                exec self.code in self.lcls
            except ScriptInterruptSignal, e:
                print e
            except ScriptModelError, e:
                pass
            except:
                print "Exception in script code:"
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60

            self.Stop()

        self.caller.endScript()
        self.running = False

class CalcOptmThread:

    def Start(self, solver):
        self.solver = solver
        self.keepGoing = self.running = self.notinterrupted = True
        thread.start_new_thread(self.Run, ())

    def Interrupt(self):
        self.notinterrupted = False
        print 'Stop required'
        self.Stop()

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        while self.keepGoing:
            self.solver.computeGeneration()
            if self.solver.exitCode !=0: self.Stop()

        self.solver.finalize()
        self.running = False

def run_wxgui():
    app = wx.App()
    frame = MyFrame(None)
    frame.Center()
    frame.Maximize()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    run_wxgui()
