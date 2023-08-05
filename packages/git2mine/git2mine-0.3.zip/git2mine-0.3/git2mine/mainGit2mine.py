#!/usr/bin/python2

import gtk
import time
import gobject
import threading
from git2mine import gitReader
from git2mine import redmineWriter

from os.path import abspath,dirname

ifaceDescPath = abspath(dirname(__file__) + "/frontend/git2mine.glade")

gobject.threads_init()

class Configuration:

    def __init__(self):
        _confLoaded = False

    @classmethod
    def setUserConf(self, settingsMap):
        self.__completeConfSetting(settingsMap)
        self._confLoaded = True

    @classmethod
    def isValid(self):
        return self._confLoaded

    @classmethod
    def getConf(self):
        raise NotImplementedError("getConf: Not implemented yet") #Abstract class

    @classmethod
    def __completeConfSetting(self,settingsMap):
        raise NotImplementedError("__completeConfSetting: Not implemented yet") #Abstract method
        
class GitConfiguration(Configuration):

    def __init__(self):
        self._confLoaded = False
        self._gitPath = ""

    @classmethod
    def setUserConf(self, settingsMap):
        self.__completeConfSetting(settingsMap)
        _confLoaded = True

    @classmethod
    def __completeConfSetting(self, settings):
        self._gitPath = settings["path"]

    @classmethod
    def getConf(self):
        ret = dict()
        ret['path'] = self._gitPath

    @classmethod
    def changePath(self, path):
        if self.isValid():
            self._gitPath = path

    @classmethod
    def gitEntry2row(self,entry):
        return [entry.commitTime.strftime("%Y%m%d"), entry.changeType, entry.taskId, round(entry.time/60.0,2), entry.description, "OK", True]

# class RedmineConfiguration(Configuration):
#
#     __serviceAddress = ""
#     __useKey = False
#     __key = ""
#     __user = ""
#     __password = ""
#
#     def __init__(self):
#         self._confLoaded = False
#         self.__serviceAddress = ""
#         self.__useKey = False
#         self.__key = ""
#         self.__user = ""
#         self.__password = ""
#
#     def __completeConfSetting(self, settings):
#         self.__serviceAddress = settings["address"]
#         self.__useKey = "key" in settings
#         if(self.__useKey):
#             self.__key = settings["key"]
#         else:
#             self.__user = settings["user"]
#             self.__password = settings["password"]
#
#     def getConf(self):
#         ret = dict()
#         ret['gitPaht'] = self._gitPath

gc = GitConfiguration()
loader = gtk.Builder()
loader.add_from_file(ifaceDescPath)
shownData = loader.get_object("liststore1")
win = loader.get_object("mainWindow")
activitiescombo = loader.get_object("comboboxtext1")
activitiesModel = loader.get_object("activitiesModel")

redmineServer = None

activitypos2id = []

def reloadEntries(entries):
    for e in entries:
        shownData.insert(-1,gc.gitEntry2row(e))

def changeType2str(ct):
    if ct == 'CI':
        return 'Improvement: '
    elif ct == 'INT':
        return 'Internal Change: '
    elif ct == 'BUG':
        return 'Bug Fix: '
    elif ct == 'NF: ':
        return 'New Functionality: '
    else:
        return ct + ' :';

from sys import stdout


def uploadEntries(pm, activeIndex = None):
    if redmineServer is None:
        md = gtk.MessageDialog(mainWindow,
                               gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                               gtk.BUTTONS_CLOSE, "Could not access to Redmine services")
        md.run()
        md.destroy()
        return
    for entry in shownData:
        if entry[-1]:
            #print([e for e in entry])
            entryOk = True
            try:
                commentText = changeType2str(entry[1]) + entry[4]
                #print("a=" + str(activeIndex))
                redmineServer.assignDedicatedTime(int(entry[2]),float(entry[3]), commentText,entry[0], activeIndex)
            except:
                entryOk = False
            #msgType =  gtk.MESSAGE_ERROR
            #msgText = "Entry upload failed for: " + commentText
            entry[-1] = not entryOk
            ##shownData.set_value(entry, len(entry)-1, not entryOk)
            #if entryOk
            #    msgType =  gtk.MESSAGE_INFO
            #    msgText = "Sent: " + commentText
            #md = gtk.MessageDialog(mainWindow,
            #                       gtk.DIALOG_DESTROY_WITH_PARENT, msgType,
            #                       gtk.BUTTONS_CLOSE, msgText)
            #md.run()
            #md.destroy()
            print(pm._currentTaskIdx)
            pm.currentCompleted()


