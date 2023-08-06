#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A spin button replicated into a label (GTK)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	6-Jan-2008
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


import gtk				# gimp tool kit bindings

from avc import *			# AVC


class Example(AVC):
  """
  A spin button whose value is replicated into a label
  """

  def __init__(self):

    ## create GUI
 
    # main window
    window = gtk.Window()
    window.set_title('AVC GTK spin button example')
    window.resize(310,50)
    window.connect('destroy',gtk.main_quit)

    # horizontal layout for widgets inside main window
    hbox = gtk.HBox()
    window.add(hbox)

    # label replicating the spin button value with formatting string
    label = gtk.Label()
    label.set_name('spin_value__label')
    label.set_markup('<b>%d</b>')
    hbox.add(label)

    # spin button
    spinbutton = gtk.SpinButton(gtk.Adjustment(0,0,100,1,5,0))
    spinbutton.set_name('spin_value__spinbutton')
    hbox.add(spinbutton)

    # show all widgets
    window.show_all()


    # the variable holding the spin button value
    self.spin_value = 0


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
gtk.main()			 	# run GTK event loop until quit

#### END
