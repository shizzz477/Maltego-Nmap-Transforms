"""Easy to use dialogs.

Message(msg) -- display a message and an OK button.
AskString(prompt, default) -- ask for a string, display OK and Cancel buttons.
AskPassword(prompt, default) -- like AskString(), but shows text as bullets.
AskYesNoCancel(question, default) -- display a question and Yes, No and Cancel buttons.
GetArgv(optionlist, commandlist) -- fill a sys.argv-like list using a dialog
AskFileForOpen(...) -- Ask the user for an existing file
AskFileForSave(...) -- Ask the user for an output file
AskFolder(...) -- Ask the user to select a folder
bar = Progress(label, maxvalue) -- Display a progress bar
bar.set(value) -- Set value
bar.inc( *amount ) -- increment value by amount (default=1)
bar.label( *newlabel ) -- get or set text label.

More documentation in each function.
This module uses DLOG resources 260 and on.
Based upon STDWIN dialogs with the same names and functions.
"""
#/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2008 Lukas Sedenka All rights reserved.
#
import os
import sys
try:
    import pygtk
    pygtk.require("2.0")
    import gtk
except:
    print "Error: PyGtk and GTK 2.xx must be installed to run this application. Exiting"
    sys.exit(1)
import string


__all__ = ['Message', 'AskString', 'AskPassword', 'AskYesNoCancel',
    'GetArgv', 'AskFileForOpen', 'AskFileForSave', 'AskFolder',
    'ProgressBar']

def width(widget):
    return gtk.Window.get_size(widget)[0]
def height(widget):
    return gtk.Window.get_size(widget)[1]
def GetWindowRect(widget):
    rect = gtk.Window.get_size(widget)
    return rect    
def CenterWindow(widget):
    widget.set_position(gtk.WIN_POS_CENTER)
    """
    x=gtk.gdk.screen_width() // 2 - width(widget) // 2
    y = gtk.gdk.screen_height() // 2 - height(widget) // 2
    widget.set_gravity(gtk.gdk.GRAVITY_SOUTH_EAST)
    widget.move( x , y )
    """
def cr2lf(text):
    if '\r' in text:
        text = string.join(string.split(text, '\r'), '\n')
    return text

def lf2cr(text):
    if '\n' in text:
        text = string.join(string.split(text, '\n'), '\r')
    if len(text) > 253:
        text = text[:253] + '\311'
    return text
    
def AutoSizeDialog(dialog, center=True):
    for ch in dialog.get_children():
        for ch1 in ch.get_children():
            if type(ch1)==gtk.HSeparator:
                continue
            elif type(ch1)==gtk.Entry :
                continue
            elif type(ch1)==gtk.HButtonBox: 
                for ch2 in ch1.get_children():
                    if type(ch2)==gtk.ProgressBar :
                        continue
                    else: 
                        text=ch2.get_label()
                    if  7<len(text) :
                        upgtext=""
                        i=0
                        j=7
                        while j<=len(text):
                            while i<=j:
                                upgtext=upgtext + text[i]
                                i=i+1
                            upgtext=upgtext + "\n"
                            j=j+8
                        k=0
                        j=j-7    
                        while k<(len(text)-j):
                            upgtext=upgtext + text[k+j]
                            k=k+1
                            ch2.set_label(upgtext)
                    else:
                        ch2.set_label(text)
                    ch2.set_size_request(70, 30)
            elif ch1.get_name()=='GtkLabel':
                    text=ch1.get_label()
                    if  40<len(text) :
                        upgtext=""
                        i=0
                        j=40
                        while j<=len(text):
                            while i<=j:
                                upgtext=upgtext + text[i]
                                i=i+1
                            upgtext=upgtext + "\n"
                            j=j+41
                        k=0   
                        j=j-40 
                        while k<(len(text)-j):
                            upgtext=upgtext + text[k+j]
                            k=k+1
                            ch1.set_label(upgtext)
                    else:
                        ch1.set_label(text)
                        

    if center==True:
        CenterWindow(dialog)
    size= dialog.size_request()   
    if size[0]<  332:
        dialog.set_size_request(332, size[1])
    size= dialog.size_request() 
    if size[1]<99:
        dialog.set_size_request(size[0], 99)
    dialog.set_resizable(True)
    
