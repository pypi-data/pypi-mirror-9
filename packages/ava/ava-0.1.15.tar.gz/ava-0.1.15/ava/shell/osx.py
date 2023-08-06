# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import os
import logging
import AppKit
from AppKit import *

from ava.shell import resource_path
from ava.shell.base import ShellBase, STR_EXIT, STR_STATUS, STR_OPEN_WEBFRONT


logger = logging.getLogger(__name__)


def applicationSupportFolder(self):
    paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,NSUserDomainMask,True)
    basePath = (len(paths) > 0 and paths[0]) or NSTemporaryDirectory()
    fullPath = basePath.stringByAppendingPathComponent_("Ava")
    if not os.path.exists(fullPath):
        os.mkdir(fullPath)
    return fullPath


def pathForFilename(self,filename):
    return self.applicationSupportFolder().stringByAppendingPathComponent_(filename)


class AppDelegate(NSObject):
    def init(self):
        #self = super(AppDelegate, self).init()
        if self is None:
            return None

        # Get objc references to the classes we need.
        self.NSUserNotification = objc.lookUpClass('NSUserNotification')
        self.NSUserNotificationCenter = objc.lookUpClass('NSUserNotificationCenter')

        return self

    def applicationDidFinishLaunching_(self, sender):
    	logger.debug("Application did finish launching.")

        logger.debug("Icon file: %s", resource_path('ava/res/eavatar.png'))
        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)
        self.icon = NSImage.alloc().initByReferencingFile_(resource_path('res/eavatar.png'))
        self.icon.setScalesWhenResized_(True)
        self.icon.setSize_((20, 20))
        self.statusitem.setImage_(self.icon)
#    	self.statusitem.setTitle_(u"影化身")
    	self.statusitem.setHighlightMode_(True)
    	self.statusitem.setEnabled_(True)

        #make the menu
        self.menubarMenu = NSMenu.alloc().init()

        self.menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(STR_OPEN_WEBFRONT, 'openMainFrame:', '')
        self.menubarMenu.addItem_(self.menuItem)

        self.menuItem = NSMenuItem.separatorItem()
        self.menubarMenu.addItem_(self.menuItem)

        self.quit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(STR_EXIT, 'terminate:', '')
        self.menubarMenu.addItem_(self.quit)

        #add menu to statusitem
        self.statusitem.setMenu_(self.menubarMenu)
        self.statusitem.setToolTip_(u'Ava - running')

    def applicationWillTerminate_(self,sender):
        logger.debug("Application will terminate.")

        self.shell.stop_server()
        self.shell.shell_stopped = True

    def alert(self, msg, title="Important Message"):
        self.app.activateIgnoringOtherApps_(True)
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(msg)
        alert.setAlertStyle_(NSInformationalAlertStyle)
        alert.runModal()

    def openMainFrame_(self, notification):
        logger.debug('Opening main UI...')

        self.shell.open_main_ui()

    def onQuitApp_(self, notification):
        self.shell.stop_server()

    def hello_(self, notification):
        self.alert("Message from Sam", "Hello There!!!")


class Shell(ShellBase):
    def __init__(self):
        super(Shell, self).__init__()

        self.app = None
        self.delegate = None
        self.mainframe = None

    def doIdle_(self, timer):
        super(Shell, self).check_server()
        if self.shell_stopped and self.app is not None:
            logger.debug("Request to terminate application.")
            self.app.terminate_(1)

    def run(self):
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(1, self, 'doIdle:', "", True)
        self.app = NSApplication.sharedApplication()
        self.delegate = AppDelegate.alloc().init()
        self.delegate.shell = self
        self.delegate.app = self.app
        self.app.setDelegate_(self.delegate)
        self.app.activateIgnoringOtherApps_(True)

        self.app.run()

if __name__ == '__main__':
    shell = Shell()
    shell.run()