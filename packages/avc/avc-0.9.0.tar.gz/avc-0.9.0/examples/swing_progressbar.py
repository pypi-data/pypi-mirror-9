#!/usr/bin/env jython
# .+
# .context    : Application View Controller
# .title      : A progressbar replicated into a label (Swing),
#		GUI programmatically generated
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
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

INCREMENTER_PERIOD = 333		# ms


class Example(AVC):
  """
  A progress bar whose value is replicated into a label
  """

  def __init__(self):

    # create GUI
    root = swing.JFrame('AVC Swing progress bar example',size=(350,60),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    root.layout = awt.FlowLayout()
    root.add(swing.JLabel('progressbar',name='progressbar__label',))
    root.add(swing.JProgressBar(name='progressbar__progressbar'))
    root.show()

    # the variable holding the progress bar value
    self.progressbar = -1.0

    # start variables incrementer
    increment = self.incrementer()
    self.timer = swing.Timer(INCREMENTER_PERIOD,None)
    self.timer.actionPerformed = lambda event: increment.next()
    self.timer.start()


  def incrementer(self):
    """
    Progress bar is alternatively shuttled or incremented from 0 to 100%
    """
    while True:

      if self.progressbar >= 0.9999:
        self.progressbar = -1.0
      else:
        self.progressbar = round(self.progressbar + 0.1,1)
      yield


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables

#### END
