# .+
# .context    : Application View Controller
# .title      : AVC GTK+ bindings
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	7-Nov-2006
# .copyright  :	(c) 2006-2011 Fabrizio Pollastri
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

import gtk			#--
import gobject			#- gimp tool kit bindings

import string			# string operations

#### GENERAL ABSTRACTION METHODS

def toplevel_widgets():
  "Return the list of all top level widgets"
  return gtk.window_list_toplevels()

def init(core):
  "Do init specific for this widget toolkit"
  # mapping between the real widget and the wal widget
  core['avccd'].widget_map = { \
  gtk.Button:		    core['Button'], \
  gtk.Calendar:	    	core['Calendar'], \
  gtk.CheckButton:	    core['ToggleButton'], \
  gtk.ComboBox:	    	core['ComboBox'],\
  gtk.ColorSelection:	core['ColorChooser'],\
  gtk.Entry:    		core['Entry'], \
  gtk.Label:	    	core['Label'], \
  gtk.ProgressBar:	    core['ProgressBar'], \
  gtk.RadioButton:  	core['RadioButton'], \
  gtk.HScale:		    core['Slider'], \
  gtk.SpinButton:	    core['SpinButton'], \
  gtk.Statusbar:    	core['StatusBar'], \
  gtk.TextView:		    core['TextView'], \
  gtk.ToggleButton:	    core['ToggleButton'], \
  gtk.TreeView:		    core['listtreeview'], \
  gtk.VScale:		    core['Slider']}
  # get toolkit version
  core['avccd'].toolkit_version = '.'.join(map(str,gtk.gtk_version))

def widget_children(widget):
  "Return the list of all children of the widget"
  # widgets that are not a subclass of gtk.Container have no children.
  if isinstance(widget,gtk.Container):
    return widget.get_children()
  else:
    return []

def widget_name(widget):
  "Return the widget name"
  return widget.get_name()

def timer(function,period):
  """
  Start a GTK timer calling back 'function' every 'period' seconds.
  Return timer id.
  """
  return gobject.timeout_add(int(period * 1000.0),timer_wrap,function)

def timer_wrap(function):
  "Call given function and return True to keep timer alive"
  function()
  return True


#### WIDGETS ABSTRACTION LAYER (widget toolkit side)

class Widget:
  "GTK Widget Abstraction Layer abstract class"

  def __init__(self,allowed_types=None):
    # check for supported control type
    if allowed_types and not self.connection.control_type in allowed_types:
      raise error, "Control type '%s' not supported with '%s' widget" % \
        (self.connection.control_type.__name__,self.widget.__class__.__name__)

  def connect_delete(self,widget,delete_method):
    "Connect widget delete method to destroy event"
    widget.connect("destroy",delete_method)


class ListTreeView(Widget):
  "Support to ListView and TreeView abstractors"

  def __init__(self):
    "Init operations common to ListView and TreeView"
    pass

  def append_column(self,col_num,text):
   "Append a column to the TreeView"
   self.widget.append_column(gtk.TreeViewColumn(
     text,gtk.CellRendererText(),text=col_num))
   

class Button(Widget):
  "GTK Button real widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("pressed",self.value_changed)
    self.widget.connect("released",self.value_changed)

  def read(self):
    "Get button status"
    if self.widget.state == gtk.STATE_ACTIVE:
      return True
    return False

  def write(self,value):
    "Set button status"
    if value:
      self.widget.set_state(gtk.STATE_ACTIVE)
    else:
      self.widget.set_state(gtk.STATE_NORMAL)


class Calendar(Widget):
  "GTK Calendar real widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("day-selected",self.value_changed)

  def read(self):
    "Get calendar date"
    date = self.widget.get_date()
    # make month number starting from 1
    return (date[0],date[1]+1,date[2])

  def write(self,value):
    "Set calendar date"
    # make month number starting from 0
    self.widget.select_month(value[1]-1,value[0])
    self.widget.select_day(value[2])


class ColorChooser(Widget):
  "GTK ColorChooser real widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("color-changed",self.value_changed)

  def read(self):
    "Get current color"
    color = self.widget.get_current_color()
    alpha = self.widget.get_current_alpha()
    # color from int to float 0.0-1.0
    return (color.red/65535.,color.green/65535.,color.blue/65535.,alpha/65535.)

  def write(self,value):
    "Set current color"
    self.widget.set_current_color(gtk.gdk.Color(
      int(value[0]*65535),int(value[1]*65535),int(value[2]*65535)))
    self.widget.set_current_alpha(int(value[3] * 65535))


class ComboBox(Widget):
  "GTK ComboBox widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("changed",self.value_changed)

  def read(self):
    "Get index of selected item"
    return self.widget.get_active()

  def write(self,value):
    "Set selected item by its index value"
    self.widget.set_active(value)


class Entry(Widget):
  "GTK Entry widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.connect("activate",self.value_changed)

  def read(self):
    "Get text from Entry"
    return self.widget.get_text()
    
  def write(self,value):
    "Set text into Entry"
    self.widget.set_text(str(value))
 

