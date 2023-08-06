# .+
# .context    : Application View Controller
# .title      : AVC Qt4 bindings
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	7-Nov-2006
# .copyright  :	(c) 2006-2013 Fabrizio Pollastri
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
# along with AVC.  If not, see <http://www.gnu.org/licenses/>.
#
# .-


#### IMPORT REQUIRED MODULES

import PyQt4.Qt as qt		# Qt4 tool kit GUI bindings
from PyQt4.QtCore import Qt # Qt4 tool kit GUI attribute bindings

import string			# string operations


#### GENERAL ABSTRACTION METHODS

def toplevel_widgets():
  "Return the list of all top level widgets"
  return qt.QApplication.topLevelWidgets()

def init(core):
  "Do init specific for this widget toolkit"
  # mapping between the real widget and the wal widget
  core['avccd'].widget_map = { \
    qt.QPushButton: 	core['Button'], \
    qt.QCalendarWidget: core['Calendar'], \
    qt.QCheckBox:   	core['ToggleButton'], \
    qt.QColorDialog:    core['ColorChooser'], \
    qt.QComboBox:   	core['ComboBox'], \
    qt.QLineEdit:	    core['Entry'], \
    qt.QLabel:		    core['Label'], \
    qt.QProgressBar:	core['ProgressBar'], \
    qt.QRadioButton:	core['RadioButton'], \
    qt.QSlider:	    	core['Slider'], \
    qt.QSpinBox:	    core['SpinButton'], \
    qt.QDoubleSpinBox:	core['SpinButton'], \
    qt.QTextEdit:   	core['TextView'], \
    qt.QTreeWidget:	    core['listtreeview']}
  # get toolkit version
  core['avccd'].toolkit_version = qt.PYQT_VERSION_STR

def widget_children(widget):
  "Return the list of all children of the widget"
  return widget.children()

def widget_name(widget):
  "Return the widget name"
  return str(widget.objectName())

def timer(function,period):
  "Start a Qt timer calling back 'function' every 'period' seconds."
  timer = qt.QTimer()
  qt.QObject.connect(timer,qt.SIGNAL("timeout()"),function)
  timer.start(int(period * 1000.0))
  return timer


#### WIDGETS ABSTRACTION LAYER (widget toolkit side)

class Widget:
  "Qt4 Widget Abstraction Layer abstract class"

  def connect_delete(self,widget,delete_method):
    "Connect widget delete method to close and destroy events"
    widget.window().setAttribute(Qt.WA_DeleteOnClose)
    qt.QObject.connect(widget,qt.SIGNAL("destroyed()"),delete_method)


class ListTreeView(Widget):
  "Support to ListView and TreeView abstractors"

  def __init__(self):
    "Init operations common to ListView and TreeView"

    # clear all items and remove all columns, if any
    self.widget.clear()

    # add required columns to TreeView widget with title (header), if required.
    head = self.connection.control_value.get('head',None)
    self.widget.setColumnCount(len(self.row_types))
    if head:
      self.widget.setHeaderLabels(head)
    else:
      pass

    # connect relevant signals
    qt.QObject.connect(self.widget.model(),
      qt.SIGNAL("layoutChanged()"),self.value_changed)
    qt.QObject.connect(self.widget.model(),
      qt.SIGNAL("dataChanged()"),self.value_changed)
    qt.QObject.connect(self.widget.model(),
      qt.SIGNAL("headerDataChanged()"),self.value_changed)


  def append_column(self,col_num,text):
   "Append a column to the TreeView"
   pass


class Button(Widget):
  "Qt4 Button widget abstractor"

  def __init__(self):
    # connect relevant signals
    qt.QObject.connect(
      self.widget,qt.SIGNAL("pressed()"),self.value_changed)
    qt.QObject.connect(
      self.widget,qt.SIGNAL("released()"),self.value_changed)

  def read(self):
    "Get button status"
    return self.widget.isDown()

  def write(self,value):
    "Set button status"
    self.widget.setDown(value)


class Calendar(Widget):
  "Qt4 Calendar widget abstractor"

  def __init__(self):
    # connect relevant signals
    qt.QObject.connect(
      self.widget,qt.SIGNAL("selectionChanged()"),self.value_changed)

  def read(self):
    "Get selected date"
    date = self.widget.selectedDate()
    return (date.year(),date.month(),date.day())

  def write(self,value):
    "Set selected date"
    self.widget.setSelectedDate(qt.QDate(*value))


class ColorChooser(Widget):
  "Qt4 ColorChooser widget abstractor"

  def __init__(self):
    # persistent color object
    self.color = qt.QColor()
    # connect relevant signals
    qt.QObject.connect(
      self.widget,qt.SIGNAL("colorSelected(QColor)"),self.value_changed)

  def read(self):
    "Get selected color"
    return self.widget.selectedColor().getRgbF()

  def write(self,value):
    "Set selected color"
    self.color.setRgbF(*value)
    self.widget.setCurrentColor(self.color)


class ComboBox(Widget):
  "Qt4 ComboBox widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    qt.QObject.connect(
      self.widget,qt.SIGNAL("activated(int)"),self.value_changed)

  def read(self):
    "Get index of selected item"
    return self.widget.currentIndex()

  def write(self,value):
    "Set selected item by its index value"
    self.widget.setCurrentIndex(value)


class Entry(Widget):
  "Qt4 Entry widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    qt.QObject.connect(
      self.widget,qt.SIGNAL("returnPressed()"),self.value_changed)

  def read(self):
    "Get text from Entry"
    return self.widget.text()
    
  def write(self,value):
    "Set text into Entry"
    self.widget.setText(str(value))


