# -*- coding: utf-8 -*-
'''
Copyright (C) 2012-2015  Diego Torres Milano
Created on oct 6, 2014

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Diego Torres Milano

'''

__version__ = '9.6.0'

import sys
import threading
import warnings
import copy
import string
import os
import platform
from Tkconstants import DISABLED

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except:
    PIL_AVAILABLE = False

try:
    import Tkinter
    import tkSimpleDialog
    import tkFileDialog
    import tkFont
    import ScrolledText
    TKINTER_AVAILABLE = True
except:
    TKINTER_AVAILABLE = False

from ast import literal_eval as make_tuple

DEBUG = False
DEBUG_MOVE = DEBUG and False
DEBUG_TOUCH = DEBUG and False
DEBUG_POINT = DEBUG and False
DEBUG_KEY = DEBUG and True
DEBUG_ISCCOF = DEBUG and False


class Color:
    GOLD = '#d19615'
    GREEN = '#15d137'
    BLUE = '#1551d1'
    MAGENTA = '#d115af'
    DARK_GRAY = '#222222'
    LIGHT_GRAY = '#dddddd'

class Unit:
    PX = 'PX'
    DIP = 'DIP'

class Operation:
    ASSIGN = 'assign'
    DEFAULT = 'default'
    DRAG = 'drag'
    DUMP = 'dump'
    TEST = 'test'
    TEST_TEXT = 'test_text'
    TOUCH_VIEW = 'touch_view'
    TOUCH_POINT = 'touch_point'
    LONG_TOUCH_POINT = 'long_touch_point'
    TYPE = 'type'
    PRESS = 'press'
    SNAPSHOT = 'snapshot'
    SLEEP = 'sleep'
    TRAVERSE = 'traverse'
    VIEW_SNAPSHOT = 'view_snapshot'