def Message(msg, id=260, ok=None):
    # Return when the user clicks the OK button or presses Return.
    #The MESSAGE string can be at most 255 characters long.

    
    if not ok :
        ok="OK"
    dialog = gtk.Dialog("",
                     None,
                     gtk.DIALOG_MODAL,
                     ( ok, gtk.RESPONSE_NONE))
   
    label= gtk.Label(lf2cr(msg))
    label.set_justify(gtk.JUSTIFY_LEFT)
    dialog.vbox.pack_start(label, True,True, 10)
    label.show()
    label.set_alignment(0.05, 0.5)
    AutoSizeDialog(dialog, center=True)
    res=dialog.run()
    dialog.hide()
    
    if res== gtk.RESPONSE_DELETE_EVENT:
        dialog.destroy()
    if res==gtk.RESPONSE_OK:
        dialog.destroy()
    
    

def AskString(prompt, default = '', id=261, ok=None, cancel=None):
    
    """Display a PROMPT string and a text entry field with a DEFAULT string.

    Return the contents of the text entry field when the user clicks the
    OK button or presses Return.
    Return None when the user clicks the Cancel button.

    If omitted, DEFAULT is empty.

    The PROMPT and DEFAULT strings, as well as the return value,
    can be at most 255 characters long.
    """
    if ok==None :
        ok="OK"
    if cancel==None:
        cancel="Cancel"
        
    dialog = gtk.Dialog("",
                     None,
                     gtk.DIALOG_MODAL,
                     (cancel, gtk.RESPONSE_CANCEL, ok, gtk.RESPONSE_OK))
   
    
    label= gtk.Label(lf2cr(prompt))
    label.set_alignment(0.05, 0.5)
    dialog.vbox.pack_start(label, True,True, 5)
    label.show()
    entry=gtk.Entry(255)
    entry.set_text(lf2cr(default))
    dialog.vbox.pack_start(entry, True, True, 5)
    entry.show()
    AutoSizeDialog(dialog, center=True)
    res=dialog.run()
    dialog.hide()

    if res== gtk.RESPONSE_DELETE_EVENT:
        dialog.destroy()
    if res==gtk.RESPONSE_OK:
        return cr2lf(entry.get_text())
    if res==gtk.RESPONSE_CANCEL:  
        return None
        dialog.destroy()
        
def AskPassword(prompt, default='', id=264, ok=None, cancel=None):
    """Display a PROMPT string and a text entry field with a DEFAULT string.
    The string is displayed as bullets only.

    Return the contents of the text entry field when the user clicks the
    OK button or presses Return.
    Return None when the user clicks the Cancel button.

    If omitted, DEFAULT is empty.

    The PROMPT and DEFAULT strings, as well as the return value,
    can be at most 255 characters long.
    """
    if ok==None :
        ok="OK"
    if cancel==None:
        cancel="Cancel"
        
    dialog = gtk.Dialog("",
                     None,
                     gtk.DIALOG_MODAL,
                     (cancel, gtk.RESPONSE_CANCEL, ok, gtk.RESPONSE_OK))
   
    
    label= gtk.Label(prompt)
    label.set_alignment(0, 0.5)
    dialog.vbox.pack_start(label, True,True, 5)
    label.show()
    entry=gtk.Entry(255)
    entry.set_visibility(False)
    entry.set_invisible_char('*')
    entry.set_text(lf2cr(default))
    dialog.vbox.pack_start(entry, True, True, 5)
    entry.show()
    AutoSizeDialog(dialog, center=True)
    res=dialog.run()
    dialog.hide()
    if res== gtk.RESPONSE_DELETE_EVENT:
        dialog.destroy()
    if res==gtk.RESPONSE_OK:
        return  cr2lf(entry.get_text())
    if res==gtk.RESPONSE_CANCEL:
        return None  
        dialog.destroy()
        
