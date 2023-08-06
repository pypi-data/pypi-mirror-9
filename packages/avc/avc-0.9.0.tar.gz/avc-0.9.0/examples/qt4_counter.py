#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A counter with count speed control (Qt4)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	7-Dec-2006
# .copyright  : (c) 2006 Fabrizio Pollastri.
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


from PyQt4.QtCore import *		# Qt core
from PyQt4.QtGui import *		# Qt GUI interface
from PyQt4.uic import *			# ui files realizer
import sys				# system support

from avc import *			# AVC

UI_FILE = 'qt4_counter.ui'		# qt ui descriptor
LOW_SPEED = 0.5				#--
HIGH_SPEED = 0.1			#- low and high speed count period (sec)


class ExampleGUI(QApplication):
  "Counter GUI creation"

  def __init__(self):

    # create GUI
    QApplication.__init__(self,sys.argv)
    self.root = loadUi(UI_FILE)
    self.root.show()
    
  def timer_start(self,period,function):
    "Start a Qt timer calling back 'function' every 'period' seconds."
    self.timer1 = QTimer()
    QObject.connect(self.timer1,SIGNAL("timeout()"),function)
    self.timer1.start(int(period * 1000.0))

  def timer_set_period(self,period):
    "Set a new period to timer"
    self.timer1.stop()
    self.timer1.start(int(period * 1000.0))


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

    # start incrementer timer
    self.gui.timer_start(LOW_SPEED,self.incrementer)


  def incrementer(self):
    """
    Counter incrementer: increment period = LOW_SPEED, if high speed
    is False, increment period = HIGH_SPEED otherwise.
    """
    self.counter += 1
    if self.high_speed:
      period = HIGH_SPEED
    else:
      period = LOW_SPEED
    self.gui.timer_set_period(period)

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
example_gui.exec_()			# run Qt event loop until quit

#### END
