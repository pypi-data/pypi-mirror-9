#!/usr/bin/env jython
# .+
# .context    : Application View Controller
# .title      : A text field replicated into a label (Swing),
#		GUI programmatically generated
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	22-Oct-2009
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


class Example(AVC):
  """
  A text field whose value is replicated into a label
  """

  def __init__(self):

    # create GUI
    root = swing.JFrame('AVC Swing text field example',size=(320,110),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    root.layout = awt.FlowLayout()
    root.add(swing.JLabel('integer entry'))
    root.add(swing.JLabel('integer',name='integer__label',))
    root.add(swing.JTextField(columns=10,name='integer__textfield'))
    root.add(swing.JLabel(' float entry '))
    root.add(swing.JLabel('float',name='float__label',))
    root.add(swing.JTextField(columns=10,name='float__textfield'))
    root.add(swing.JLabel('string entry '))
    root.add(swing.JLabel('string',name='string__label',))
    root.add(swing.JTextField(columns=10,name='string__textfield'))
    root.show()

    # the variables holding the text field values
    self.integer = 0
    self.float = 0.0
    self.string = 'abc'


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables

#### END
