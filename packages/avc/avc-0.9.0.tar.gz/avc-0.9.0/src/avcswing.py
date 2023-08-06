# .+
# .context    : Application View Controller
# .title      : AVC Swing bindings
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	18-Nov-2007
# .copyright  :	(c) 2007-2011 Fabrizio Pollastri
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


#### IMPORT REQUIRED MODULES

from java import awt,beans	# awt and beans tool kit bindings
from javax import swing		# swing tool kit bindings
from java.lang import System	# to get java version

import sys


#### GENERAL ABSTRACTION METHODS

def toplevel_widgets():
  "Return the list of all top level widgets"
  return awt.Frame.getFrames().tolist()

def init(core,*args,**kwargs):
  "Do init specific for this widget toolkit"
  # mapping between the real widget and the wal widget
  core['avccd'].widget_map = { \
    swing.JButton:	core['Button'], \
    swing.JCheckBox:	core['ToggleButton'], \
    swing.JColorChooser:core['ColorChooser'], \
    swing.JComboBox:	core['ComboBox'],\
    swing.JTextField:	core['Entry'], \
    swing.JLabel:	core['Label'], \
    swing.JProgressBar:	core['ProgressBar'], \
    swing.JRadioButton:	core['RadioButton'], \
    swing.JSlider:	core['Slider'], \
    swing.JSpinner:	core['SpinButton'], \
    swing.JTable:	core['ListView'],
    swing.JTextArea:	core['TextView'],
    swing.JToggleButton:core['ToggleButton'],
    swing.JTree:	core['TreeView']}
  # get toolkit version
  core['avccd'].toolkit_version = System.getProperties()['java.runtime.version']

def widget_children(widget):
  "Return the list of all children of the widget"
  # Widgets that are not a subclass of awt.Container have no children.
  if isinstance(widget,awt.Container):
    return widget.components.tolist()
  else:
    return []

def widget_name(widget):
  "Return the widget name"
  widgetname = widget.getName()
  if not widgetname:
    widgetname = '<unnamed>'
  return widgetname

def timer(function,period):
  """
  Start a Swing timer calling back 'function' every 'period' seconds.
  Return timer instance.
  """
  swing_timer = swing.Timer(int(period * 1000.0),None)
  swing_timer.actionPerformed = lambda event: function()
  swing_timer.start()
  return swing_timer


class error(Exception):
  "A generic error exception"
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


#### WIDGETS ABSTRACTION LAYER (widget toolkit side)


class Widget:
  "Widget Abstraction Layer abstract class"

  def __init__(self,allowed_types=None):
    # check for supported control type
    if allowed_types and not self.connection.control_type in allowed_types:
      raise error, "Control type '%s' not supported with '%s' widget" % \
        (self.connection.control_type.__name__,self.widget.__class__.__name__)

  def connect_delete(self,widget,delete_method):
    "Connect widget delete method to destroy event"
    # it seems that swing has no destroy signal euivalent for widgets
    pass

class ListTreeView(Widget):
  "Support to ListView and TreeView abstractors"

  def append_column(self,col_num,text):
    "Append a column to the ListTreeView"
    pass


class Button(Widget):
  "Button widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.stateChanged = self.value_changed

  def read(self):
    "Get button status"
    return self.widget.model.isArmed()

  def write(self,value):
    "Set button status"
    self.widget.model.setArmed(value)


class Calendar(Widget):
  "Widget not in swing"

  def __init__(self):
      pass


class ColorChooser(Widget):
  "ColorChooser widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.getSelectionModel().stateChanged = self.value_changed

  def read(self):
    "Get button status"
    color = self.widget.getColor()
    return (color.getRed() / 255., color.getGreen() / 255.,
            color.getBlue() / 255., color.getAlpha() / 255.)

  def write(self,value):
    "Set button status"
    self.widget.setColor(awt.Color(*value))


class ComboBox(Widget):
  "ComboBox widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.addActionListener(ActionListener(self.value_changed))

  def read(self):
    "Get index of selected item"
    return self.widget.getSelectedIndex()

  def write(self,value):
    "Set selected item by its index value"
    self.widget.setSelectedIndex(value)


class Entry(Widget):
  "Entry widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.keyReleased = self.value_changed

  def read(self):
    "Get text from Entry"
    return self.connection.control_type(self.widget.getText())
    
  def write(self,value):
    "Set text into Entry"
    self.widget.setText(str(value))
 

class Label(Widget):
  "Label widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get value from Label"
    return self.widget.text

  def write(self,value):
    "Set text into Label"
    self.widget.text = value


class ListView(ListTreeView):
  "ListView widget abstractor"

  def __init__(self):
    # prepare data model.
    self.model = swing.table.DefaultTableModel(1,len(self.row_types))
    # set model to widget
    self.widget.setModel(self.model)
    # connect relevant signals
    self.model.addTableModelListener(TableModelListener(self.value_changed))

  def read(self):
    "Get values displayed by widget"
    # get head
    head = map(lambda col_num: str(self.model.getColumnName(col_num)),
      range(self.model.getColumnCount()))
    # get data rows
    body = [[str(item) for item in row] for row in self.model.getDataVector()]
    # return
    return {'head': head,'body': body}

  def write(self,value):
    "Set values displayed by widget"
    # set header
    if value.has_key('head'):
      head = value['head']
      col_model = self.widget.getColumnModel()
      map(lambda col_num, col_name:
        col_model.getColumn(col_num).setHeaderValue(col_name),
        range(self.model.getColumnCount()),head)
    else:
      head = [''] * len(self.row_types)  
    # set data rows
    self.model.setDataVector(value['body'],head)


