#!/usr/bin/python
# .+
#
# .identifier :	$Id:$
# .context    : Application View Controller
# .title      : A spin box replicated into a text label (Qt4)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	10-Jan-2008
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
import sys				# system support

from avc import *			# AVC


class Example(QApplication,AVC):
  """
  A spin box whose value is replicated into a text label
  """

  def __init__(self):

    ## create GUI

    QApplication.__init__(self,sys.argv)

    # main window
    self.window = QWidget()
    self.window.setWindowTitle('AVC Qt4 spin box example')
    self.window.resize(280,70)

    # horizontal layout for widgets inside main window
    self.hbox = QHBoxLayout()
    self.window.setLayout(self.hbox)

    # label replicating the spin box value with formatting string
    self.label = QLabel()
    self.label.setObjectName('spin_value__label')
    self.label.setText('<b>%d</b>')
    self.hbox.addWidget(self.label)
     
    # spin box
    self.spinbox = QSpinBox()
    self.spinbox.setRange(0,100)
    self.spinbox.setObjectName('spin_value__spinbox')
    self.hbox.addWidget(self.spinbox)

    # show all widgets
    self.window.show()


    # the variable holding the spin box value
    self.spin_value = 0


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
example.exec_()				# run Qt event loop until quit

#### END
