#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A random generation of count down windows (GTK)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	11-Feb-2008
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


import gobject				#--
import gtk				#- gimp tool kit bindings
import gtk.glade			# glade bindings

from avc import *			# AVC

from random import randint		# random integer generator

GLADE_XML_MAIN = 'gtk_countdown_main.glade'	# main window glade descriptor
GLADE_XML_CD = 'gtk_countdown.glade'	# count down window glade descriptor
TOPLEVEL_NAME = 'countdown'		# name of the top level widget
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
    self.glade = gtk.glade.XML(GLADE_XML_CD)

    # autoconnect GUI signal handlers
    self.glade.signal_autoconnect(self)

    # init the counter variable 
    self.counter = count_start

    # connect counter variable with label widget
    self.avc_connect(self.glade.get_widget(TOPLEVEL_NAME))

    # start count down
    gobject.timeout_add(COUNTDOWN_PERIOD,self.decrementer)


  def decrementer(self):
    "Counter decrementer. Return False to destroy previous timer."
    self.counter -= 1

    if self.counter:
      # if counter not zero: reschedule count timer
      gobject.timeout_add(COUNTDOWN_PERIOD,self.decrementer)
    else:
      # counter reached zero: destroy this countdown and its GUI
      self.glade.get_widget(TOPLEVEL_NAME).destroy()

    return False


class Example(AVC):
  """
  Continuously create at random intervals windows with a countdown from 10 to 0.
  When a countdown reaches zero, its window is destroyed. Also create a main
  window with a "close all" button.
  """

  def __init__(self):

    # create main window
    self.glade = gtk.glade.XML(GLADE_XML_MAIN)

    # create the first countdown after avc_init call
    gobject.timeout_add(FIRST_COUNT_DELAY,self.new_countdown) 

    # close all button connected variable
    self.close_all = False

    # autoconnect GUI signal handlers
    self.glade.signal_autoconnect(self)


  def new_countdown(self,count_start=10):
    "Create a new countdown"

    # create a new countdown
    Countdown(count_start)

    # autocall after a random delay
    gobject.timeout_add(randint(1,MAX_CREATION_PERIOD),self.new_countdown) 

    return False			# destroy previous timer


  def on_destroy(self,window):
    "Terminate program at window destroy"
    gtk.main_quit()

  def close_all_changed(self,value):
    "Terminate program at 'close all' button pressing"
    gtk.main_quit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
gtk.main()				# run GTK event loop until quit

#### END
