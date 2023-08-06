#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : Random generation of count down windows (Qt4)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	13-May-2008
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


from PyQt4.QtCore import *		# Qt core
from PyQt4.QtGui import *		# Qt GUI interface
from PyQt4.uic import *			# ui files realizer
import sys				# system support

from avc import *			# AVC

from random import randint		# random integer generator

UI_MAIN = 'qt4_countdown_main.ui'	# qt ui descriptor for main window
UI_CD = 'qt4_countdown.ui'		# qt ui descriptor for countdown window
TOPLEVEL_NAME = 'countdown'		# name of the top level widget
COUNTDOWN_PERIOD = 500			# count down at 2 unit per second
MAX_CREATION_PERIOD = 4000		# create a new count down at 1/2 this


class Countdown(AVC):
  """
  A countdown counter displayed in a Label widget. Count starts at given
  value. When count reaches zero the counter and its GUI are destroyed.
  """

  def __init__(self,count_start=10):

    # create GUI
    self.root = loadUi(UI_CD)
    self.root.show()

    # init the counter variable 
    self.counter = count_start

    # connect counter variable with label widget
    self.avc_connect(self.root)

    # start count down
    self.timer = QTimer(self.root)
    self.root.connect(self.timer,SIGNAL("timeout()"),self.decrementer)
    self.timer.start(COUNTDOWN_PERIOD)


  def decrementer(self):
    "Counter decrementer. Return False to destroy previous timer."
    self.counter -= 1
    # if counter reached zero, destroy this countdown and its GUI
    if not self.counter:
      self.timer.stop()
      del self.timer
      self.root.close()


class Example(QApplication,AVC):
  """
  Continuously create at random intervals windows with a countdown from 10 to 0.
  When a countdown reaches zero, its window is destroyed. Also create a main
  window with a "close all" button.
  """

  def __init__(self):

    # create main window
    QApplication.__init__(self,sys.argv)
    self.root = loadUi(UI_MAIN)
    self.root.show()
    
    # close all button connected variable
    self.close_all = False

    # start count down
    self.timer = QTimer(self)
    self.connect(self.timer,SIGNAL("timeout()"),self.new_countdown)
    self.timer.start(randint(1,MAX_CREATION_PERIOD))


  def new_countdown(self,count_start=10):
    "Create a new countdown"

    # create a new countdown
    Countdown(count_start)

    # autocall after a random delay
    self.timer.stop()
    self.timer.start(randint(1,MAX_CREATION_PERIOD)) 


  def close_all_changed(self,value):
    "Terminate program at 'close all' button pressing"
    self.quit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.exec_()				# run Qt event loop until quit

#### END
