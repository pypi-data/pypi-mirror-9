#!/usr/bin/python
# .+
#
# .identifier :	$Id: example2.py,v 1.1 2006/11/20 17:31:56 fabrizio Exp $
# .context    : Application View Controller 
# .title      : A table of all supported widget/control type conbinations (Tk)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	6-Jun-2007
# .copyright  : (c) 2007 Fabrizio Pollastri
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


from Tkinter import * 			# Tk interface

from avc import *			# AVC

TCL_FILE = 'tk_showcase.tcl'		# GUI description as tcl script
INCREMENTER_PERIOD = 0.333		# seconds


class Example(AVC):
  """
  A table of all supported widget/control type combinations
  """

  def __init__(self):

    # create GUI
    self.root = Tk()
    self.root.eval('set argc {}; set argv {}; proc ::main {argc argv} {};')
    self.root.tk.evalfile(TCL_FILE)

    # terminate program at toplevel window destroy: connect toplevel
    # destroy signal to termination handler.
    self.root.bind_class('Toplevel','<Destroy>',lambda event: self.root.quit())

    # the control variables
    self.boolean1 = False
    self.boolean2 = False
    self.radio = 0
    self.integer = 0
    self.float = 0.0
    self.string = ''
    self.textview = ''

    # start variables incrementer
    increment = self.incrementer()
    self.timer_function = increment.next
    self.root.after(int(INCREMENTER_PERIOD * 1000.0),self.timer_wrap)


  def timer_wrap(self):
    "Call given function, reschedule it after return"
    self.timer_function()
    self.root.after(int(INCREMENTER_PERIOD * 1000.0),self.timer_wrap)


  def incrementer(self):
    """
    Booleans are toggled, radio button index is rotated from first to last,
    integer is incremented by 1, float by 0.5, string is appended a char
    until maxlen when string is cleared, text view/edit is appended a line
    of text until maxlen when it is cleared.
    Return True to keep timer alive.
    """
    while True:
      self.boolean1 = not self.boolean1
      yield True

      self.boolean2 = not self.boolean2
      yield True

      if self.radio == 2:
        self.radio = 0
      else:
        self.radio += 1
      yield True

      self.integer += 1
      yield True

      self.float += 0.5
      yield True

      if len(self.string) >= 20:
        self.string = 'A'
      else:
        self.string += 'A'
      yield True

      if len(self.textview) >= 200:
        self.textview = ''
      else:
        self.textview += 'line of text, line of text, line of text\n'
      yield True


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
mainloop()				# run Tk event loop until quit

#### END
