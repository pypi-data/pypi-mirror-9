#!/usr/bin/env jython
# .+
# .context    : Application View Controller
# .title      : table widget display capabilities (Swing),
#		GUI programmatically generated
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	29-Oct-2009
# .copyright  : (c) 2009 Fabrizio Pollastri.
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

from javax import swing			# swing toolkit bindings
from java import awt			# awt toolkit bindings

from avc import *			# AVC for Swing

import copy				# object cloning support

UPDATE_PERIOD = 2000			# ms


class Example(AVC):
  """
  Showcase of display capabilities for the table widget
  """

  def __init__(self):

    # create GUI
    root = swing.JFrame('AVC Swing table example',size=(500,120),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    root.layout = awt.FlowLayout()
    root.add(swing.JLabel(name='list__label',))
    table = swing.JTable(name='list__table')
    scrollpane = swing.JScrollPane()
    scrollpane.setPreferredSize(awt.Dimension(200,65))
    scrollpane.getViewport().setView(table)
    root.add(scrollpane)
    root.show()

    # connected variables
    self.list = {'head':['col1 int','col2 str'], \
      'body':[[1,'one'],[2,'two'],[3,'three']]}
    self.list_work = copy.deepcopy(self.list)

    # start variables update
    update = self.update()
    self.timer = swing.Timer(UPDATE_PERIOD,None)
    self.timer.actionPerformed = lambda event: update.next()
    self.timer.start()


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
      yield


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables

#### END