class Culebron:
    APPLICATION_NAME = "Culebra"

    UPPERCASE_CHARS = string.uppercase[:26]
    
    KEYSYM_TO_KEYCODE_MAP = {
        'Home': 'HOME',
        'BackSpace': 'BACK',
        'Left': 'DPAD_LEFT',
        'Right': 'DPAD_RIGHT',
        'Up': 'DPAD_UP',
        'Down': 'DPAD_DOWN',
         }
     
    KEYSYM_CULEBRON_COMMANDS = {
        'F1': None,
        'F5': None
        }

    canvas = None
    imageId = None
    vignetteId = None
    areTargetsMarked = False
    isDragDialogShowed = False
    isGrabbingTouch = False
    isGeneratingTestCondition = False
    isTouchingPoint = False
    isLongTouchingPoint = False
    onTouchListener = None
    snapshotDir = '/tmp'
    snapshotFormat = 'PNG'
    
    @staticmethod
    def checkDependencies():
        if not PIL_AVAILABLE:
            raise Exception('''PIL or Pillow is needed for GUI mode

On Ubuntu install

   $ sudo apt-get install python-imaging python-imaging-tk

On OSX install

   $ brew install homebrew/python/pillow
''')
        if not TKINTER_AVAILABLE:
            raise Exception('''Tkinter is needed for GUI mode

This is usually installed by python package. Check your distribution details.
''')

    def __init__(self, vc, printOperation, scale=1):
        '''
        Culebron constructor.
        
        @param vc: The ViewClient used by this Culebron instance
        @type vc: ViewClient
        @param printOperation: the method invoked to print operations to the script
        @type printOperation: method
        @param scale: the scale of the device screen used to show it on the window
        @type scale: float
        '''
        
        self.vc = vc
        self.printOperation = printOperation
        self.device = vc.device
        self.serialno = vc.serialno
        self.scale = scale
        self.window = Tkinter.Tk()
        self.mainMenu = MainMenu(self)
        self.window.config(menu=self.mainMenu)
        self.statusBar = StatusBar(self.window)
        self.statusBar.pack(side=Tkinter.BOTTOM, padx=2, pady=2, fill=Tkinter.X)
        self.statusBar.set("Always press F1 for help")

    def takeScreenshotAndShowItOnWindow(self):
        '''
        Takes the current screenshot and shows it on the main window.
        It also:
         - sizes the window
         - create the canvas
         - set the focus
         - enable the events
         - create widgets
         - finds the targets (as explained in L{findTargets})
         - hides the vignette (that could have been showed before)
        '''
        
        if DEBUG:
            print >> sys.stderr, "takeScreenshotAndShowItOnWindow()"
        self.unscaledScreenshot = self.device.takeSnapshot(reconnect=True)
        self.image = self.unscaledScreenshot
        (width, height) = self.image.size
        if self.scale != 1:
            self.image = self.image.resize((int(width*self.scale), int(height*self.scale)), Image.ANTIALIAS)
            (width, height) = self.image.size
        if self.canvas is None:
            if DEBUG:
                print >> sys.stderr, "Creating canvas", width, 'x', height
            self.canvas = Tkinter.Canvas(self.window, width=width, height=height)
            self.canvas.focus_set()
            self.enableEvents()
            self.createMessageArea(width, height)
            self.createVignette(width, height)
        self.screenshot = ImageTk.PhotoImage(self.image)
        if self.imageId is not None:
            self.canvas.delete(self.imageId)
        self.imageId = self.canvas.create_image(0, 0, anchor=Tkinter.NW, image=self.screenshot)
        try:
            self.canvas.pack_info()
        except:
            self.canvas.pack(fill=Tkinter.BOTH)
        self.findTargets()
        self.hideVignette()

    def createMessageArea(self, width, height):
        self.__message = Tkinter.Label(self.window, text='', background=Color.GOLD, font=('Helvetica', 16), anchor=Tkinter.W)
        self.__message.configure(width=width)
        self.__messageAreaId = self.canvas.create_window(0, 0, anchor=Tkinter.NW, window=self.__message)
        self.canvas.itemconfig(self.__messageAreaId, state='hidden')
        self.isMessageAreaVisible = False
        
    def showMessageArea(self):
        if self.__messageAreaId:
            self.canvas.itemconfig(self.__messageAreaId, state='normal')
            self.isMessageAreaVisible = True
            self.canvas.update_idletasks()
    
    def hideMessageArea(self):
        if self.__messageAreaId and self.isMessageAreaVisible:
            self.canvas.itemconfig(self.__messageAreaId, state='hidden')
            self.isMessageAreaVisible = False
            self.canvas.update_idletasks()

    def toggleMessageArea(self):
        if self.isMessageAreaVisible:
            self.hideMessageArea()
        else:
            self.showMessageArea()

    def message(self, text, background=None):
        self.__message.config(text=text)
        if background:
            self.__message.config(background=background)
        self.showMessageArea()

    def toast(self, text, background=None, timeout=5):
        if DEBUG:
            print >> sys.stderr, "toast(", text, ",", background,  ")"
        self.message(text, background)
        if text:
            t = threading.Timer(timeout, self.hideMessageArea)
            t.start()
        else:
            self.hideMessageArea()

    def createVignette(self, width, height):
        if DEBUG:
            print >> sys.stderr, "createVignette(%d, %d)" % (width, height)
        self.vignetteId = self.canvas.create_rectangle(0, 0, width, height, fill=Color.MAGENTA,
            stipple='gray50')
        font = tkFont.Font(family='Helvetica',size=int(144*self.scale))
        msg = "Please\nwait..."
        self.waitMessageShadowId = self.canvas.create_text(width/2+2, height/2+2, text=msg,
            fill=Color.DARK_GRAY, font=font)
        self.waitMessageId = self.canvas.create_text(width/2, height/2, text=msg,
            fill=Color.LIGHT_GRAY, font=font)
        self.canvas.update_idletasks()
    
    def showVignette(self):
        if DEBUG:
            print >> sys.stderr, "showVignette()"
        if self.canvas is None:
            return
        if self.vignetteId:
            if DEBUG:
                print >> sys.stderr, "    showing vignette"
            # disable events while we are processing one
            self.disableEvents()
            self.canvas.lift(self.vignetteId)
            self.canvas.lift(self.waitMessageShadowId)
            self.canvas.lift(self.waitMessageId)
            self.canvas.update_idletasks()
    
    def hideVignette(self):
        if DEBUG:
            print >> sys.stderr, "hideVignette()"
        if self.canvas is None:
            return
        if self.vignetteId:
            if DEBUG:
                print >> sys.stderr, "    hiding vignette"
            self.canvas.lift(self.imageId)
            self.canvas.update_idletasks()
            self.enableEvents()

    def deleteVignette(self):
        if self.canvas is not None:
            self.canvas.delete(self.vignetteId)
            self.vignetteId = None
            self.canvas.delete(self.waitMessageShadowId)
            self.waitMessageShadowId = None
            self.canvas.delete(self.waitMessageId)
            self.waitMessageId = None

    def showPopupMenu(self, event):
        (scaledX, scaledY) = (event.x/self.scale, event.y/self.scale)
        v = self.findViewContainingPointInTargets(scaledX, scaledY)
        ContextMenu(self, view=v).showPopupMenu(event)

    def showHelp(self):
        d = HelpDialog(self)
        self.window.wait_window(d)

    def findTargets(self):
        '''
        Finds the target Views (i.e. for touches).
        '''
        
        if DEBUG:
            print >> sys.stderr, "findTargets()"
        LISTVIEW_CLASS = 'android.widget.ListView'
        ''' The ListView class name '''
        self.targets = []
        ''' The list of target coordinates (x1, y1, x2, y2) '''
        self.targetViews = []
        ''' The list of target Views '''
        if self.device.isKeyboardShown():
            print >> sys.stderr, "#### keyboard is show but handling it is not implemented yet ####"
            # fixme: still no windows in uiautomator
            window = -1
        else:
            window = -1
        dump = self.vc.dump(window=window)
        self.printOperation(None, Operation.DUMP, window, dump)
        for v in dump:
            if DEBUG:
                print >> sys.stderr, "    findTargets: analyzing", v.getClass(), v.getId()
            if v.getClass() == LISTVIEW_CLASS:
                # We may want to touch ListView elements, not just the ListView
                continue
            parent = v.getParent()
            if (parent and parent.getClass() == LISTVIEW_CLASS and self.isClickableCheckableOrFocusable(parent)) \
                    or self.isClickableCheckableOrFocusable(v):
                # If this is a touchable ListView, let's add its children instead
                # or add it if it's touchable, focusable, whatever
                ((x1, y1), (x2, y2)) = v.getCoords()
                if DEBUG:
                    print >> sys.stderr, "appending target", ((x1, y1, x2, y2))
                self.targets.append((x1, y1, x2, y2))
                self.targetViews.append(v)
            else:
                #print v
                pass
    
    def getViewContainingPointAndGenerateTestCondition(self, x, y):
        if DEBUG:
            print >> sys.stderr, 'getViewContainingPointAndGenerateTestCondition(%d, %d)' % (x, y)
        self.finishGeneratingTestCondition()
        vlist = self.vc.findViewsContainingPoint((x, y))
        vlist.reverse()
        for v in vlist:
            text = v.getText()
            if text:
                self.toast(u'Asserting view with text=%s' % text, timeout=2)
                # FIXME: only getText() is invoked by the generated assert(), a parameter
                # should be used to provide different alternatives to printOperation()
                self.printOperation(v, Operation.TEST, text)
                break
                

    def findViewContainingPointInTargets(self, x, y):
        vlist = self.vc.findViewsContainingPoint((x, y))
        vlist.reverse()
        for v in vlist:
            if DEBUG:
                print >> sys.stderr, "checking if", v, "is in", self.targetViews
            if v in self.targetViews:
                if DEBUG_TOUCH:
                    print >> sys.stderr
                    print >> sys.stderr, "I guess you are trying to touch:", v
                    print >> sys.stderr
                return v
        
        return None

    def getViewContainingPointAndTouch(self, x, y):
        if DEBUG:
            print >> sys.stderr, 'getViewContainingPointAndTouch(%d, %d)' % (x, y)
        if self.areEventsDisabled:
            if DEBUG:
                print >> sys.stderr, "Ignoring event"
            self.canvas.update_idletasks()
            return
         
        self.showVignette()
        if DEBUG_POINT:
            print >> sys.stderr, "getViewsContainingPointAndTouch(x=%s, y=%s)" % (x, y)
            print >> sys.stderr, "self.vc=", self.vc
        v = self.findViewContainingPointInTargets(x, y)
        if v is None:
            # FIXME: We can touch by DIP by default if no Views were found
            self.hideVignette()
            msg = "There are no touchable or clickable views here!"
            self.toast(msg)
            return
        clazz = v.getClass()
        if clazz == 'android.widget.EditText':
            title = "EditText"
            kwargs = {}
            if DEBUG:
                print >>sys.stderr, v
            if v.isPassword():
                title = "Password"
                kwargs = {'show': '*'}
            text = tkSimpleDialog.askstring(title, "Enter text to type into this field", **kwargs)
            self.canvas.focus_set()
            if text:
                v.type(text)
                self.printOperation(v, Operation.TYPE, text)
            else:
                self.hideVignette()
                return
        else:
            candidates = [v]
            def findBestCandidate(view):
                isccf = Culebron.isClickableCheckableOrFocusable(view)
                cd = view.getContentDescription()
                text = view.getText()
                if (cd or text) and not isccf:
                    # because isccf==False this view was not added to the list of targets
                    # (i.e. Settings)
                    candidates.insert(0, view)
                return None
            if not (v.getText() or v.getContentDescription()) and v.getChildren():
                self.vc.traverse(root=v, transform=findBestCandidate, stream=None)
            if len(candidates) > 2:
                warnings.warn("We are in trouble, we have more than one candidate to touch", stacklevel=0)
            candidate = candidates[0]
            candidate.touch()
            # we pass root=v as an argument so the corresponding findView*() searches in this
            # subtree instead of the full tree
            self.printOperation(candidate, Operation.TOUCH_VIEW, v if candidate != v else None)

        self.printOperation(None, Operation.SLEEP, Operation.DEFAULT)
        self.vc.sleep(5)
        self.takeScreenshotAndShowItOnWindow()

    def touchPoint(self, x, y):
        '''
        Touches a point in the device screen.
        The generated operation will use the units specified in L{coordinatesUnit} and the
        orientation in L{vc.display['orientation']}.
        '''
        
        if DEBUG:
            print >> sys.stderr, 'touchPoint(%d, %d)' % (x, y)
            print >> sys.stderr, 'touchPoint:', type(x), type(y)
        if self.areEventsDisabled:
            if DEBUG:
                print >> sys.stderr, "Ignoring event"
            self.canvas.update_idletasks()
            return
        if DEBUG:
            print >> sys.stderr, "Is touching point:", self.isTouchingPoint
        if self.isTouchingPoint:
            self.showVignette()
            self.device.touch(x, y)
            if self.coordinatesUnit == Unit.DIP:
                x = round(x / self.vc.display['density'], 2)
                y = round(y / self.vc.display['density'], 2)
            self.printOperation(None, Operation.TOUCH_POINT, x, y, self.coordinatesUnit, self.vc.display['orientation'])
            self.printOperation(None, Operation.SLEEP, Operation.DEFAULT)
            self.vc.sleep(5)
            self.isTouchingPoint = False
            self.takeScreenshotAndShowItOnWindow()
            self.hideVignette()
            self.statusBar.clear()
            return
    
    def longTouchPoint(self, x, y):
        '''
        Long-touches a point in the device screen.
        The generated operation will use the units specified in L{coordinatesUnit} and the
        orientation in L{vc.display['orientation']}.
        '''

        if DEBUG:
            print >> sys.stderr, 'longTouchPoint(%d, %d)' % (x, y)
        if self.areEventsDisabled:
            if DEBUG:
                print >> sys.stderr, "Ignoring event"
            self.canvas.update_idletasks()
            return
        if DEBUG:
            print >> sys.stderr, "Is long touching point:", self.isLongTouchingPoint
        if self.isLongTouchingPoint:
            self.showVignette()
            self.device.longTouch(x, y)
            if self.coordinatesUnit == Unit.DIP:
                x = round(x / self.vc.display['density'], 2)
                y = round(y / self.vc.display['density'], 2)
            self.printOperation(None, Operation.LONG_TOUCH_POINT, x, y, 2000, self.coordinatesUnit, self.vc.display['orientation'])
            self.printOperation(None, Operation.SLEEP, 5)
            self.vc.sleep(5)
            self.isLongTouchingPoint = False
            self.takeScreenshotAndShowItOnWindow()
            self.hideVignette()
            self.statusBar.clear()
            return
    
    def onButton1Pressed(self, event):
        if DEBUG:
            print >> sys.stderr, "onButton1Pressed((", event.x, ", ", event.y, "))"
        (scaledX, scaledY) = (event.x/self.scale, event.y/self.scale)
        if DEBUG:
            print >> sys.stderr, "    onButton1Pressed: scaled: (", scaledX, ", ", scaledY, ")"
            print >> sys.stderr, "    onButton1Pressed: is grabbing:", self.isGrabbingTouch

        if self.isGrabbingTouch:
            self.onTouchListener((scaledX, scaledY))
            self.isGrabbingTouch = False
        elif self.isDragDialogShowed:
            self.toast("No touch events allowed while setting drag parameters", background=Color.GOLD)
            return
        elif self.isTouchingPoint:
            self.touchPoint(scaledX, scaledY)
        elif self.isLongTouchingPoint:
            self.longTouchPoint(scaledX, scaledY)
        elif self.isGeneratingTestCondition:
            self.getViewContainingPointAndGenerateTestCondition(scaledX, scaledY)
        else:
            self.getViewContainingPointAndTouch(scaledX, scaledY)
    
    def onCtrlButton1Pressed(self, event):
        if DEBUG or True:
            print >> sys.stderr, "onCtrlButton1Pressed((", event.x, ", ", event.y, "))"
        (scaledX, scaledY) = (event.x/self.scale, event.y/self.scale)
        l = self.vc.findViewsContainingPoint((scaledX, scaledY))
        if l and len(l) > 0:
            self.saveViewSnapshot(l[-1])
        else:
            msg = "There are no views here!"
            self.toast(msg)
            return
    
    def onButton2Pressed(self, event):
        if DEBUG:
            print >> sys.stderr, "onButton2Pressed((", event.x, ", ", event.y, "))"
        osName = platform.system()
        if osName == 'Darwin':
            self.showPopupMenu(event)

    def onButton3Pressed(self, event):
        if DEBUG:
            print >> sys.stderr, "onButton3Pressed((", event.x, ", ", event.y, "))"
        self.showPopupMenu(event)
            
    def command(self, keycode):
        '''
        Presses a key.
        Generates the actual key press on the device and prints the line in the script.
        '''
        
        self.device.press(keycode)
        self.printOperation(None, Operation.PRESS, keycode)
            
    def onKeyPressed(self, event):
        if DEBUG_KEY:
            print >> sys.stderr, "onKeyPressed(", repr(event), ")"
            print >> sys.stderr, "    event", type(event.char), len(event.char), repr(event.char), event.keysym, event.keycode, event.type
            print >> sys.stderr, "    events disabled:", self.areEventsDisabled
        if self.areEventsDisabled:
            if DEBUG_KEY:
                print >> sys.stderr, "ignoring event"
            self.canvas.update_idletasks()
            return


        char = event.char
        keysym = event.keysym

        if len(char) == 0 and not (keysym in Culebron.KEYSYM_TO_KEYCODE_MAP or keysym in Culebron.KEYSYM_CULEBRON_COMMANDS):
            if DEBUG_KEY:
                print >> sys.stderr, "returning because len(char) == 0"
            return
        
        ###
        ### internal commands: no output to generated script
        ###
        try:
            handler = getattr(self, 'onCtrl%s' % self.UPPERCASE_CHARS[ord(char)-1])
        except:
            handler = None
        if handler:
            return handler(event)
        elif keysym == 'F1':
            self.showHelp()
            return
        elif keysym == 'F5':
            self.refresh()
            return
        elif keysym == 'Alt_L':
            return
        elif keysym == 'Control_L':
            return
        elif keysym == 'Escape':
            # we cannot send Escape to the device, but I think it's fine
            self.cancelOperation()
            return

        ### empty char (modifier) ###
        # here does not process events  like Home where char is ''
        #if char == '':
        #    return

        ###
        ### target actions
        ###
        self.showVignette()

        if keysym in Culebron.KEYSYM_TO_KEYCODE_MAP:
            if DEBUG_KEY:
                print >> sys.stderr, "Pressing", Culebron.KEYSYM_TO_KEYCODE_MAP[keysym]
            self.command(Culebron.KEYSYM_TO_KEYCODE_MAP[keysym])
        elif char == '\r':
            self.command('ENTER')
        elif char == '':
            # do nothing
            pass
        else:
            self.command(char.decode('ascii', errors='replace'))
        self.vc.sleep(1)
        self.takeScreenshotAndShowItOnWindow()

    
    def refresh(self):
            self.showVignette()
            display = copy.copy(self.device.display)
            self.device.initDisplayProperties()
            changed = False
            for prop in display:
                if display[prop] != self.device.display[prop]:
                    changed = True
                    break
            if changed:
                self.window.geometry('%dx%d' % (self.device.display['width']*self.scale, self.device.display['height']*self.scale+int(self.statusBar.winfo_height())))
                self.deleteVignette()
                self.canvas.destroy()
                self.canvas = None
                self.window.update_idletasks()
            self.takeScreenshotAndShowItOnWindow()
    
    def cancelOperation(self):
        '''
        Cancels the ongoing operation if any.
        '''
        if self.isLongTouchingPoint:
            self.toggleLongTouchPoint()
        elif self.isTouchingPoint:
            self.toggleTouchPoint()
        elif self.isGeneratingTestCondition:
            self.toggleGenerateTestCondition()
        
    def onCtrlA(self, event):
        if DEBUG:
            self.toggleMessageArea()


    def showDragDialog(self):
        d = DragDialog(self)
        self.window.wait_window(d)
        self.setDragDialogShowed(False)

    def onCtrlD(self, event):
        self.showDragDialog()

    def onCtrlF(self, event):
        self.saveSnapshot()
        
    def saveSnapshot(self):
        '''
        Saves the current shanpshot to the specified file.
        Current snapshot is the image being displayed on the main window.
        '''
        
        filename = self.snapshotDir + os.sep + '${serialno}-${focusedwindowname}-${timestamp}' + '.' + self.snapshotFormat.lower()
        # We have the snapshot already taken, no need to retake
        d = FileDialog(self, self.device.substituteDeviceTemplate(filename))
        saveAsFilename = d.askSaveAsFilename()
        if saveAsFilename:
            _format = os.path.splitext(saveAsFilename)[1][1:].upper()
            self.printOperation(None, Operation.SNAPSHOT, filename, _format)
            self.unscaledScreenshot.save(saveAsFilename, _format)

    def saveViewSnapshot(self, view):
        '''
        Saves the View snapshot.
        '''
        
        if not view:
            raise ValueError("view must be provided to take snapshot")
        filename = self.snapshotDir + os.sep + '${serialno}-' + view.variableNameFromId() + '-${timestamp}' + '.' + self.snapshotFormat.lower()
        d = FileDialog(self, self.device.substituteDeviceTemplate(filename))
        saveAsFilename = d.askSaveAsFilename()
        if saveAsFilename:
            _format = os.path.splitext(saveAsFilename)[1][1:].upper()
            self.printOperation(view, Operation.VIEW_SNAPSHOT, filename, _format)
            view.writeImageToFile(saveAsFilename, _format)
        
    def toggleTouchPointDip(self):
        '''
        Toggles the touch point operation using L{Unit.DIP}.
        This invokes L{toggleTouchPoint}.
        '''

        self.coordinatesUnit = Unit.DIP
        self.toggleTouchPoint()

    def onCtrlI(self, event):
        self.toggleTouchPointDip()
    

    def toggleLongTouchPoint(self):
        '''
        Toggles the long touch point operation.
        '''
        if not self.isLongTouchingPoint:
            msg = 'Long touching point'
            self.toast(msg, background=Color.GREEN)
            self.statusBar.set(msg)
            self.isLongTouchingPoint = True
            # FIXME: There should be 2 methods DIP & PX
            self.coordinatesUnit = Unit.DIP
        else:
            self.toast(None)
            self.statusBar.clear()
            self.isLongTouchingPoint = False

    def onCtrlL(self, event):
        self.toggleLongTouchPoint()

    def toggleTouchPoint(self):
        '''
        Toggles the touch point operation using the units specified in L{coordinatesUnit}.
        '''
        
        if not self.isTouchingPoint:
            msg = 'Touching point (units=%s)' % self.coordinatesUnit
            self.toast(msg, background=Color.GREEN)
            self.statusBar.set(msg)
            self.isTouchingPoint = True
        else:
            self.toast(None)
            self.statusBar.clear()
            self.isTouchingPoint = False


    def toggleTouchPointPx(self):
        self.coordinatesUnit = Unit.PX
        self.toggleTouchPoint()

    def onCtrlP(self, event):
        self.toggleTouchPointPx()
        
    def onCtrlQ(self, event):
        if DEBUG:
            print >> sys.stderr, "onCtrlQ(%s)" % event
        self.quit()
    
    def quit(self):
        self.window.destroy()
        

    def showSleepDialog(self):
        seconds = tkSimpleDialog.askfloat('Sleep Interval', 'Value in seconds:', initialvalue=1, minvalue=0, parent=self.window)
        if seconds is not None:
            self.printOperation(None, Operation.SLEEP, seconds)
        self.canvas.focus_set()

    def onCtrlS(self, event):
        self.showSleepDialog()
    
    def startGeneratingTestCondition(self):
        self.message('Generating test condition...', background=Color.GREEN)
        self.isGeneratingTestCondition = True

    def finishGeneratingTestCondition(self):
        self.isGeneratingTestCondition = False
        self.hideMessageArea()


    def toggleGenerateTestCondition(self):
        '''
        Toggles generating test condition
        '''
        
        if self.isGeneratingTestCondition:
            self.finishGeneratingTestCondition()
        else:
            self.startGeneratingTestCondition()

    def onCtrlT(self, event):
        if DEBUG:
            print >>sys.stderr, "onCtrlT()"
        # FIXME: This is only valid if we are generating a test case
        self.toggleGenerateTestCondition()
    
    def onCtrlU(self, event):
        if DEBUG:
            print >>sys.stderr, "onCtrlU()"
    
    def onCtrlV(self, event):
        if DEBUG:
            print >>sys.stderr, "onCtrlV()"
        self.printOperation(None, Operation.TRAVERSE)
        
    def toggleTargetZones(self):
        self.toggleTargets()
        self.canvas.update_idletasks()

    def onCtrlZ(self, event):
        if DEBUG:
            print >> sys.stderr, "onCtrlZ()"
        self.toggleTargetZones()


    def showControlPanel(self):
        from com.dtmilano.android.controlpanel import ControlPanel
        self.controlPanel = ControlPanel(self, self.vc, self.printOperation)

    def onCtrlK(self, event):
        self.showControlPanel()
    
    def drag(self, start, end, duration, steps, units=Unit.DIP):
        self.showVignette()
        # the operation on this device is always done in PX
        self.device.drag(start, end, duration, steps)
        if units == Unit.DIP:
            x0 = round(start[0] / self.vc.display['density'], 2)
            y0 = round(start[1] / self.vc.display['density'], 2)
            x1 = round(end[0] / self.vc.display['density'], 2)
            y1 = round(end[1] / self.vc.display['density'], 2)
            start = (x0, y0)
            end = (x1, y1)
        self.printOperation(None, Operation.DRAG, start, end, duration, steps, units, self.vc.display['orientation'])
        self.printOperation(None, Operation.SLEEP, 1)
        self.vc.sleep(1)
        self.takeScreenshotAndShowItOnWindow()
        
    def enableEvents(self):
        self.canvas.update_idletasks()
        self.canvas.bind("<Button-1>", self.onButton1Pressed)
        self.canvas.bind("<Control-Button-1>", self.onCtrlButton1Pressed)
        self.canvas.bind("<Button-2>", self.onButton2Pressed)
        self.canvas.bind("<Button-3>", self.onButton3Pressed)
        self.canvas.bind("<BackSpace>", self.onKeyPressed)
        #self.canvas.bind("<Control-Key-S>", self.onCtrlS)
        self.canvas.bind("<Key>", self.onKeyPressed)
        self.areEventsDisabled = False

    def disableEvents(self):
        if self.canvas is not None:
            self.canvas.update_idletasks()
            self.areEventsDisabled = True
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Control-Button-1>")
            self.canvas.unbind("<Button-2>")
            self.canvas.unbind("<Button-3>")
            self.canvas.unbind("<BackSpace>")
            #self.canvas.unbind("<Control-Key-S>")
            self.canvas.unbind("<Key>")
    
    def toggleTargets(self):
        if DEBUG:
            print >> sys.stderr, "toggletargets: aretargetsmarked=", self.areTargetsMarked
        if not self.areTargetsMarked:
            self.markTargets()
        else:
            self.unmarkTargets()

    def markTargets(self):
        if DEBUG:
            print >> sys.stderr, "marktargets: aretargetsmarked=", self.areTargetsMarked
            print >> sys.stderr, "    marktargets: targets=", self.targets
        colors = ["#ff00ff", "#ffff00", "#00ffff"]

        self.targetIds = []
        c = 0
        for (x1, y1, x2, y2) in self.targets:
            if DEBUG:
                print "adding rectangle:", x1, y1, x2, y2
            self.targetIds.append(self.canvas.create_rectangle(x1*self.scale, y1*self.scale, x2*self.scale, y2*self.scale, fill=colors[c%len(colors)], stipple="gray25"))
            c += 1
        self.areTargetsMarked = True

    def unmarkTargets(self):
        if not self.areTargetsMarked:
            return
        for t in self.targetIds:
            self.canvas.delete(t)
        self.areTargetsMarked = False

    def setDragDialogShowed(self, showed):
        self.isDragDialogShowed = showed
        if showed:
            pass
        else:
            self.isGrabbingTouch = False

    def drawTouchedPoint(self, x, y):
        size = 50
        return self.canvas.create_oval((x-size)*self.scale, (y-size)*self.scale, (x+size)*self.scale, (y+size)*self.scale, fill=Color.MAGENTA)
        
    def drawDragLine(self, x0, y0, x1, y1):
        width = 15
        return self.canvas.create_line(x0*self.scale, y0*self.scale, x1*self.scale, y1*self.scale, width=width, fill=Color.MAGENTA, arrow="last", arrowshape=(50, 50, 30), dash=(50, 25))
    
    def setOnTouchListener(self, listener):
        self.onTouchListener = listener

    def setGrab(self, state):
        if DEBUG:
            print >> sys.stderr, "Culebron.setGrab(%s)" % state
        if state and not self.onTouchListener:
            warnings.warn('Starting to grab but no onTouchListener')
        self.isGrabbingTouch = state
        if state:
            self.toast('Grabbing drag points...', background=Color.GREEN)
        else:
            self.hideMessageArea()


    @staticmethod
    def isClickableCheckableOrFocusable(v):
        if DEBUG_ISCCOF:
            print >> sys.stderr, "isClickableCheckableOrFocusable(", v.__tinyStr__(), ")"
        try:
            return v.isClickable()
        except AttributeError:
            pass
        try:
            return v.isCheckable()
        except AttributeError:
            pass
        try:
            return v.isFocusable()
        except AttributeError:
            pass
        return False

    def mainloop(self):
        self.window.title("%s v%s" % (Culebron.APPLICATION_NAME, __version__))
        self.window.resizable(width=Tkinter.FALSE, height=Tkinter.FALSE)
        self.window.lift()
        self.window.mainloop()