class Label(Widget):
  "Qt4 Label widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get text into Label"
    return str(self.widget.text())

  def write(self,value):
    "Set text into Label"
    self.widget.setText(value)


class ListView(Widget):
  "Qt4 TreeView widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get values displayed by widget"
    # get head
    header = self.widget.headerItem()
    head = map(lambda col_num: str(header.text(col_num)),
      range(self.widget.columnCount()))
    # get data rows
    body = []
    item = self.widget.itemAt(0,0)
    while item:
      row = []
      for col_num in range(self.cols_num):
        try:
          row.append(self.row_types[col_num](item.text(col_num)))
        except:
          if self.row_types[col_num] == int:
            row.append(0)
          elif self.row_types[col_num] == float:
            row.append(0.0)
      body.append(row)
      item = self.widget.itemBelow(row)
    # return
    return {'head': head,'body': body}


  def write(self,value):
    "Set values displayed by widget"
    # set header
    if value.has_key('head'):
      self.widget.setHeaderLabels(value['head'])
    # set data rows
    self.widget.clear()
    body = value['body']
    last_item = None
    if type(body[0]) == list:
      for row in body:
        self.widget.addTopLevelItem(qt.QTreeWidgetItem(map(str,row)))
    else:
      for row in body:
        self.widget.addTopLevelItem(qt.QTreeWidgetItem(str(row)))


class ProgressBar(Widget):
  "Qt4 ProgressBar widget abstractor"

  def __init__(self):
    # set value range to 0-100
    self.widget.setMinimum(0)
    self.widget.setMaximum(100)
    pass

  def read(self):
    "Get progress bar position"
    return self.widget.value() / 100.0
    
  def write(self,value):
    "Set progress bar position"
    # negative values pulse the bar, positive values position the bar. 
    if value < 0:
      self.widget.setMinimum(0)
      self.widget.setMaximum(0)
      self.widget.setValue(0)
    else:
      self.widget.setMinimum(0)
      self.widget.setMaximum(100)
      self.widget.setValue(int(round(value * 100)))


class RadioButton(Widget):
  "Qt4 RadioButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    qt.QObject.connect(
      self.widget,qt.SIGNAL("clicked()"),self.value_changed)

  def read(self):
    "Get index of activated button"
    return self.widget.group().checkedId()

  def write(self,value):
    "Set activate button indexed by value"
    self.widget.group().buttons()[value].setChecked(True)

 
class Slider(Widget):
  "Qt4 Slider widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    qt.QObject.connect(
      self.widget,qt.SIGNAL("valueChanged(int)"),self.value_changed)

  def read(self):
    "Get Slider value"
    return self.widget.value()

  def write(self,value):
    "Set Slider value"
    self.widget.setValue(value)


class SpinButton(Widget):
  "Qt4 SpinButton widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    # QSpinBox manages integers, while QDoubleSpinBox manages floats
    if self.widget.__class__ == qt.QSpinBox:
      SIGNAL_NAME = "valueChanged(int)"
    else:
      SIGNAL_NAME = "valueChanged(double)"
    qt.QObject.connect(
      self.widget,qt.SIGNAL(SIGNAL_NAME),self.value_changed)

  def read(self):
    "Get spinbutton value"
    return self.widget.value()

  def write(self,value):
    "Set spinbutton value"
    self.widget.setValue(value)


class StatusBar(Widget):
  "Q4 no status bar support"
  pass


class TextView(Widget):
  "Qt4 TextView/Edit widget abstractor"

  def __init__(self):
    # connect relevant signals
    qt.QObject.connect(
      self.widget,qt.SIGNAL("textChanged()"),self.value_changed)

  def read(self):
    "Get text from TextView"
    return str(self.widget.toPlainText())
    
  def write(self,value):
    "Set text into TextView"
    self.widget.setPlainText(str(value))
 

class ToggleButton(Widget):
  "Qt4 ToggleButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    qt.QObject.connect(
      self.widget,qt.SIGNAL("clicked()"),self.value_changed)

  def read(self):
    "Get button status"
    return self.widget.isChecked()

  def write(self,value):
    "Set button status"
    self.widget.setChecked(value)


class TreeView(Widget):
  "Qt4 TreeView widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get values displayed by widget"
    # get head
    header = self.widget.headerItem()
    head = map(lambda col_num: str(header.text(col_num)),
      range(self.widget.columnCount()))
    # get data row
    body = {}
    # recursive depth first tree data node reader
    def read_node(node,node_path):
      row = []
      for col_num in range(self.cols_num):
        try:
            row.append(self.row_types[col_num](node.text(col_num)))
        except:
          if self.row_types[col_num] == int:
            row.append(0)
          elif self.row_types[col_num] == float:
            row.append(0.0)
      body[string.join(map(str,node_path),'.')] = row
      for child_num in range(node.childCount()):
        read_node(node.child(child_num),node_path+[child_num+1])
    for node_num in range(self.widget.topLevelItemCount()):
      read_node(self.widget.topLevelItem(node_num),[node_num+1])
    # return
    return {'head': head,'body': body}

  def write_head(self,head):
    self.widget.setHeaderLabels(head)

  def root_node(self):
    "Return the root node of the tree"
    return self.widget

  def add_node(self,parent,last_node,current_depth,data):
    "Add current node to the tree"
    node = qt.QTreeWidgetItem(map(str,data))
    if current_depth == 1:
      self.widget.addTopLevelItem(node)
    else:
      parent.addChild(node)
    return node
 
#### END