class ProgressManager:
    _waitWin = loader.get_object("waitWindow")
    _taskLabel = loader.get_object("taskLabel")
    _pbar = loader.get_object("progressbar")
    _okButton = loader.get_object("okProgress")

    def __presentSt(self):
       #if self._currentTaskIdx < 0:
           #print("hide!")
           #self._waitWin.hide()
       #    return
       self._taskLabel.set_text(self._taskName)
       self._pbar.set_fraction(float(self._currentTaskIdx)/len(self._subTasks))
       self._pbar.set_text(self._subTasks[self._currentTaskIdx-1])


    def __init__(self, taskName, subTasks):
        _subTasks = []
        _taskName = "No Task"
        _currentTaskIdx = -1
        _waitWin = None
        _taskLabel = None
        _pbar = None

        self._taskName = taskName
        self._subTasks = subTasks

        #loader = gtk.Builder()
        #loader.add_from_file(ifaceDescPath)
        print("Init PM for " + taskName)

        if len(subTasks) < 1:
            self._currentTaskIdx = -1
        else:
            self._okButton.set_sensitive(False)
            self._currentTaskIdx = 0

        self.__presentSt()
        self._waitWin.show_all()

    def currentCompleted(self):
        print("current completed: " + str(self._currentTaskIdx))
        self._currentTaskIdx += 1
        if self._currentTaskIdx >= len(self._subTasks):
            #self._currentTaskIdx = -1
            #self._subTasks = []
            self._okButton.set_sensitive(True)
        #    return
        self.__presentSt()

def changeAllEntriesSelectState(newState):
    for entry in shownData:
        entry[-1] = newState

class SignalsHandler:

    def onDeleteMainWindow(self, *args):
        gtk.main_quit(*args)

    def onGitPathChanged(self, *args):
        shownData.clear()
        fp = args[0].get_filename()
        if fp is None or len(fp) == 0:
            print("No folder selected")
            return
        gc.setUserConf({"path": fp})
        entries = gitReader.readCommits(fp)
        reloadEntries(entries)

    def changeItemSelectedState(self, *args):
        idx = int(args[1])
        if idx >= 0 and idx < len(shownData):
            shownData[idx][-1] = not shownData[idx][-1]

    def unselectClicked(self, *args):
        changeAllEntriesSelectState(False)

    def selectClicked(self, *args):
        changeAllEntriesSelectState(True)

    def uploadClicked(self, *args):
        pm = ProgressManager("Uploading entries", [changeType2str(e[1]) + e[4] for e in filter(lambda entry: entry[-1], shownData)])
        #pm = None
        activeIndex = activitiescombo.get_active()
        if activeIndex < 0:
            activeIndex = None
        else:
            activeIndex = activitypos2id[activeIndex]

        ut = threading.Thread(target=uploadEntries,args=(pm,activeIndex))
        #ut = threading.Thread(target=uploadEntries)
        ut.start()
        #uploadEntries()

    def okProgress_clicked_cb(self, *args):
        v = ProgressManager._waitWin
        if v is not None:
            v.hide()


    def rconfigClicked(self,*args):
        #activitiescombo.append_text("hola")
        #activitiescombo.set_sensitive(True)
        #return
        url = loader.get_object("redmine_url")
        user = loader.get_object("redmine_user")
        password = loader.get_object("redmine_password")
        key = loader.get_object("redmine_key")
        #if redmineServer is not None:
        #    redmineServer.
        keyVal = key.get_text()
        userVal = user.get_text()
        passVal = password.get_text()

        if len(keyVal) == 0:
            keyVal = None
        if len(userVal) == 0:
            userVal = None
        if len(passVal) == 0:
            passVal = None

        global redmineServer

        if keyVal is not None and len(keyVal)>0:
            userVal = None
            passVal = None
        else:
            keyVal = None

        try:
            redmineServer = redmineWriter.RedmineWriter(url.get_text(), key=keyVal, user=userVal, password=passVal)
        except:
            redmineServer = None
        global activitypos2id
        activitypos2id = []
        #activitiescombo.clear()
        activitiescombo.set_sensitive(False)
        try:
            for atup in redmineServer.getListOfActivities():
                activitiescombo.append_text(atup[1])
                activitypos2id.append(atup[0])
            activitiescombo.set_sensitive(True)
        except:
            activitypos2id = []
            activitiescombo.clear()

        if not redmineServer.isConnected():
            redmineServer = None
            md = gtk.MessageDialog(mainWindow,
                              gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                              gtk.BUTTONS_CLOSE, "Invalid server connection paramaeters")
            md.run()
            md.destroy()
        else:
            md = gtk.MessageDialog(mainWindow,
                          gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                          gtk.BUTTONS_CLOSE, "Connected to Redmine")
            md.run()
            md.destroy()

    #Field changes
    def onDateChanged(self,*args):
        idx = args[1]
        val = args[2]
        shownData[idx][0] = val


    def onHoursEdit(self,*args):
        idx = args[1]
        val = round(float(args[2]),2)
        shownData[idx][3] = val



loader.connect_signals(SignalsHandler())

mainWindow = loader.get_object("mainWindow")
mainWindow.show_all()

gtk.main()
