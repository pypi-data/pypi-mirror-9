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

from avc import *			# AVC

LOW_SPEED = 500				#--
HIGH_SPEED = 100			#- low and high speed period (ms)


class Example(wx.PySimpleApp,AVC):
  """
  A counter displayed in a static text widget whose count speed can be
  accelerated by checking a check box.
  """

  def __init__(self):

    ## create GUI

    # init wx application base class
    wx.PySimpleApp.__init__(self)

    # create widgets: a top level window, a label and a spin control.
    self.root = wx.Frame(None,title='AVC wx counter example',size=(320,60))
    label = wx.StaticText(self.root,label='%s',name='counter__label',
      size=(100,20))
    checkbox = wx.CheckBox(self.root,label='high speed',
      name='high_speed__checkbox',size=(100,25))

    # layout the label and the check box horizontally into the window
    hsizer = wx.BoxSizer(wx.HORIZONTAL)
    hsizer.Add((20,10),proportion=1)
    hsizer.Add(label,proportion=0.5,flag=wx.CENTER)
    hsizer.Add(checkbox,proportion=0.5,flag=wx.CENTER)
    hsizer.Add((20,10),proportion=1)
    self.root.SetSizer(hsizer)
    self.root.Show()

    ## the counter variable and its speed status
    self.counter = 0
    self.high_speed = False

    # start counter incrementer at low speed
    self.timer = wx.Timer(self.root,wx.NewId())
    self.root.Bind(wx.EVT_TIMER,self.incrementer,self.timer)
    self.timer.Start(LOW_SPEED,oneShot=True)


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
    self.timer.Start(period,oneShot=True)

  def high_speed_changed(self,value):
    "Notify change of counting speed to terminal"
    if value:
      print 'counting speed changed to high'
    else:
      print 'counting speed changed to low'


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.MainLoop()		 	# run wx event loop until quit

#### END
