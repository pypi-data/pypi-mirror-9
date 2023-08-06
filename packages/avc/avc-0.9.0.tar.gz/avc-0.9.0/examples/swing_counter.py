#!/usr/bin/env jython
# .+
# .context    : Application View Controller
# .title      : A counter with count speed control (Swing),
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

LOW_SPEED = 500				#--
HIGH_SPEED = 100			#- low and high speed period (ms)


class ExampleGUI:
  "Counter GUI creation"

  def __init__(self):

    # create GUI
    root = swing.JFrame('AVC Swing counter example',size=(350,60),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    root.layout = awt.FlowLayout()
    root.add(swing.JLabel('counter',name='counter__label',))
    root.add(swing.JCheckBox('high speed',name='high_speed__checkbox'))
    root.show()

    # create a timer for incrementer
    self.timer = swing.Timer(LOW_SPEED,None)
  

class ExampleMain(AVC):
  """
  A counter displayed in a Label widget whose count speed can be
  accelerated by checking a check box.
  """

  def __init__(self,gui):

    # save GUI
    self.gui = gui

    # the counter variable and its speed status
    self.counter = 0
    self.high_speed = False

    # start variable incrementer
    self.gui.timer.actionPerformed = self.incrementer
    self.gui.timer.start()


  def incrementer(self,*args):
    """
    Counter incrementer: increment period = LOW_SPEED, if high speed is False,
    increment period = HIGH_SPEED otherwise.
    """
    self.counter += 1
    if self.high_speed:
      period = HIGH_SPEED
    else:
      period = LOW_SPEED
    self.gui.timer.setDelay(period)

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

#### END
