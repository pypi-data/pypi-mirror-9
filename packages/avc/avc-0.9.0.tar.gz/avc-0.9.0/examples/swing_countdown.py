#!/usr/bin/env jython
# .+
# .context    : Application View Controller
# .title      : A random generation of count down windows (Swing),
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

from random import randint		# random integer generator
import sys				# system support

FIRST_COUNT_DELAY = 1000		# let avc_init be called
COUNTDOWN_PERIOD = 500			# count down at 2 unit per second
MAX_CREATION_PERIOD = 4000		# create a new count down at 1/2 this


class Countdown(AVC):
  """
  A countdown counter displayed in a Label widget. Count starts at given
  value. When count reaches zero the counter and its GUI are destroyed.
  """

  def __init__(self,count_start=10):

    # create GUI
    self.root = swing.JFrame('AVC Swing countdown example',size=(350,60),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    self.root.layout = awt.FlowLayout()
    self.root.add(swing.JLabel('counter',name='counter__label',))
    self.root.show()

    # init the counter variable 
    self.counter = count_start

    # connect counter variable with label widget
    self.avc_connect(self.root)

    # start count down
    self.timer = swing.Timer(COUNTDOWN_PERIOD,None)
    self.timer.actionPerformed = self.decrementer
    self.timer.start()
  

  def decrementer(self,*args):
    "Counter decrementer."
    self.counter -= 1

    if not self.counter:
      # counter reached zero: destroy this countdown and its GUI
      self.root.dispose()


class Example(AVC):
  """
  Continuously create at random intervals windows with a countdown from 10 to 0.
  When a countdown reaches zero, its window is destroyed. Also create a main
  window with a "close all" button.
  """

  def __init__(self):

    # create main window
    self.root = swing.JFrame('AVC Swing countdown example',size=(350,60),
      defaultCloseOperation = swing.JFrame.EXIT_ON_CLOSE)
    self.root.layout = awt.FlowLayout()
    self.root.add(swing.JButton('CLOSE ALL',name='close_all__button',))
    self.root.show()

    # create the first countdown after avc_init call
    self.timer = swing.Timer(FIRST_COUNT_DELAY,None)
    self.timer.actionPerformed = self.new_countdown
    self.timer.start()

    # close all button connected variable
    self.close_all = False


  def new_countdown(self,event,count_start=10):
    "Create a new countdown"

    # create a new countdown
    Countdown(count_start)

    # autocall after a random delay
    self.timer.setDelay(MAX_CREATION_PERIOD)


  def close_all_changed(self,value):
    "Terminate program at 'close all' button pressing"
    for frame in self.root.getFrames():
       frame.dispose()
    sys.exit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables

#### END