def AskYesNoCancel(question, default=0, yes=None, no=None, cancel=None, id=262):
    """Display a QUESTION string which can be answered with Yes or No.

    Return 1 when the user clicks the Yes button.
    Return 0 when the user clicks the No button.
    Return -1 when the user clicks the Cancel button.

    When the user presses Return, the DEFAULT value is returned.
    If omitted, this is 0 (No).

    The QUESTION string can be at most 255 characters.
    """
    
    if yes==None :
        yes="Yes"
    if no==None:
        no="No"
    if cancel==None:
        cancel="Cancel"
        
    dialog = gtk.Dialog("",
                     None,
                     gtk.DIALOG_MODAL,
                     (no, gtk.RESPONSE_NO, cancel, gtk.RESPONSE_CANCEL, yes, gtk.RESPONSE_YES))
   
    label= gtk.Label(lf2cr(question))
    label.set_justify(gtk.JUSTIFY_LEFT)
    label.set_alignment(0.05, 0.5)
    dialog.vbox.pack_start(label, True,True, 10)
    label.show()
    AutoSizeDialog(dialog, center=True)
    res=dialog.run()
    dialog.hide()
    if res== gtk.RESPONSE_DELETE_EVENT:
        dialog.destroy()
        return 0
    if res==gtk.RESPONSE_YES:
        dialog.destroy()
        if default==0:
            return 1
        else:
            return default
    if res==gtk.RESPONSE_NO:
        return 0
    if res==gtk.RESPONSE_CANCEL:
        return -1
    
    
    
def _runGtkMain(*args):
    while gtk.events_pending():
        gtk.main_iteration()
        
class ProgressBar:
    def __init__(self, title="Working...", maxval=0, label="", id=263):
        self.dialog=gtk.Dialog(title,  None,  gtk.DIALOG_MODAL)
        self.maxval=maxval
        self.curval=0
        self.bar=gtk.ProgressBar()
        self.bar.show()
        self.dialog.action_area.pack_start(self.bar, True,True, 8)
        button=gtk.Button("Cancel")
        button.show()
        self.dialog.action_area.pack_start(button, True,True, 10)
        button.connect("clicked", self.button_del, self.dialog)
        self.text=gtk.Label()
        self.text.set_text(label)
        self.text.set_alignment(0.1, 0.8)
        self.dialog.vbox.pack_start(self.text, True, True, 2)
        AutoSizeDialog(self.dialog, center=True)
        self.dialog.show_all()

    def button_del(self, button, dialog):        
        self.__del__()
        
    def __del__(self):
        self.dialog.hide_all()
        self.dialog.destroy()
        
        
    def title(self, newstr=""):
        if newstr:
            self.dialog.set_title(newstr)
        _runGtkMain()
        
    def label( self, *newstr ):
        if newstr:
            self.text.set_text(lf2cr(*newstr))
            AutoSizeDialog(self.dialog, center=False)
        _runGtkMain()
    
    def _update(self, value):
        maxval=self.maxval
        if maxval == 0:     # an indeterminate bar
            progbar = self.bar
            progbar.pulse()
        else:               # a determinate bar
            if maxval > 32767:
                value = int(value/(maxval/32767.0))
                maxval = 32767
            maxval = int(maxval)
            value = int(value)
            progbar = self.bar
            progbar.set_fraction(float(value)/float(maxval))
        
        if not (self.dialog.flags() & gtk.VISIBLE):
            raise KeyboardInterrupt
        
        _runGtkMain()
       
    def set(self, value, max=None):
        """set(value) - Set progress bar position"""
        if max != None:
            self.maxval = max
            #if max <= 0: 
            #    pass # indeterminate bar
            #else:           # determinate bar
            #    pass
        if value < 0:
            value = 0
        elif value > self.maxval:
            value = self.maxval
        self.curval = value
        self._update(value)

    def inc(self, n=1):
        """inc(amt) - Increment progress bar position"""
        self.set(self.curval + n)
        

