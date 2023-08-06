# .+
# .context    : Application View Controller
# .title      : AVC Tk bindings
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	7-Nov-2006
# .copyright  : (c) 2006-2008 Fabrizio Pollastri
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

import Tkinter				# Tk interface


#### GENERAL ABSTRACTION METHODS

## redifinition of BaseWidget __init__ in Tkinter with a "monkey patch".
# The same as the original, but without any call to tcl interpreter.
# Needed to instantiate the python widget of a already existing tcl widget.

def _dummy_call(*args):
  return

def _basewidget_new_init(self, master, widgetName, cnf={}, kw={}, extra=()):
  """
  Construct a widget with the parent widget MASTER, a name WIDGETNAME
  and appropriate options.
  """
  if kw:
    cnf = Tkinter._cnfmerge((cnf, kw))
  self.widgetName = widgetName
  Tkinter.BaseWidget._setup(self, master, cnf)



def toplevel_widgets():
  "Return the list of all top level widgets"
  return [Tkinter._default_root]

def complete_widget_tree(widget):
  """
  Since direct usage of the tcl interpreter (call to "eval","evalfile" or
  "call") do not create any widget instance in python, complete the python
  widget tree instantiating the corresponding widget class from Tkinter
  for each widget created by the tcl interpreter.
  Do the work by visiting in deep first mode the widget tree with the tcl
  interpreter commands.
  Also build the list of all top level widgets.
  """
  children_path = widget.tk.eval('winfo children ' + str(widget)).split()
  for child_path in children_path:
    child_name = child_path.split('.')[-1]
    # if python widget do not exists, create it.
    if not widget.children.has_key(child_name):
      class_name = widget.tk.eval('winfo class ' + child_path)
      eval('Tkinter.' + class_name + '(widget,name="' + child_name + '")')
    # if widget is a toplevel window, append it to top level widgets list.
    ##if child_path == widget.tk.eval('winfo toplevel ' + child_path):
    ##  self._toplevel_widgets += [widget.nametowidget(child_path)]
    # go deep into widgets tree
    for child in widget.children.values():
      complete_widget_tree(child)

def init(core):
  "Do init specific for this widget toolkit"
  # replace Tkinter basewidget init, with the one not calling tcl interpreter
  basewidget_original_init = Tkinter.BaseWidget.__init__
  Tkinter.BaseWidget.__init__ = _basewidget_new_init
  toplevel_original_title = Tkinter.Wm.title
  Tkinter.Wm.title = _dummy_call
  # complete the python widget tree, if necessary
  complete_widget_tree(toplevel_widgets()[0])
  # restore original basewidget init
  Tkinter.BaseWidget.__init__ = basewidget_original_init
  Tkinter.Wm.title = toplevel_original_title
  # mapping between the real widget and the wal widget
  core['avccd'].widget_map = { \
    Tkinter.Button:	core['Button'],\
    Tkinter.Checkbutton:core['ToggleButton'], \
    Tkinter.Entry:	core['Entry'], \
    Tkinter.Label:	core['Label'], \
    Tkinter.Radiobutton:core['RadioButton'], \
    Tkinter.Scale:	core['Slider'], \
    Tkinter.Spinbox:	core['SpinButton'],
    Tkinter.Text:	core['TextView']}
  # get toolkit version
  core['avccd'].toolkit_version = Tkinter.__version__


def widget_children(widget):
  "Return the list of all children of the widget"
  return widget.children.values()

def widget_name(widget):
  """
  Return the widget name. Try first to get avc_name attribute. If this
  fails, get Tk widget name keeping the last part only.
  """
  try:
    return widget.avc_name
  except:
    return str(widget).split('.')[-1]

def timer(function,period):
  "Call given function, reschedule it after return"
  function()
  return toplevel_widgets()[0].after(int(period * 1000.0),
    timer,function,period)


#### WIDGETS ABSTRACTION LAYER (widget toolkit side)

