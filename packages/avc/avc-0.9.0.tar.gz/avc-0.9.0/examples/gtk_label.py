#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : Formatting capabilities for label widget (GTK)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	2-Jan-2008
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
import gtk.glade			# glade bindings

from avc import *			# AVC

GLADE_XML = 'gtk_label.glade'		# GUI glade descriptor


class Example(AVC):
  """
  Showcase of formatting capabilities for the label widget
  """

  def __init__(self):

    # create GUI
    self.glade = gtk.glade.XML(GLADE_XML)

    # autoconnect GUI signal handlers
    self.glade.signal_autoconnect(self)

    # all types of connected variables
    self.bool_value = True
    self.dict_value = {'k1':'A','k2':'B'}
    self.float_value = 1.0
    self.int_value = 1
    self.list_value = [1,2,3]
    self.str_value = 'abc'
    self.tuple_value = (1,2,3)
    class Obj:
      "A generic object with 2 attributes x,y"
      def  __init__(self):
        self.x = 1
        self.y = 2
    self.obj_value = Obj()


  def on_destroy(self,window):
    "Terminate program at window destroy"
    gtk.main_quit()


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
gtk.main()			 	# run GTK event loop until quit

#### END
