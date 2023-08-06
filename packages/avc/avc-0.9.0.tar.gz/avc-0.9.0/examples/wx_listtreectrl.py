#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : tree view widget display capabilities (wx)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	25-Dec-2008
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

import copy				# object cloning support

WXGLADE_XML = 'wx_listtreectrl.xrc'	# GUI wxGlade descriptor

UPDATE_PERIOD = 2000			# ms


class Example(wx.PySimpleApp,AVC):
  """
  Showcase of display capabilities for the list control and tree control widgets
  """

  def __init__(self):

    # init wx application base class
    wx.PySimpleApp.__init__(self)

    # create GUI
    xml_resource = xrc.XmlResource(WXGLADE_XML)
    self.root = xml_resource.LoadFrame(None,'frame_1')
    self.root.Show()

    # connected variables
    self.list = {'head':['col1 int','col2 str'], \
      'body':[[1,'one'],[2,'two'],[3,'three']]}
    self.list_work = copy.deepcopy(self.list)
    self.tree = {'body':{ \
      # root rows
      '1':'one', \
      '2':'two', \
      # children of root row '1'
      '1.1':'one one', \
      '1.2':'one two', \
      # children of root row '2'
      '2.1':'two one', \
      '2.2':'two two'}}

    # start a wx timer calling back 'function' every 'period' seconds."
    self.timer1 = wx.Timer(self.root,wx.NewId())
    self.root.Bind(wx.EVT_TIMER,self.update_wrap,self.timer1)
    self.timer1.Start(UPDATE_PERIOD,oneShot=False)


  def update_wrap(self,event):
    "Discard event argument and call the real update iterator"
    self.update().next()

  def update(self):
    """
    Tabular data rows data are rolled down.
    """
    rows_num = len(self.list['body'])
    while True:
      # save last row of data
      last_row = self.list_work['body'][-1]
      # shift down one position each data row
      for i in range(1,rows_num): 
        self.list_work['body'][-i] = \
          self.list_work['body'][-1-i]
      # copy last row into first position
      self.list_work['body'][0] = last_row
      # copy working copy into connected variable
      self.list = self.list_work
      yield True


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.MainLoop()			# run wx event loop until quit

#### END
