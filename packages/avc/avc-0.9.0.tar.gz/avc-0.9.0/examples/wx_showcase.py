#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A table of all supported widget/control type conbinations (wx)
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

from avc import *			# AVC for wx

WXGLADE_XML = 'wx_showcase.xrc'		# GUI wxGlade descriptor
INCREMENTER_PERIOD = 333		# ms


class Example(wx.PySimpleApp,AVC):
  """
  A table of all supported widget/control type combinations
  """

  def __init__(self):

    # init wx application base class
    wx.PySimpleApp.__init__(self)

    # create GUI
    xml_resource = xrc.XmlResource(WXGLADE_XML)
    self.root = xml_resource.LoadFrame(None,'frame_1')
    self.root.Show()

    # the control variables
    self.boolean1 = False
    self.boolean2 = False
    self.index = 0
    self.integer = 0
    self.float = 0.0
    self.progressbar = -1.0
    self.string = ''
    self.textview = ''
    self.status = ''

    # start counter incrementer at low speed
    self.timer = wx.Timer(self.root,wx.NewId())
    self.root.Bind(wx.EVT_TIMER,self.incrementer_wrap,self.timer)
    self.timer.Start(int(INCREMENTER_PERIOD),oneShot=False)
    self.increment = self.incrementer()


  def incrementer_wrap(self,event):
    "Discard event argument and call the real incrementer iterator"
    self.increment.next()

  def incrementer(self,*args):
    """
    Booleans are toggled, radio button index is rotated from first to last,
    integer is incremented by 1, float by 0.5, progress bar is alternatively
    shuttled or incremented from 0 to 100%, string is appended a char
    until maxlen when string is cleared, text view/edit is appended a line
    of text until maxlen when it is cleared. Status bar message is toggled.
    Return True to keep timer alive.
    """
    while True:

      self.boolean1 = not self.boolean1
      yield True

      self.boolean2 = not self.boolean2
      yield True

      if self.index >= 2:
        self.index = 0
      else:
        self.index += 1
      yield True

      self.integer += 1
      yield True

      self.float += 0.5
      yield True

      if self.progressbar >= 0.9999:
        self.progressbar = -1.0
      else:
        self.progressbar += 0.1
      yield True

      if len(self.string) >= 10:
        self.string = ''
      else:
        self.string += 'A'
      yield True

      if len(self.textview) >= 200:
        self.textview = ''
      else:
        self.textview += 'line of text, line of text, line of text\n'
      yield True

      if not self.status:
        self.status = 'status message'
      else:
        self.status = ''
      yield True


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.MainLoop()		 	# run wx event loop until quit

#### END