class ProgressBar(Widget):
  "ProgressBar widget abstractor"

  def __init__(self):
    self.minimum = self.widget.getMinimum()
    self.range = self.widget.getMaximum() - self.minimum

  def read(self):
    "Get progress bar position"
    return self.widget.value
    
  def write(self,value):
    "Set progress bar position"
    # negative values pulse the bar, positive values position the bar. 
    if value < 0:
      self.widget.indeterminate = True
    else:
      self.widget.indeterminate = False
      self.widget.value = int(self.minimum + self.range * value)
 

class RadioButton(Widget):
  "RadioButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.stateChanged = self.value_changed

  def read(self):
    "Get index of activated button"
    rbuttons = self.widget.model.getGroup().getElements()
    for index,rbutton in enumerate(rbuttons):
      if rbutton.model.isSelected():
        break
    return index

  def write(self,value):
    "Set activate button indexed by value"
    rbuttons = self.widget.model.getGroup().getElements()
    rbuttons_list = [rbutton for rbutton in rbuttons]
    rbutton = rbuttons_list[value]
    rbutton.model.setSelected(True)


class Slider(Widget):
  "Slider widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.stateChanged = self.value_changed
 
  def read(self):
    "Get Slider value"
    return self.connection.control_type(self.widget.getModel().getValue())

  def write(self,value):
    "Set Slider value"
    self.widget.getModel().setValue(value)


class SpinButton(Widget):
  "SpinButton widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.stateChanged = self.value_changed

  def read(self):
    "Get spinbutton value"
    return self.connection.control_type(self.widget.value)

  def write(self,value):
    "Set spinbutton value"
    self.widget.setValue(value)


class StatusBar(Widget):
  "StatusBar widget abstractor"

  def __init__(self):
    pass

  def set_value(self,value):
    "Set StatusBar value"
    self.widget.pop(1)
    self.widget.push(1,value)


class TextView(Widget):
  "TextView widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.keyReleased = self.value_changed

  def read(self):
    "Get text from TextView"
    return self.widget.getText()
    
  def write(self,value):
    "Set text into TextView"
    self.widget.setText(value)


class ToggleButton(Widget):
  "ToggleButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.stateChanged = self.value_changed

  def read(self):
    "Get button status"
    return self.widget.model.isSelected()

  def write(self,value):
    "Set button status"
    self.widget.model.setSelected(value)


class TreeView(ListTreeView):
  "TreeView widget abstractor"

  def __init__(self):
    # check for allowed control type
    if self.connection.control_value.get('head',None):
      raise error, "%s widget do not support header." \
        % self.widget.__class__.__name__
    key,row = self.connection.control_value.get('body',None).iteritems().next()
    if type(row) == list and not len(row) == 1:
      raise error,"%s widget do not allow data rows with more than one column."\
        % self.widget.__class__.__name__
    # prepare data model.
    self.model =swing.tree.DefaultTreeModel(swing.tree.DefaultMutableTreeNode())
    # set model to widget
    self.widget.setModel(self.model)
    # connect relevant signals
    self.model.addTreeModelListener(TreeModelListener(self.value_changed))
   
  def read(self):
    "Get values displayed by widget"
    # get data rows
    body = {}
    # recursive depth first tree data node reader
    def read_node(node,node_path):
      try:
        body['.'.join(map(str,node_path))] = \
          self.row_types[0](node.toString())
      except:
        if self.row_types[0] == int:
          body['.'.join(map(str,node_path))] = [0]
        elif self.row_types[0] == float:
          body['.'.join(map(str,node_path))] = [0.0]
      children = list(node.children())
      for child_num,child in enumerate(children):
        read_node(child,node_path+[child_num+1])
    root = self.model.getRoot()
    children = list(root.children())
    for child_num,child in enumerate(children):
      read_node(child,[child_num+1])
    # return
    return {'body': body}

  def write_head(self,head):
    "Header not supported"
    pass

  def root_node(self):
    "Return the root node of the tree"
    return self.model.getRoot()

  def add_node(self,parent,last_node,current_depth,data):
    "Add current node to the tree"
    node = swing.tree.DefaultMutableTreeNode(data)
    parent.add(node)
    return node


## support classes

class ActionListener(awt.event.ActionListener):
  "Define status change handler"

  def __init__(self,value_changed):
    self.value_changed = value_changed

  def actionPerformed(self,*args):
    self.value_changed()


class TableModelListener(swing.event.TableModelListener):
  "Define table model change handler"

  def __init__(self,value_changed):
    self.value_changed = value_changed

  def tableChanged(self,*args):
    self.value_changed()


class TreeModelListener(swing.event.TreeModelListener):
  "Define tree model change handler"

  def __init__(self,value_changed):
    self.value_changed = value_changed

  def treeNodesChanged(self,*args):
    self.value_changed()

#### END