def AskFileForOpen(
        message=None,
        typeList=None,
        # From here on the order is not documented
        version=None,
        defaultLocation=None,
        dialogOptionFlags=None,
        location=None,
        clientName=None,
        windowTitle=None,
        actionButtonLabel=None,
        cancelButtonLabel=None,
        preferenceKey=None,
        popupExtension=None,
        eventProc=None,
        previewProc=None,
        filterProc=None,
        wanted=None,
        multiple=None,
        # the following are for implementation use only
        fname=None
        ):
    """Display a dialog asking the user for a file to open.

    wanted is the return type wanted: FSSpec, FSRef, unicode or string (default)
    the other arguments can be looked up in Apple's Navigation Services documentation

    Windows differences:

    typeList is used for the same purpose, but file type handling is different
    between Windows and Mac, so the form of this argument is different. In an
    attempt to remain as similar as possible, a list of extensions can be
    supplied (e.g., ['*', 'txt', 'bat']). A more complete form is also
    allowed: [('All Files (*.*)', '*.*'), ('C Files (*.c, *.h)', '*.c;*.h')].
    The first item in each tuple is the text description presented to the
    user. The second item in each tuple is a semi-colon seperated list of
    standard Windows wildcard patterns that will match files described in the
    text description.

    The folowing parameters are ignored on Windows:
    clientName, dialogOptionFlags, eventProc, filterProc, popupExtension,
    preferenceKey, previewProc, version, wanted
    """
    
    dlg = gtk.FileChooserDialog(windowTitle, 
                                action=gtk.FILE_CHOOSER_ACTION_OPEN, 
                                buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                         gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL))
    label=gtk.Label()
    label.show()
    dlg.get_child().pack_start(label, False, False, 0)
    dlg.get_child().reorder_child(dlg.get_child().get_children()[1], 0)
    
    if message:
        label.set_label(message)
    
    if multiple:
        dlg.set_select_multiple(multiple)
        
    if location:
        x=location[0]
        y=location[1]
        dlg.move(x, y)
    else:
        CenterWindow(dlg)

    if fname:
        dlg.set_current_folder(os.path.dirname(fname))
    elif defaultLocation:
        dlg.set_current_folder(defaultLocation)
    if actionButtonLabel:
        buttons[0].set_label(actionButtonLabel)
    if cancelButtonLabel:
        buttons[1].set_label(cancelButtonLabel)
    
    if typeList:
        filter=gtk.FileFilter()
        for i in typeList:
            filter.add_pattern(i)
        dlg.set_filter(filter)
    dlg.set_local_only(True)
    resp = dlg.run()
    fname = dlg.get_filename()
    dlg.hide()
    if resp == gtk.RESPONSE_CANCEL:
        return None
    return fname
    
def AskFileForSave(
        message=None,
        savedFileName=None,
        # From here on the order is not documented
        version=None,
        defaultLocation=None,
        dialogOptionFlags=None,
        location=None,
        clientName=None,
        windowTitle=None,
        actionButtonLabel=None,
        cancelButtonLabel=None,
        preferenceKey=None,
        popupExtension=None,
        eventProc=None,
        fileType=None,
        fileCreator=None,
        wanted=None,
        multiple=None):
    """Display a dialog asking the user for a filename to save to.

    wanted is the return type wanted: FSSpec, FSRef, unicode or string (default)
    the other arguments can be looked up in Apple's Navigation Services documentation

    Windows differences:

    fileType is used for the same purpose, but file type handling is different
    between Windows and Mac, so the form of this argument is different. In an
    attempt to remain as similar as possible, an extensions can be supplied
    (e.g., 'txt'). A more complete form is also	allowed:
    ('Text Files (*.txt)', '*.txt'). The first item in the tuple is the text
    description presented to the user. The second item in the tuple is a
    standard Windows wildcard pattern that will match files described in the
    text description.

    The folowing parameters are ignored on Windows:
    clientName, dialogOptionFlags, eventProc, fileCreator, filterProc,
    multiple, popupExtension, preferenceKey, previewProc, version, wanted
    """
    
    dlg = gtk.FileChooserDialog(windowTitle, 
                                action=gtk.FILE_CHOOSER_ACTION_SAVE, 
                                buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                         gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL))
    label=gtk.Label()
    label.show()
    dlg.get_child().pack_start(label, False, False, 0)
    dlg.get_child().reorder_child(dlg.get_child().get_children()[1], 0)
    
    if message:
        label.set_label(message)
    
    if multiple:
        dlg.set_select_multiple(multiple)
        
    if location:
        x=location[0]
        y=location[1]
        dlg.move(x, y)
    else:
        CenterWindow(dlg)

    if savedFileName:
        dlg.set_current_name(savedFileName)
    elif defaultLocation:
        dlg.set_current_folder(defaultLocation)
    if actionButtonLabel:
        buttons[0].set_label(actionButtonLabel)
    if cancelButtonLabel:
        buttons[1].set_label(cancelButtonLabel)
    
    if fileType:
        filter=gtk.FileFilter()
        for i in fileType:
            filter.add_pattern(i)
        dlg.set_filter(filter)
    dlg.set_local_only(True)
    resp = dlg.run()
    savedFileName = dlg.get_filename()
    dlg.hide()
    if resp == gtk.RESPONSE_CANCEL:
        return None
    return savedFileName
    
