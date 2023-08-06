#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A counter with count speed control (Tk)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	12-May-2008
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


from Tkinter import *			# Tk interface

from avc import *			# AVC for Tk

from random import randint		# random integer generator

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

    ## create GUI

    # main window
    self.root = Tk()
    self.root.title('AVC Tk countdown example')
    self.frame = Frame(self.root,name='countdown',width=350,height=50)
    self.frame.pack(expand=1)

    # count down label
    self.label = Label(self.frame,name='counter')
    self.label.place(relx=0.5,rely=0.4,anchor=CENTER)

    # terminate program at toplevel window destroy: connect toplevel
    # destroy signal to termination handler.
    self.root.bind_class('Toplevel','<Destroy>',lambda event: self.root.quit())

    # init the counter variable 
    self.counter = count_start

    # connect counter variable with label widget
    self.avc_connect(self.root)

    # start count down
    self.root.after(COUNTDOWN_PERIOD,self.decrementer)


  def decrementer(self):
    "Counter decrementer. Return False to destroy previous timer."
    self.counter -= 1
    if self.counter:
      # if counter not zero: reschedule count timer
      self.root.after(COUNTDOWN_PERIOD,self.decrementer)
    else:
      # counter reached zero: destroy this countdown and its GUI
      self.root.destroy()


class Example(AVC):
  """
  Continuously create at random intervals windows with a countdown from 10 to 0.
  When a countdown reaches zero, its window is destroyed. Also create a main
  window with a "close all" button.
  """

  def __init__(self):

    ## create GUI

    # main window
    self.root = Tk()
    self.root.title('AVC Tk countdown example')
    self.frame = Frame(self.root,name='countdown',width=350,height=50)
    self.frame.pack(expand=1)

    # close all button
    self.button = Button(self.frame,name='close_all',text='CLOSE ALL WINDOWS')
    self.button.place(relx=0.5,rely=0.5,anchor=CENTER)

    # terminate program at toplevel window destroy: connect toplevel
    # destroy signal to termination handler.
    self.root.bind_class('Toplevel','<Destroy>',lambda event: self.root.quit())

    # create the first countdown after avc_init call
    self.root.after(FIRST_COUNT_DELAY,self.new_countdown) 

    # close all button connected variable
    self.close_all = False


  def new_countdown(self,count_start=10):
    "Create a new countdown"

    # create a new countdown
    Countdown(count_start)

    # autocall after a random delay
    self.root.after(randint(1,MAX_CREATION_PERIOD),self.new_countdown) 


  def close_all_changed(self,value):
    "Terminate program at 'close all' button pressing"
    self.root.quit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
mainloop()			 	# run Tk event loop until quit

#### END
