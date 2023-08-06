#!/usr/bin/env jython
# .+
# .context    : Application View Controller
# .title      : tree widget display capabilities (Swing),
#		GUI programmatically generated
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	6-Nov-2009
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


class Example(AVC):
  """
  Showcase of display capabilities for the tree view widget
  """

  def __init__(self):

    # create GUI
    root = swing.JFrame('AVC Swing tree example',size=(800,220),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    root.layout = awt.FlowLayout()
    root.add(swing.JLabel(name='tree__label',))
    self.jtree = swing.JTree(name='tree__table')
    self.jtree.setEditable(True)
    scrollpane = swing.JScrollPane()
    scrollpane.setPreferredSize(awt.Dimension(200,160))
    scrollpane.getViewport().setView(self.jtree)
    root.add(scrollpane)
    root.show()

    # connected variables
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


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables

# expand first level rows in the tree
for i in range(example.jtree.getRowCount()):
  example.jtree.expandRow(i)

#### END