def AskFolder(
        message=None,
        # From here on the order is not documented
        version=None,
        defaultLocation=None,
        dialogOptionFlags=None,
        location=None,
        clientName=None,
        windowTitle=None,
        actionButtonLabel=None,
        cancelButtonLabel=None,
        preferenceKey=None,
        popupExtension=None,
        eventProc=None,
        filterProc=None,
        wanted=None,
        multiple=None):
    """Display a dialog asking the user for select a folder.

    wanted is the return type wanted: FSSpec, FSRef, unicode or string (default)
    the other arguments can be looked up in Apple's Navigation Services documentation

    Windows differences:

    The folowing parameters are ignored on Windows:
    clientName, dialogOptionFlags, eventProc, filterProc,
    multiple, popupExtension, preferenceKey, version, wanted
    """
    dlg = gtk.FileChooserDialog(windowTitle, 
                                buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                         gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL))
    dlg.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
    label=gtk.Label()
    label.show()
    dlg.get_child().pack_start(label, False, False, 0)
    dlg.get_child().reorder_child(dlg.get_child().get_children()[1], 0)
    
    if message:
        label.set_label(message)
    
    if multiple:
        dlg.set_select_multiple(multiple)
        
    if location:
        x=location[0]
        y=location[1]
        dlg.move(x, y)
    else:
        CenterWindow(dlg)

    if defaultLocation:
        dlg.set_current_folder(defaultLocation)
    if actionButtonLabel:
        buttons[0].set_label(actionButtonLabel)
    if cancelButtonLabel:
        buttons[1].set_label(cancelButtonLabel)
    
    dlg.set_local_only(True)
    resp = dlg.run()
    fname = dlg.get_filename()
    dlg.hide()
    if resp == gtk.RESPONSE_CANCEL:
        return None
    return fname
    
ARGV_ID=265
ARGV_ITEM_OK=1
ARGV_ITEM_CANCEL=2
ARGV_OPTION_GROUP=3
ARGV_OPTION_EXPLAIN=4
ARGV_OPTION_VALUE=5
ARGV_OPTION_ADD=6
ARGV_COMMAND_GROUP=7
ARGV_COMMAND_EXPLAIN=8
ARGV_COMMAND_ADD=9
ARGV_ADD_OLDFILE=10
ARGV_ADD_NEWFILE=11
ARGV_ADD_FOLDER=12
ARGV_CMDLINE_GROUP=13
ARGV_CMDLINE_DATA=14

def _setmenu(control, items):
    pom=gtk.ListStore(str)
    for item in items:
        if type(item) == type(()):
            label = item[0]
        else:
            label = item[0]
        if label[-1] == '=' or label[-1] == ':':
            label = label[:-1]
        pom.append([label])
    control.set_model(pom)
    control.set_active(0)
    
    
def _selectoption(d, optionlist, idx):
    if idx < 0 or idx >= len(optionlist):
        Message("Error")
        return
    option = optionlist[idx]
    if type(option) == type(()):
        if len(option) == 4:
            help = option[2]
        elif len(option) > 1:
            help = option[-1]
        else:
            help = ''
    else:
        help = ''
    h = _getDialogItem(d, "ARGV_OPTION_EXPLAIN")
    if help and len(help) > 250:
        help = help[:250] + '...'
    h.set_label(help)
    hasvalue = 0
    if type(option) == type(()):
        label = option[0]
    else:
        label = option
    if label[-1] == '=' or label[-1] == ':':
        hasvalue = 1
    h = _getDialogItem(d, "ARGV_OPTION_VALUE")
    h.set_text('')
    if hasvalue:
        h.show()
    else:
        h.hide()
        
def _getDialogItem(d, name):
    a=0
    for i in d.get_children():
        if i.get_name()==name:
            return i
            a=1
        else:
            for j in i.get_children():
                if j.get_name()==name:
                    return j
                    a=1
                else:
                    if type(j)!=gtk.HSeparator:
                       for k in j.get_children():
                            if k.get_name()==name:
                                return k
                                a=1
                            else:
                                if k.is_composited():
                                    for l in k.get_children():
                                        if l.get_name()==name:
                                            return l
                                            a=1
    if a==0:
        raise RuntimeError, "Unknown dialog item "+ name
 