class Label(Widget):
  "GTK Label widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get value from Label"
    return self.widget.get_label()

  def write(self,value):
    "Set text into Label"
    self.widget.set_label(value)


class ListView(ListTreeView):
  "GTK TreeView widget abstractor"

  def __init__(self):
    # prepare data model.
    self.model = gtk.ListStore(*self.row_types)
    # set model to widget
    self.widget.set_model(self.model)

    # connect relevant signals
    self.model.connect("row-deleted",self.value_changed)
    self.model.connect("row-changed",self.value_changed)


  def read(self):
    "Get values displayed by widget"
    # get head
    head = map(gtk.TreeViewColumn.get_title,self.widget.get_columns())
    # get data rows
    body = []
    self.model.foreach(
      lambda model,path,iter,body: body.append(
        list(model.get(iter,*range(self.cols_num)))),body)
    # return
    return {'head': head,'body': body}


  def write(self,value):
    "Set values displayed by widget"
    # set header
    if value.has_key('head'):
      map(gtk.TreeViewColumn.set_title,self.widget.get_columns(),value['head'])
    # set data rows
    body = value['body']
    self.model.clear()
    if type(body[0]) == list:
      for row in body:
        self.model.append(row)
    else:
      for row in body:
        self.model.append([row])


class ProgressBar(Widget):
  "GTK ProgressBar widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get progress bar position"
    return self.widget.get_fraction()
    
  def write(self,value):
    "Set progress bar position"
    # negative values pulse the bar, positive values position the bar. 
    if value < 0:
      self.widget.pulse()
    else:
      self.widget.set_fraction(value)
 

class RadioButton(Widget):
  "GTK RadioButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("clicked",self.value_changed)

  def read(self):
    "Get index of activated button"
    button = self.widget
    buttons = button.get_group()
    for index,rbutton in enumerate(buttons):
      if rbutton.get_active():
        break
    index = len(buttons) - index - 1
    return index

  def write(self,value):
    "Set activate button indexed by value"
    button = self.widget
    rbuttons = button.get_group()
    rbutton = rbuttons[len(rbuttons) - value - 1]
    rbutton.set_active(True)


class Slider(Widget):
  "GTK Slider widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.connect("value_changed",self.value_changed)

  def read(self):
    "Get Slider value"
    return self.widget.get_value()

  def write(self,value):
    "Set Slider value"
    self.widget.set_value(value)


class SpinButton(Widget):
  "GTK SpinButton widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.connect("value_changed",self.value_changed)

  def read(self):
    "Get spinbutton value"
    return self.widget.get_value()

  def write(self,value):
    "Set spinbutton value"
    self.widget.set_value(value)


class StatusBar(Widget):
  "GTK StatusBar widget abstractor"

  def __init__(self):
    pass

  def write(self,value):
    "Set StatusBar value"
    self.widget.pop(1)
    self.widget.push(1,value)


class TextView(Widget):
  "GTK TextView widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.get_buffer().connect("changed",self.value_changed)

  def read(self):
    "Get text from TextView"
    textbuf = self.widget.get_buffer()
    return textbuf.get_text(textbuf.get_start_iter(),textbuf.get_end_iter())
    
  def write(self,value):
    "Set text into TextView"
    self.widget.get_buffer().set_text(str(value))


class ToggleButton(Widget):
  "GTK ToggleButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.connect("clicked",self.value_changed)

  def read(self):
    "Get button status"
    return self.widget.get_active()

  def write(self,value):
    "Set button status"
    self.widget.set_active(value)


class TreeView(ListTreeView):
  "GTK TreeView widget abstractor"

  def __init__(self):
    # prepare data model.
    self.model = gtk.TreeStore(*self.row_types)
    # set model to widget
    self.widget.set_model(self.model)

    # connect relevant signals
    self.model.connect("row-deleted",self.value_changed)
    self.model.connect("row-changed",self.value_changed)


  def read(self):
    "Get values displayed by widget"
    # get head
    head = map(gtk.TreeViewColumn.get_title,self.widget.get_columns())
    # get data rows
    body = {}
    # recursive depth first tree data node reader
    def read_node(node_iter,parent_id):
      node_id = string.join(
        map(lambda x: str(x+1),self.model.get_path(node_iter)),'.')
      body[node_id] = list(self.model.get(node_iter,*range(self.cols_num)))
      child_iter = self.model.iter_children(node_iter)
      while child_iter:
        read_node(child_iter,node_id)
        child_iter = self.model.iter_next(child_iter)
    node_iter = self.model.get_iter_first()
    while node_iter:
      read_node(node_iter,None)
      node_iter = self.model.iter_next(node_iter)
    # return
    return {'head': head,'body': body}

  def write_head(self,head):
    "Write header"
    map(gtk.TreeViewColumn.set_title,self.widget.get_columns(),head)

  def root_node(self):
    "Return the root node of the tree"
    return None

  def add_node(self,parent,last_node,current_depth,data):
    "Add current node to the tree"
    return self.model.append(parent,data)
      

#### END