class Widget:
  "Tk Widget Abstraction Layer abstract class"

  def connect_delete(self,widget,delete_method):
    "Connect widget delte method to destroy event"
    widget.bind("<Destroy>",delete_method)


class ListTreeView(Widget):
  "Tk has no list view and tree view support"
  pass


class Button(Widget):
  "Tk Button widget abstractor"

  def __init__(self):

    # create button press status variable
    self.widget.value = False

    # connect relevant signals
    self.widget.bind("<ButtonPress-1>",
      lambda dummy: self.connection.coget.__set__(
        '',True,self.widget,self.connection))
    self.widget.bind("<ButtonRelease-1>",
      lambda dummy: self.connection.coget.__set__(
        '',False,self.widget,self.connection))


  def read(self):
    "Get button status"
    return self.widget.value

  def write(self,value):
    "Set button status"
    self.widget.value = value


class Calendar(Widget):
  "Widget not in tk"

  def __init__(self):
      pass


class ComboBox(Widget):
  "Tk no combo box support"
  pass


class ColorChooser(Widget):
  "Widget not in tk"

  def __init__(self):
      pass


class Entry(Widget):
  "Tk Entry widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.bind("<Return>",self.value_changed)

  def read(self):
    "Get text from Entry"
    return self.widget.get()
    
  def write(self,value):
    "Set text into Entry"
    self.widget.delete(0,Tkinter.END)
    self.widget.insert(0,str(value))

 
class Label(Widget):
  "Tk Label widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get value into Label"
    return self.widget.cget('text')

  def write(self,value):
    "Set text into Label"
    self.widget.config(text=value)


class ListView(ListTreeView):
  "Tk has no list view support"
  pass


class ProgressBar(Widget):
  "Tk no prograss bar support"
  pass

class RadioButton(Widget):
  "Tk RadioButton widget abstractor"

  def __init__(self):

    # if not yet done, get existing (by default) variable with pressed
    # button index.
    if not hasattr(self.connection,'active_index_name'):
      self.connection.active_index_name = str(self.widget.cget("variable"))
    
    # connect relevant signals
    self.widget.bind("<ButtonRelease-1>",self.value_changed)


  def read(self):
    "Get index of activated button"
    return int(str(self.widget.getvar(self.connection.active_index_name)))

  def write(self,value):
    "Set activate button indexed by value"
    self.widget.setvar(self.connection.active_index_name,value)


class Slider(Widget):
  "Tk Scale widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.config(command=self.value_changed)
 
  def read(self):
    "Get Slider value"
    return self.widget.get()

  def write(self,value):
    "Set Slider value"
    self.widget.set(str(value))


class SpinButton(Widget):
  "Tk SpinButton widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.bind("<Return>",self.value_changed)
    self.widget.config(command=self.value_changed)

  def read(self):
    "Get spin button value"
    return self.widget.get()

  def write(self,value):
    "Set spin button value"
    self.widget.delete(0,Tkinter.END)
    self.widget.insert(0,str(value))
 

class StatusBar(Widget):
  "Tk no status bar support"
  pass


class TextView(Widget):
  "Tk TextView widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.bind("<Return>",self.value_changed)

  def read(self):
    "Get text from TextView"
    return self.widget.get("1.0",Tkinter.END)
    
  def write(self,value):
    "Set text into TextView"
    self.widget.delete("1.0",Tkinter.END)
    self.widget.insert("1.0",str(value))


class ToggleButton(Widget):
  "Tk ToggleButton widget abstractor"

  def __init__(self):

    # get and save button value variable name
    self.value_name = str(self.widget.cget('variable'))

    # connect relevant signals
    self.widget.bind("<ButtonRelease-1>",self.value_changed)


  def read(self):
    "Get button status"
    return bool(int(self.widget.getvar(self.value_name)))

  def write(self,value):
    "Set button status"
    self.widget.setvar(self.value_name,int(value))


class TreeView(ListTreeView):
  "Tk has no tree view support"
  pass

#### END