def _action(widget, dialog, list):
    
    stringstoadd = []
    if widget.get_name()== "ARGV_OPTION_GROUP":
        it = _getDialogItem(dialog,"ARGV_OPTION_GROUP")
        idx=it.get_active()
        _selectoption(dialog, list, idx)
    elif widget.get_name()== "ARGV_OPTION_VALUE":
        pass
    elif widget.get_name()== "ARGV_OPTION_ADD":
        it=_getDialogItem(dialog, "ARGV_OPTION_GROUP")
        idx = it.get_active()
        if 0 <= idx < len(list):
            option = list[idx]
            if type(option) == type(()):
                option = option[0]
            if option[-1] == '=' or option[-1] == ':':
                option = option[:-1]
                h = _getDialogItem(dialog, "ARGV_OPTION_VALUE")
                value = h.get_text()
            else:
                value = ''
            if len(option) == 1:
                stringtoadd = '-' + option
            else:
                stringtoadd = '--' + option
            stringstoadd = [stringtoadd]
            if value:
                stringstoadd.append(value)
        else:
            Message("Error")
            
    elif widget.get_name()== "ARGV_COMMAND_GROUP":
        it=_getDialogItem(dialog, "ARGV_COMMAND_GROUP")
        idx = it.get_active()
        if 0 <= idx < len(list) and type(list[idx]) == type(()) and \
                len(list[idx]) > 1:
            help = list[idx][-1]
            h = _getDialogItem(dialog, "ARGV_COMMAND_EXPLAIN")
            h.set_text(help)
            
    elif widget.get_name()=="ARGV_COMMAND_ADD":
        it=_getDialogItem(dialog, "ARGV_COMMAND_GROUP")
        idx = it.get_active()
        if 0 <= idx < len(list):
            command = list[idx]
            if type(command) == type(()):
                command = command[0]
            stringstoadd = [command]
        else:
            Message("Error")
    elif widget.get_name()== "ARGV_ADD_OLDFILE":
        pathname = AskFileForOpen()
        if pathname:
            stringstoadd = [pathname]
    elif widget.get_name()== "ARGV_ADD_NEWFILE":
        pathname = AskFileForSave()
        if pathname:
            stringstoadd = [pathname]
    elif widget.get_name()== "ARGV_ADD_FOLDER":
        pathname = AskFolder()
        if pathname:
            stringstoadd = [pathname]
    elif widget.get_name()== "ARGV_CMDLINE_DATA":
        pass # Nothing to do
    else:
        raise RuntimeError, "Unknown dialog item %d"%n    
           
    for stringtoadd in stringstoadd:
            if '"' in stringtoadd or "'" in stringtoadd or " " in stringtoadd:
                stringtoadd = repr(stringtoadd)
            i=_getDialogItem(dialog, "ARGV_CMDLINE_DATA")
            oldstr=i.get_text()
            if oldstr and oldstr[-1] != ' ':
                oldstr = oldstr + ' '
            oldstr = oldstr + stringtoadd
            if oldstr[-1] != ' ':
                oldstr = oldstr + ' '
            i.set_text(oldstr)
    i=_getDialogItem(dialog, "ARGV_CMDLINE_DATA")        
    oldstr = i.get_text()
    tmplist = string.split(oldstr)
    newlist = []
    while tmplist:
        item = tmplist[0]
        del tmplist[0]
        if item[0] == '"':
            while item[-1] != '"':
                if not tmplist:
                    raise RuntimeError, "Unterminated quoted argument"
                item = item + ' ' + tmplist[0]
                del tmplist[0]
            item = item[1:-1]
        if item[0] == "'":
            while item[-1] != "'":
                if not tmplist:
                    raise RuntimeError, "Unterminated quoted argument"
                item = item + ' ' + tmplist[0]
                del tmplist[0]
            item = item[1:-1]
        newlist.append(item)
    return newlist
 
