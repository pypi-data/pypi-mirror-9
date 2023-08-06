#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A spin control replicated into a text label (Tk)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	1-Jun-2007
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


from Tkinter import *			# Tk interface

from avc import *			# AVC for Tk


class Example(AVC):
  """
  A spin box whose value is replicated into a label
  """

  def __init__(self):

    ## create GUI

    # main window
    self.root = Tk()
    self.root.title('AVC Tk spin box example')
    self.frame = Frame(self.root,name='frame')
    self.frame.pack()

    # label replicating the spin box value
    self.label = Label(self.frame,name='spin_value__label',width=16,height=3)
    self.label.pack(side=LEFT)

    # spin box
    self.spinbox = Spinbox(self.frame,name='spin_value__spinbox',
      increment=1.0,to=100)
    self.spinbox.pack(side=RIGHT)


    # the variable holding the spin control value
    self.spin_value = 0


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
mainloop()			 	# run Tk event loop until quit

#### END
