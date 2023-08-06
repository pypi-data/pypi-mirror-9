#!/usr/bin/python
# -*- coding: utf-8 -*-
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : Calendar widget connected to label widget (wx)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	31-Jan-2013
# .copyright  : (c) 2013 Fabrizio Pollastri.
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


import wx				    # wx tool kit bindings
from wx import xrc			# xml resource support

from avc import *			# AVC for wx

WXGLADE_XML = 'wx_calendar.xrc'		# GUI wxGlade descriptor


class Example(wx.PySimpleApp,AVC):
  """
  Calendar widget connected to label widget (GTK)
  """

  def __init__(self):

    # init wx application base class
    wx.PySimpleApp.__init__(self)

    # create GUI
    xml_resource = xrc.XmlResource(WXGLADE_XML)
    self.root = xml_resource.LoadFrame(None,'frame_1')
    self.root.Show()
     
    # all types of connected variables
    self.calendar_value = (2000,1,1)


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.MainLoop()		 	# run wx event loop until quit

#### END
