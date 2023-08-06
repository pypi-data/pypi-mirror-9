#!/usr/bin/env jython
# .+
# .context    : Application View Controller
# .title      : A color chooser replicated into a label (Swing),
#		GUI programmatically generated
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	7-Feb-2013
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

from javax import swing			# swing toolkit bindings
from java import awt			# awt toolkit bindings

from avc import *			# AVC for Swing


class Example(AVC):
  """
  A color chooser replicated into a label (Swing),
  """

  def __init__(self):

    # create GUI
    root = swing.JFrame('AVC Swing color chooser example',size=(900,380),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    root.layout = awt.FlowLayout()
    root.add(swing.JLabel('%s',name='color_value__label'))
    root.add(swing.JColorChooser(name='color_value__colorchooser'))
    root.show()

    # the variable holding the color chooser value
    self.color_value = (0.25,0.5,1.,1.)


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables

#### END
