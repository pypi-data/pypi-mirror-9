#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A counter with count speed control (wx)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	24-Nov-2007
# .copyright  : (c) 2007 Fabrizio Pollastri.
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

WXGLADE_XML = 'wx_counter.xrc'		# GUI wxGlade descriptor
LOW_SPEED = 0.5				#--
HIGH_SPEED = 0.1			#- low and high speed period (ms)


class ExampleGUI(wx.PySimpleApp):
  "Counter GUI creation"

  def __init__(self):

    # init wx application base class
    wx.PySimpleApp.__init__(self)

    # create GUI
    xml_resource = xrc.XmlResource(WXGLADE_XML)
    self.root = xml_resource.LoadFrame(None,'frame_1')
    self.root.Show()

    # timer
    self.timer1 = None


  def timer(self,period,function):
    "Start a wx timer calling back 'function' every 'period' seconds."
    if not self.timer1:
      self.timer1 = wx.Timer(self.root,wx.NewId())
      self.root.Bind(wx.EVT_TIMER,function,self.timer1)
    self.timer1.Start(period * 1000,oneShot=True)


class ExampleMain(AVC):
  """
  A counter displayed in a Label widget whose count speed can be
  accelerated by checking a check button.
  """

  def __init__(self,gui):

    # save gui
    self.gui = gui

    # the counter variable and its speed status
    self.counter = 0
    self.high_speed = False

    # start incrementer timer
    self.gui.timer(LOW_SPEED,self.incrementer)


  def incrementer(self,event):
    """
    Counter incrementer: increment period = LOW_SPEED, if high speed is False,
    increment period = HIGH_SPEED otherwise. Return False to destroy previous
    timer.
    """
    self.counter += 1
    if self.high_speed:
      period = HIGH_SPEED
    else:
      period = LOW_SPEED
    self.gui.timer(period,self.incrementer)

  def high_speed_changed(self,value):
    "Notify change of counting speed to terminal"
    if value:
      print 'counting speed changed to high'
    else:
      print 'counting speed changed to low'


#### MAIN

example_gui = ExampleGUI()		# create the application GUI
example = ExampleMain(example_gui)	# instantiate the application
example.avc_init()			# connect widgets with variables
example_gui.MainLoop()			# run wx event loop until quit

#### END