def GetArgv(optionlist=None, commandlist=None, addoldfile=1, addnewfile=1, addfolder=1, id=ARGV_ID):
    dialog = gtk.Dialog("",
                     None,
                     gtk.DIALOG_MODAL,
                     ( gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

    # Optionlist panel
    opanel=gtk.Table(4, 2, True)
    
    olabel=gtk.Label("Option: ")
    olabel.set_justify(gtk.JUSTIFY_LEFT)
    opanel.attach(olabel, 0, 1, 0, 1)
    
    olabel1=gtk.Label()
    olabel1.set_name("ARGV_OPTION_EXPLAIN")
    olabel1.set_justify(gtk.JUSTIFY_LEFT)
    opanel.attach(olabel1, 0, 2, 1, 2)
    
    oentry=gtk.Entry()
    oentry.set_name("ARGV_OPTION_VALUE")
    opanel.attach(oentry, 0, 2, 2, 3)
    
    obutton=gtk.Button("Add")
    obutton.set_name("ARGV_OPTION_ADD")
    obutton.connect("clicked", _action, dialog, optionlist)
    opanel.attach(obutton, 1, 2, 3, 4, 0, gtk.FILL)
    
    optionl=gtk.ComboBox()
    ocell= gtk.CellRendererText()
    optionl.pack_start(ocell, True)
    optionl.add_attribute(ocell, 'text', 0)
    opanel.attach(optionl,  1, 2, 0, 1)
    optionl.set_name("ARGV_OPTION_GROUP")
    
    for i in opanel.get_children():
        if type(i)==gtk.Label:
            i.set_alignment(0.1, 0.5)

    # Commandlist panel
    cpanel=gtk.Table(3, 2, True)
    
    clabel1=gtk.Label()
    clabel1.set_name("ARGV_COMMAND_EXPLAIN")
    clabel1.set_justify(gtk.JUSTIFY_LEFT)
    cpanel.attach(clabel1, 0, 1, 1, 2)

    clabel=gtk.Label("Command: ")
    clabel.set_justify(gtk.JUSTIFY_LEFT)
    cpanel.attach(clabel, 0, 1, 0, 1)
    
    cbutton=gtk.Button("Add")
    cbutton.set_name("ARGV_COMMAND_ADD")
    cbutton.connect("clicked", _action, dialog, commandlist)
    cpanel.attach(cbutton, 1, 2, 2, 3, 0, gtk.FILL)
    
    cptionl=gtk.ComboBox()
    cptionl.set_name("ARGV_COMMAND_GROUP")
    ccell= gtk.CellRendererText()
    cptionl.pack_start(ccell, True)
    cptionl.add_attribute(ccell, 'text', 0)
    cpanel.attach(cptionl,  1, 2, 0, 1)
    for i in cpanel.get_children():
        if type(i)==gtk.Label:
            i.set_alignment(0.1, 0.5)

    # ButtonBox
    bbox=gtk.Table(2, 2)
    bbox.attach(gtk.Button("Add file..."), 0, 1, 0, 1, gtk.FILL, 0)
    bbox.attach(gtk.Button("Add new file..."), 1, 2, 0, 1, gtk.FILL,0)
    bbox.attach(gtk.Button("Add folder..."), 0, 1, 1, 2, gtk.FILL, 0)
    bbox.get_children()[0].set_name("ARGV_ADD_FOLDER")
    bbox.get_children()[0].connect("clicked", _action,  dialog, None)
    bbox.get_children()[1].set_name("ARGV_ADD_NEWFILE")
    bbox.get_children()[1].connect("clicked", _action,  dialog, None)
    bbox.get_children()[2].set_name("ARGV_ADD_OLDFILE")
    bbox.get_children()[2].connect("clicked", _action,  dialog, None)
    
    # Command Line
    cl=gtk.Table(2, 1)
    
    cllabel=gtk.Label("Command line: ")
    cllabel.set_alignment(0.1, 0.1)
    cl.attach(cllabel, 0, 1, 0, 1, gtk.FILL, 0)
    
    clentry=gtk.Entry()
    clentry.set_text("")
    clentry.set_name("ARGV_CMDLINE_DATA")
    cl.attach(clentry, 0, 2, 1, 2)
    
    # Add into dialog
    dialog.vbox.pack_start(opanel,  False, False, 5)
    dialog.vbox.pack_start(gtk.HSeparator(),  True, True, 10)
    dialog.vbox.pack_start(cpanel,  False, False, 5)
    dialog.vbox.pack_start(gtk.HSeparator(),  True, True, 10)
    dialog.vbox.pack_start(bbox,  False, False, 5)
    dialog.vbox.pack_start(gtk.HSeparator(),  True, True, 10)
    dialog.vbox.pack_start(cl,  False, False, 5)
    dialog.set_size_request(340, 450)
    dialog.show_all()
    oentry.hide()
    
    if optionlist:
        _setmenu(optionl, optionlist)
        optionl.set_active(0)
        _action(optionl, dialog, optionlist)
    else:
        opanel.set_state(gtk.STATE_INSENSITIVE)
        
    optionl.connect("changed",_action, dialog, optionlist)
    
    if commandlist:
        _setmenu(cptionl, commandlist)
        cptionl.set_active(0)        
        if type(commandlist[0]) == type(()) and len(commandlist[0]) > 1:
            help = commandlist[0][-1]
            clabel1.set_label(help)
    else:
        cpanel.set_state(gtk.STATE_INSENSITIVE)
    cptionl.connect("changed",_action, dialog, commandlist)
    
    
    if not addoldfile:
        bbox.get_children()[2].set_state(gtk.STATE_INSENSITIVE)
    if not addnewfile:
        bbox.get_children()[1].set_state(gtk.STATE_INSENSITIVE)
    if not addfolder:
        bbox.get_children()[0].set_state(gtk.STATE_INSENSITIVE)
        
    res=dialog.run()
    dialog.hide()

    if res== gtk.RESPONSE_CANCEL:
        dialog.destroy()
        sys.exit(1)
    if res== gtk.RESPONSE_DELETE_EVENT:
        dialog.destroy()
        sys.exit(1)
    if res==gtk.RESPONSE_OK:
        return _action(clentry, dialog, None)


def test():
    import time

    class empty: pass
    Carbon = empty()
    Carbon.File = empty()
    Carbon.File.FSSpec = None
    Carbon.File.FSRef = None
    MacOS = empty()

    Message("Testing EasyDialogs.")
    optionlist = (('v', 'Verbose'), ('verbose', 'Verbose as long option'),
                ('flags=', 'Valued option'), ('f:', 'Short valued option'))
    commandlist = (('start', 'Start something'), ('stop', 'Stop something'))
    argv = GetArgv(optionlist=optionlist, commandlist=commandlist, addoldfile=0)
    Message("Command line: %s"%' '.join(argv))
    for i in range(len(argv)):
        print 'arg[%d] = %r' % (i, argv[i])
    ok = AskYesNoCancel("Do you want to proceed?")
    ok = AskYesNoCancel("Do you want to identify?", yes="Identify", no="No")
    if ok > 0:
        s = AskString("Enter your first name", "Joe")
        s2 = AskPassword("Okay %s, tell us your nickname"%s, s, cancel="None")
        if not s2:
            Message("%s has no secret nickname"%s)
        else:
            Message("Hello everybody!!\nThe secret nickname of %s is %s!!!"%(s, s2))
    else:
        s = 'Anonymous'
    rv = AskFileForOpen(message="Gimme a file, %s"%s, wanted=Carbon.File.FSSpec)
    Message("rv: %s"%rv)
    rv = AskFileForSave(wanted=Carbon.File.FSRef, savedFileName="%s.txt"%s)
    Message("rv: %s"%rv) # was: Message("rv.as_pathname: %s"%rv.as_pathname())
    rv = AskFolder()
    Message("Folder name: %s"%rv)
    text = ( "Working Hard...", "Hardly Working..." ,
            "So far, so good!", "Keep on truckin'" )
    bar = ProgressBar("Progress, progress...", 0, label="Ramping up...")
    try:
        if hasattr(MacOS, 'SchedParams'):
            appsw = MacOS.SchedParams(1, 0)
        for i in xrange(20):
            bar.inc()
            time.sleep(0.05)
        bar.set(0,100)
        for i in xrange(100):
            bar.set(i)
            time.sleep(0.05)
            if i % 10 == 0:
                bar.label(text[(i//10) % 4])
        bar.label("Done.")
        time.sleep(1.0)     # give'em a chance to see "Done."
    finally:
        del bar
        if hasattr(MacOS, 'SchedParams'):
            MacOS.SchedParams(*appsw)

if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        Message("Operation Canceled.")