if TKINTER_AVAILABLE:
    class MainMenu(Tkinter.Menu):
        def __init__(self, culebron):
            Tkinter.Menu.__init__(self, culebron.window)
            self.culebron = culebron
            self.fileMenu = Tkinter.Menu(self)
            self.fileMenu.add_command(label="Quit", underline=0, accelerator='Command-Q', command=self.culebron.quit)
            self.add_cascade(label="File", underline=0, menu=self.fileMenu)
            self.viewMenu = Tkinter.Menu(self)
            self.showTree = Tkinter.BooleanVar()
            self.viewMenu.add_checkbutton(label="Tree", underline=0, accelerator='Command-T', onvalue=True, offvalue=False, variable=self.showTree, state=DISABLED)
            self.showViewDetails = Tkinter.BooleanVar()
            self.viewMenu.add_checkbutton(label="View details", underline=0, accelerator='Command-V', onvalue=True, offvalue=False, variable=self.showViewDetails, state=DISABLED)
            self.add_cascade(label="View", underline=0, menu=self.viewMenu)
            self.helpMenu = Tkinter.Menu(self)
            self.helpMenu.add_command(label="Keyboard shortcuts", underline=0, accelerator='Command-K', command=self.culebron.showHelp)
            self.add_cascade(label="Help", underline=0, menu=self.helpMenu)
            
        def callback(self):
            pass
    
    class StatusBar(Tkinter.Frame):

        def __init__(self, parent):
            Tkinter.Frame.__init__(self, parent)
            self.label = Tkinter.Label(self, bd=1, relief=Tkinter.SUNKEN, anchor=Tkinter.W)
            self.label.pack(fill=Tkinter.X)
    
        def set(self, fmt, *args):
            self.label.config(text=fmt % args)
            self.label.update_idletasks()
    
        def clear(self):
            self.label.config(text="")
            self.label.update_idletasks()

    
    class LabeledEntry():
        def __init__(self, parent, text, validate, validatecmd):
            self.f = Tkinter.Frame(parent)
            Tkinter.Label(self.f, text=text, anchor="w", padx=8).pack(fill="x")
            self.entry = Tkinter.Entry(self.f, validate=validate, validatecommand=validatecmd)
            self.entry.pack(padx=5)
    
        def pack(self, **kwargs):
            self.f.pack(kwargs)
    
        def get(self):
            return self.entry.get()
    
        def set(self, text):
            self.entry.delete(0, Tkinter.END)
            self.entry.insert(0, text)
            
    class LabeledEntryWithButton(LabeledEntry):
        def __init__(self, parent, text, buttonText, command, validate, validatecmd):
            LabeledEntry.__init__(self, parent, text, validate, validatecmd)
            self.button = Tkinter.Button(self.f, text=buttonText, command=command)
            self.button.pack(side="right")
    
    class DragDialog(Tkinter.Toplevel):
        
        DEFAULT_DURATION = 1000
        DEFAULT_STEPS = 20
        
        spX = None
        spY = None
        epX = None
        epY = None
        spId = None
        epId = None
        
        def __init__(self, culebron):
            self.culebron = culebron
            self.parent = culebron.window
            Tkinter.Toplevel.__init__(self, self.parent)
            self.transient(self.parent)
            self.culebron.setDragDialogShowed(True)
            self.title("Drag: selecting parameters")
    
            # valid percent substitutions (from the Tk entry man page)
            # %d = Type of action (1=insert, 0=delete, -1 for others)
            # %i = index of char string to be inserted/deleted, or -1
            # %P = value of the entry if the edit is allowed
            # %s = value of entry prior to editing
            # %S = the text string being inserted or deleted, if any
            # %v = the type of validation that is currently set
            # %V = the type of validation that triggered the callback
            #      (key, focusin, focusout, forced)
            # %W = the tk name of the widget
            self.validate = (self.parent.register(self.onValidate), '%P')
            self.sp = LabeledEntryWithButton(self, "Start point", "Grab", command=self.onGrabSp, validate="focusout", validatecmd=self.validate)
            self.sp.pack(pady=5)
    
            self.ep = LabeledEntryWithButton(self, "End point", "Grab", command=self.onGrabEp, validate="focusout", validatecmd=self.validate)
            self.ep.pack(pady=5)
    
            self.units = Tkinter.StringVar()
            self.units.set(Unit.DIP)
            for u in dir(Unit):
                if u.startswith('_'):
                    continue
                Tkinter.Radiobutton(self, text=u, variable=self.units, value=u).pack(padx=40, anchor=Tkinter.W)
            
            self.d = LabeledEntry(self, "Duration", validate="focusout", validatecmd=self.validate)
            self.d.set(DragDialog.DEFAULT_DURATION)
            self.d.pack(pady=5)
    
            self.s = LabeledEntry(self, "Steps", validate="focusout", validatecmd=self.validate)
            self.s.set(DragDialog.DEFAULT_STEPS)
            self.s.pack(pady=5)
    
            self.buttonBox()
    
        def buttonBox(self):
            # add standard button box. override if you don't want the
            # standard buttons
    
            box = Tkinter.Frame(self)
    
            self.ok = Tkinter.Button(box, text="OK", width=10, command=self.onOk, default=Tkinter.ACTIVE, state=Tkinter.DISABLED)
            self.ok.pack(side=Tkinter.LEFT, padx=5, pady=5)
            w = Tkinter.Button(box, text="Cancel", width=10, command=self.onCancel)
            w.pack(side=Tkinter.LEFT, padx=5, pady=5)
    
            self.bind("<Return>", self.onOk)
            self.bind("<Escape>", self.onCancel)
    
            box.pack()
            
        def onValidate(self, value):
            if self.sp.get() and self.ep.get() and self.d.get() and self.s.get():
                self.ok.configure(state=Tkinter.NORMAL)
            else:
                self.ok.configure(state=Tkinter.DISABLED)
            
        def onOk(self, event=None):
            if DEBUG:
                print >> sys.stderr, "onOK()"
                print >> sys.stderr, "values are:",
                print >> sys.stderr, self.sp.get(),
                print >> sys.stderr, self.ep.get(),
                print >> sys.stderr, self.d.get(),
                print >> sys.stderr, self.s.get(),
                print >> sys.stderr, self.units.get()
    
            sp = make_tuple(self.sp.get())
            ep = make_tuple(self.ep.get())
            d = int(self.d.get())
            s = int(self.s.get())
            self.cleanUp()
            # put focus back to the parent window's canvas
            self.culebron.canvas.focus_set()
            self.destroy()
            self.culebron.drag(sp, ep, d, s, self.units.get())
    
        def onCancel(self, event=None):
            self.culebron.setGrab(False)
            self.cleanUp()
            # put focus back to the parent window's canvas
            self.culebron.canvas.focus_set()
            self.destroy()
        
        def onGrabSp(self):
            '''
            Grab starting point
            '''
            
            self.sp.entry.focus_get()
            self.onGrab(self.sp)
    
        def onGrabEp(self):
            '''
            Grab ending point
            '''
    
            self.ep.entry.focus_get()
            self.onGrab(self.ep)
    
        def onGrab(self, entry):
            '''
            Generic grab method.
            
            @param entry: the entry being grabbed
            @type entry: Tkinter.Entry
            '''
            
            self.culebron.setOnTouchListener(self.onTouchListener)
            self.__grabbing = entry
            self.culebron.setGrab(True)
    
        def onTouchListener(self, point):
            '''
            Listens for touch events and draws the corresponding shapes on the Culebron canvas.
            If the starting point is being grabbed it draws the touching point via
            C{Culebron.drawTouchedPoint()} and if the end point is being grabbed it draws
            using C{Culebron.drawDragLine()}.
            
            @param point: the point touched
            @type point: tuple
            '''
            
            x = point[0]
            y = point[1]
            value = "(%d,%d)" % (x, y)
            self.__grabbing.set(value)
            self.onValidate(value)
            self.culebron.setGrab(False)
            if self.__grabbing == self.sp:
                self.__cleanUpSpId()
                self.__cleanUpEpId()
                self.spX = x
                self.spY = y
            elif self.__grabbing == self.ep:
                self.__cleanUpEpId()
                self.epX = x
                self.epY = y
            if self.spX and self.spY and not self.spId:
                self.spId = self.culebron.drawTouchedPoint(self.spX, self.spY)
            if self.spX and self.spY and self.epX and self.epY and not self.epId:
                self.epId = self.culebron.drawDragLine(self.spX, self.spY, self.epX, self.epY)
            self.__grabbing = None
            self.culebron.setOnTouchListener(None)
    
        def __cleanUpSpId(self):
            if self.spId:
                self.culebron.canvas.delete(self.spId)
                self.spId = None
    
        def __cleanUpEpId(self):
            if self.epId:
                self.culebron.canvas.delete(self.epId)
                self.epId = None
    
        def cleanUp(self):
            self.__cleanUpSpId()
            self.__cleanUpEpId()
    

    class ContextMenu(Tkinter.Menu):
        '''
        The context menu (popup).
        '''
        
        PADDING = '  '
        ''' Padding used to separate menu entries from border '''

        class Separator():
            SEPARATOR = 'SEPARATOR'

            
            def __init__(self):
                self.description = self.SEPARATOR
        
        class Command():
            def __init__(self, description, underline, shortcut, event, command):
                self.description = description
                self.underline = underline
                self.shortcut = shortcut
                self.event = event
                self.command = command 

        def __init__(self, culebron, view):
            # Tkninter.Menu is not extending object, so we can't do this:
            #super(ContextMenu, self).__init__(culebron.window, tearoff=False)
            Tkinter.Menu.__init__(self, culebron.window, tearoff=False)
            self.view = view
            items = []

            if self.view:
                _saveViewSnapshotForSelectedView = lambda: culebron.saveViewSnapshot(self.view)
                items.append(ContextMenu.Command('Take view snapshot and save to file',  5, 'Ctrl+W', '<Control-W>', _saveViewSnapshotForSelectedView))
                items.append(ContextMenu.Separator())

            items.append(ContextMenu.Command('Drag dialog',                  0,      'Ctrl+D',   '<Control-D>',  culebron.showDragDialog))
            items.append(ContextMenu.Command('Take snapshot and save to file',           26,  'Ctrl+F',   '<Control-F>',  culebron.saveSnapshot))
            items.append(ContextMenu.Command('Control Panel',                0,      'Ctrl+K',   '<Control-K>',  culebron.showControlPanel))
            items.append(ContextMenu.Command('Long touch point using PX',    0,      'Ctrl+L',   '<Control-L>',  culebron.toggleLongTouchPoint))
            items.append(ContextMenu.Command('Touch using DIP',             13,      'Ctrl+I',   '<Control-I>',  culebron.toggleTouchPointDip))
            items.append(ContextMenu.Command('Touch using PX',              12,      'Ctrl+P',   '<Control-P>',   culebron.toggleTouchPointPx))
            items.append(ContextMenu.Command('Generates a Sleep() on output script',     12,  'Ctrl+S', '<Control-S>', culebron.showSleepDialog))
            items.append(ContextMenu.Command('Toggle generating Test Condition',         18,  'Ctrl+T', '<Control-T>', culebron.toggleGenerateTestCondition))
            items.append(ContextMenu.Command('Touch Zones',                  6,      'Ctrl+Z',   '<Control-Z>',  culebron.toggleTargetZones))
            items.append(ContextMenu.Command('Refresh',                      0,      'F5',   '<F5>',  culebron.refresh))
            items.append(ContextMenu.Separator())
            items.append(ContextMenu.Command('Quit',                         0,      'Ctrl+Q',   '<Control-Q>',  culebron.quit))

            for item in items:
                self.addItem(item)

        def addItem(self, item):
            if isinstance(item, ContextMenu.Separator):
                self.addSeparator()
            elif isinstance(item, ContextMenu.Command):
                self.addCommand(item)
            else:
                raise RuntimeError("Unsupported item=" + str(item))

        def addSeparator(self):
            self.add_separator()
            
        def addCommand(self, item):
            self.add_command(label=self.PADDING + item.description, underline=item.underline + len(self.PADDING), command=item.command, accelerator=item.shortcut)
            if item.event:
                self.bind_all(item.event, item.command)
            
        def showPopupMenu(self, event):
            try:
                self.tk_popup(event.x_root, event.y_root)
            finally:
                # make sure to release the grab (Tk 8.0a1 only)
                #self.grab_release()
                pass
                


    class HelpDialog(Tkinter.Toplevel):
    
        def __init__(self, culebron):
            self.culebron = culebron
            self.parent = culebron.window
            Tkinter.Toplevel.__init__(self, self.parent)
            #self.transient(self.parent)
            self.title("%s: help" % Culebron.APPLICATION_NAME)
    
            self.text = ScrolledText.ScrolledText(self, width=60, height=40)
            self.text.insert(Tkinter.INSERT, '''
    Special keys
    ------------
    
    F1: Help
    F5: Refresh
    
    Mouse Buttons
    -------------
    <1>: Touch the underlying View
    
    Commands
    --------
    Ctrl-A: Toggle message area
    Ctrl-D: Drag dialog
    Ctrl-F: Take snapshot and save to file
    Ctrl-K: Control Panel
    Ctrl-L: Long touch point using PX
    Ctrl-I: Touch using DIP
    Ctrl-P: Touch using PX
    Ctrl-Q: Quit
    Ctrl-S: Generates a sleep() on output script
    Ctrl-T: Toggle generating test condition
    Ctrl-V: Verifies the content of the screen dump
    Ctrl-Z: Touch zones
    ''')
            self.text.pack()
    
            self.buttonBox()
    
        def buttonBox(self):
            # add standard button box. override if you don't want the
            # standard buttons
    
            box = Tkinter.Frame(self)
    
            w = Tkinter.Button(box, text="Dismiss", width=10, command=self.onDismiss, default=Tkinter.ACTIVE)
            w.pack(side=Tkinter.LEFT, padx=5, pady=5)
    
            self.bind("<Return>", self.onDismiss)
            self.bind("<Escape>", self.onDismiss)
    
            box.pack()
    
        def onDismiss(self, event=None):
            # put focus back to the parent window's canvas
            self.culebron.canvas.focus_set()
            self.destroy()

    class FileDialog():
        def __init__(self, culebron, filename):
            self.parent = culebron.window
            self.filename = filename
            self.basename = os.path.basename(self.filename)
            self.dirname = os.path.dirname(self.filename)
            self.ext = os.path.splitext(self.filename)[1]
            self.fileTypes = [('images', self.ext)]
            
        def askSaveAsFilename(self):
            return tkFileDialog.asksaveasfilename(parent=self.parent, filetypes=self.fileTypes, defaultextension=self.ext, initialdir=self.dirname, initialfile=self.basename)
