#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : Formatting capabilities for label widget (Qt4)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	3-Jan-2008
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

UI_FILE = 'qt4_label.ui'		# qt ui descriptor


class Example(QApplication,AVC):
  """
  Showcase of formatting capabilities for the label widget
  """

  def __init__(self):

    # create GUI
    QApplication.__init__(self,sys.argv)
    self.root = loadUi(UI_FILE)
    self.root.show()
    
    # all types of connected variables
    self.bool_value = True
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
   

#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.exec_()				# run Qt event loop until quit

#### END
