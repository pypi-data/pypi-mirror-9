#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A random generation of count down windows (wx)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	13-May-2008
# .copyright  : (c) 2008 Fabrizio Pollastri.
# .license    : GNU General Public License (see below)
#
# This file is part of "AVC, Application View Controller".
#
# AVC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# AVC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# .-


import wx				# wx tool kit bindings
from wx import xrc			# xml resource support

from avc import *			# AVC

from random import randint		# random integer generator

WXGLADE_MAIN = 'wx_countdown_main.xrc'	# main window glade descriptor
WXGLADE_CD = 'wx_countdown.xrc'		# count down window glade descriptor
FIRST_COUNT_DELAY = 1000		# let avc_init be called
COUNTDOWN_PERIOD = 500			# count down at 2 unit per second
MAX_CREATION_PERIOD = 4000		# create a new count down at 1/2 this


class Countdown(AVC):
  """
  A countdown counter displayed in a Label widget. Count starts at given
  value. When count reaches zero the counter and its GUI are destroyed.
  """

  def __init__(self,count_start=10):

    # create GUI
    xml_resource = xrc.XmlResource(WXGLADE_CD)
    self.root = xml_resource.LoadFrame(None,'frame_1')
    self.root.Show()

    # init the counter variable 
    self.counter = count_start

    # connect counter variable with label widget
    self.avc_connect(self.root)

    # start count down
    self.timer = wx.Timer(self.root,wx.NewId())
    self.root.Bind(wx.EVT_TIMER,self.decrementer,self.timer)
    self.timer.Start(COUNTDOWN_PERIOD)


  def decrementer(self,event):
    "Counter decrementer. Return False to destroy previous timer."
    self.counter -= 1
    if not self.counter:
      # counter reached zero: destroy this countdown and its GUI
      self.root.Close()


class Example(wx.PySimpleApp,AVC):
  """
  Continuously create at random intervals windows with a countdown from 10 to 0.
  When a countdown reaches zero, its window is destroyed. Also create a main
  window with a "close all" button.
  """

  def __init__(self):

    # init wx application base class
    wx.PySimpleApp.__init__(self)

    # create GUI
    xml_resource = xrc.XmlResource(WXGLADE_MAIN)
    self.root = xml_resource.LoadFrame(None,'frame_1')
    self.root.Show()

    # terminate application at main window close
    self.root.Bind(wx.EVT_CLOSE,self.on_destroy)

    # close all button connected variable
    self.close_all = False

    # create count down creation timer
    self.timer = wx.Timer(self.root,wx.NewId())
    self.root.Bind(wx.EVT_TIMER,self.new_countdown,self.timer)

    # create the first countdown after avc_init call
    self.timer.Start(FIRST_COUNT_DELAY,oneShot=True)


  def new_countdown(self,event,count_start=10):
    "Create a new countdown"

    # create a new countdown
    Countdown(count_start)

    # autocall after a random delay
    self.timer.Start(randint(1,MAX_CREATION_PERIOD),oneShot=True)


  def on_destroy(self,window):
    "Terminate program at window destroy"
    self.Exit()

  def close_all_changed(self,value):
    "Terminate program at 'close all' button pressing"
    self.Exit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.MainLoop()		 	# run wx event loop until quit

#### END
