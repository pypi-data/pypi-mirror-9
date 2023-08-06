#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : ColorDialog widget connected to label widget (Qt4)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	4-Feb-2013
# .copyright  : (c) 2013 Fabrizio Pollastri.
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
import sys				        # system support

from avc import *			    # AVC

UI_FILE = 'qt4_colordialog.ui'	# qt ui descriptor


class Example(QApplication,AVC):
  """
  ColorDialog connected to label widget (Qt4)
  """

  def __init__(self):

    # create GUI
    QApplication.__init__(self,sys.argv)
    self.root = loadUi(UI_FILE)
    self.root.show()

    # all types of connected variables
    self.open_color_chooser = False
    self.color_value = (0.25,0.5,1.0,1.0)
  

  def open_color_chooser_changed(self,value):
    """
    Create color chooser dialog connecting a color variable to it
    """
    if value:
      # create color chooser dialog with name matching 'color_value'
      self.color_chooser = QColorDialog()
      self.color_chooser.setObjectName('color_value__color_chooser')
      self.color_chooser.show()
      # connect color variable with color chooser
      self.avc_connect(self.color_chooser)


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.exec_()				# run Qt event loop until quit

#### END
