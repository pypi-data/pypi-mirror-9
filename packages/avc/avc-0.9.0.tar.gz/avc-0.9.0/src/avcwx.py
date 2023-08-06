"""
# .+
# .context      : Application View Controller
# .title        : AVC wx bindings
# .kind         : python source
# .author       : Fabrizio Pollastri
# .site         : Torino - Italy
# .creation     : 23-Nov-2007
# .copyright    : (c) 2007-2008 Fabrizio Pollastri
# .license      : GNU General Public License (see below)
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
"""

#### IMPORT REQUIRED MODULES

import wx               # wx tool kit bindings
import wx.calendar      # wx calendar module

import string           # string operations


#### GENERAL ABSTRACTION METHODS

def toplevel_widgets():
  "Return the list of all top level widgets"
  return [wx.GetApp().GetTopWindow()]

def init(core):
  "Do init specific to this widget toolkit"
  # mapping between the real widget and the wal widget
  core['avccd'].widget_map = { \
    wx.BitmapButton:    core['Button'], \
    wx.Button:            core['Button'], \
    wx.calendar.CalendarCtrl:core['Calendar'], \
    wx.CheckBox:        core['ToggleButton'], \
    wx.ColourPickerCtrl:core['ColorChooser'],\
    wx.ComboBox:        core['ComboBox'],\
    wx.Choice:            core['ComboBox'],\
    wx.Gauge:           core['ProgressBar'], \
    wx.ListCtrl:        core['ListView'], \
    wx.RadioBox:        core['RadioButton'], \
    wx.Slider:          core['Slider'], \
    wx.SpinCtrl:        core['SpinButton'], \
    wx.StaticText:      core['Label'], \
    wx.StatusBar:        core['StatusBar'],
    wx.TextCtrl:        core['Entry'],
    wx.ToggleButton:    core['ToggleButton'], \
    wx.TreeCtrl:        core['TreeView']}
  # get toolkit version
  core['avccd'].toolkit_version = wx.VERSION_STRING

def widget_children(widget):
  "Return the list of all children of the widget"
  # Widgets that are not a subclass of gtk.Container have no children.
  if isinstance(widget, wx.Window):
    return widget.GetChildren()
  else:
    return []

def widget_name(widget):
  "Return the widget name"
  return widget.GetName()

def timer(function, period):
  "Create and start a timer calling 'function' every 'period' time"
  first_toplevel = toplevel_widgets()[0]
  timer = wx.Timer(first_toplevel, wx.NewId())
  first_toplevel.Bind(wx.EVT_TIMER, lambda event: function(), timer)
  timer.Start(int(period * 1000.0), oneShot=False)
  return timer


class Error(Exception):
  "A generic error exception"
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


#### WIDGETS ABSTRACTION LAYER (widget toolkit side)

class Widget:
  "wx Widget Abstraction Layer abstract class"

  def delete_method_filter(self, event):
    "Ignore destroy events not coming from current widget"
    if self.widget.GetId() == event.GetId():
      self.delete_method()

  def connect_delete(self, widget, delete_method):
    "Connect widget delete method to window destroy event"
    self.delete_method = delete_method
    #widget.Bind(wx.EVT_WINDOW_DESTROY,delete_method)
    widget.Bind(wx.EVT_WINDOW_DESTROY, self.delete_method_filter)


class ListTreeView(Widget):
  "Support to ListView and TreeView abstractors"

  def __init__(self):
    "Init operations common to ListView and TreeView"
    pass


class Button(Widget):
  "wx Button widget abstractor"

  def __init__(self):
    # create button press status variable
    self.widget.value = False
    # connect relevant signals
    self.widget.Bind(wx.EVT_LEFT_DOWN,
      lambda event: wx.CallAfter(
      lambda: self.connection.coget.__set__(
        '',True,self.widget,self.connection))
      or event.Skip())
    self.widget.Bind(wx.EVT_LEFT_UP,
      lambda event: wx.CallAfter(
      lambda: self.connection.coget.__set__(
        '',False,self.widget,self.connection))
      or event.Skip())

  def read(self):
    "Get button status"
    return self.widget.value

  def write(self, value):
    "Set button status"
    self.widget.value = value


class Calendar(Widget):
  "wx Calendar widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.value_changed)

  def read(self):
    "Get selected date"
    date = self.widget.GetDate()
    # make month number starting from 1
    return (date.GetYear(), date.GetMonth()+1, date.GetDay())

  def write(self, value):
    "Set selected date"
    # change date from yyyymmdd to dd mm-1 yyyy, required by Set
    self.widget.SetDate(wx.DateTime().Set(value[2], value[1]-1, value[0]))


class ColorChooser(Widget):
  "wx ColorChooser widget abstractor"

  def __init__(self):
    # color storage
    self.color = wx.Color()
    # connect relevant signals
    self.widget.Bind(wx.EVT_COLOURPICKER_CHANGED, self.value_changed)

  def read(self):
    "Get selected color"
    color = self.widget.GetColour().Get(True)
    return tuple([float(component / 255.) for component in color])

  def write(self, value):
    "Set selected color"
    self.color.Set(*[int(component * 255) for component in value])
    self.widget.SetColour(self.color)


class ComboBox(Widget):
  "wx ComboBox widget abstractor"

  def __init__(self):
    # connect relevant signals
    if self.widget.__class__ == wx.ComboBox:
      event_type = wx.EVT_COMBOBOX
    else:
      event_type = wx.EVT_CHOICE
    self.widget.Bind(event_type, self.value_changed)

  def read(self):
    "Get index of selected item"
    return self.widget.GetSelection()

  def write(self, value):
    "Set selected item by its index value"
    self.widget.SetSelection(value)


class Entry(Widget):
  "wx Entry widget abstractor"

  def __init__(self):
    # create entry text value variable
    self.widget.value =  self.widget.GetValue()
    # connect relevant signals
    self.widget.Bind(wx.EVT_TEXT, self.value_changed)

  def read(self):
    "Get text from Entry"
    text = self.widget.GetValue()
    # when TextCtrl text is set by program, the event EVT_TEXT is
    # triggered twice: first time with an empty string, second time with
    # the correct value. Substitute first (wrong) value with the old one.
    if text:
      return text
    else:
      return self.widget.value

  def write(self, value):
    "Set text into Entry"
    self.widget.SetValue(str(value))
    self.widget.value = str(value)


class Label(Widget):
  "wx Label widget abstractor"

  def __init__(self):
    pass

  def read(self):
    "Get value from Label"
    return self.widget.GetLabel()

  def write(self, value):
    "Set text into Label"
    self.widget.SetLabel(value)


class ListView(ListTreeView):
  "wx ListView widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.Bind(wx.EVT_LIST_END_LABEL_EDIT,
      lambda event: wx.CallAfter(self.value_changed) or event.Skip())

  def append_column(self, col_num, text):
    "Append a column to the ListView"
    self.widget.InsertColumn(col_num, text)

  def read(self):
    "Get values displayed by widget"
    # get head
    head = [str(self.widget.GetColumn(col_num).GetText()) \
      for col_num in range(self.widget.GetColumnCount())]
    # get data rows
    body = []
    for row_num in range(self.widget.GetItemCount()):
      row = []
      for col_num in range(self.widget.GetColumnCount()):
        try:
          row.append(self.row_types[col_num](
            self.widget.GetItem(row_num,col_num).GetText()))
        except:
          if self.row_types[col_num] == int:
            row.append(0)
          elif self.row_types[col_num] == float:
            row.append(0.0)
      body.append(row)
    # return
    return {'head': head, 'body': body}

  def write(self, value):
    "Set values displayed by widget"
    # set header
    if value.has_key('head'):
      for col_num in range(self.widget.GetColumnCount()):
        col_item = self.widget.GetColumn(col_num)
        col_item.SetText(value['head'][col_num])
        self.widget.SetColumn(col_num, col_item)
    # set data rows
    body = value['body']
    self.widget.DeleteAllItems()
    if type(body[0]) == list:
      for row_num, row in enumerate(body):
        self.widget.InsertStringItem(row_num,'')
        for col_num, item in enumerate(row):
          self.widget.SetStringItem(row_num, col_num, str(item))
    else:
      for row_num, row in enumerate(body):
        self.widget.InsertStringItem(row_num, str(row))


class ProgressBar(Widget):
  "wx ProgressBar widget abstractor"

  def __init__(self):
    self.widget.SetRange(100)

  def read(self):
    "Get progress bar position"
    return self.widget.GetValue() / 100.

  def write(self, value):
    "Set progress bar position"
    # negative values pulse the bar, positive values position the bar.
    if value < 0:
      self.widget.Pulse()
    else:
      self.widget.SetValue(int(round(value * 100)))


class RadioButton(Widget):
  "wx RadioButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    if self.widget.__class__ == wx.RadioBox:
      event_type = wx.EVT_RADIOBOX
    else:
      event_type = wx.EVT_RADIOBUTTON
    self.widget.Bind(event_type, self.value_changed)

  def read(self):
    "Get index of activated button"
    return self.widget.GetSelection()

  def write(self, value):
    "Set activate button indexed by value"
    self.widget.SetSelection(value)


class Slider(Widget):
  "wx Slider widget abstractor"

  def __init__(self):
    # connect relevant signals
    self.widget.Bind(wx.EVT_LEFT_UP,
      lambda event: wx.CallAfter(self.value_changed) or event.Skip())

  def read(self):
    "Get Slider value"
    return self.widget.GetValue()

  def write(self, value):
    "Set Slider value"
    self.widget.SetValue(value)


class SpinButton(Widget):
  "wx SpinButton widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    wx.EVT_SPINCTRL(self.widget, self.widget.GetId(), self.value_changed)


  def read(self):
    "Get spinbutton value"
    return self.widget.GetValue()

  def write(self, value):
    "Set spinbutton value"
    self.widget.SetValue(value)


class StatusBar(Widget):
  "wx StatusBar widget abstractor"

  def __init__(self):
    pass

  def write(self, value):
    "Set StatusBar value (only field 1)"
    self.widget.SetStatusText(value)


class TextView(Widget):
  "wx TextView widget abstractor"

  def __init__(self):
    # connect relevant signals to handlers
    self.widget.get_buffer().connect("changed", self.value_changed)

  def read(self):
    "Get text from TextView"
    textbuf = self.widget.get_buffer()
    return textbuf.get_text(textbuf.get_start_iter(), textbuf.get_end_iter())

  def write(self, value):
    "Set text into TextView"
    self.widget.get_buffer().set_text(str(value))


class ToggleButton(Widget):
  "wx ToggleButton widget abstractor"

  def __init__(self):
    # connect relevant signals
    if self.widget.__class__ == wx.CheckBox:
      event_type = wx.EVT_CHECKBOX
    else:
      event_type = wx.EVT_TOGGLEBUTTON
    self.widget.Bind(event_type, self.value_changed)

  def read(self):
    "Get button status"
    return bool(self.widget.GetValue())

  def write(self, value):
    "Set button status"
    self.widget.SetValue(value)


class TreeView(ListTreeView):
  "wx TreeView widget abstractor"

  def __init__(self):

    # check for allowed control type
    if self.connection.control_value.get('head', None):
      raise error, "%s widget do not support header." \
        % self.widget.__class__.__name__
    key, row = \
        self.connection.control_value.get('body', None).iteritems().next()
    if type(row) == list and not len(row) == 1:
      raise error, \
          "%s widget do not allow data rows with more than one column."\
        % self.widget.__class__.__name__

    # connect relevant signals
    self.widget.Bind(wx.EVT_TREE_END_LABEL_EDIT,
      lambda event: wx.CallAfter(self.value_changed) or event.Skip())

  def append_column(self, col_num, text):
    "wx TreeCtrl has no columns support"
    pass

  def read(self):
    "Get values displayed by widget"
    # get data rows
    body = {}

    def read_node(node_id, node_path):
      """recursive depth first tree data node reader"""
      try:
        body[string.join(map(str, node_path), '.')] = \
          self.row_types[0](self.widget.GetItemText(node_id))
      except:
        if self.row_types[0] == int:
          body[string.join(map(str,node_path),'.')] = [0]
        elif self.row_types[0] == float:
          body[string.join(map(str,node_path),'.')] = [0.0]
      child_id,child = self.widget.GetFirstChild(node_id)
      child_num = 1
      while child_id:
        read_node(child_id,node_path+[child_num])
        child_id,child = self.widget.GetNextChild(node_id,child)
        child_num += 1
    root_id = self.widget.GetRootItem()
    child_id,child = self.widget.GetFirstChild(root_id)
    child_num = 1
    while child_id:
      read_node(child_id,[child_num])
      child_id,child = self.widget.GetNextChild(root_id,child)
      child_num += 1
    # return
    return {'body': body}

  def write_head(self,head):
    "Header not supported"
    pass

  def root_node(self):
    "Clean tree and return the root node"
    self.widget.DeleteAllItems()
    return self.widget.AddRoot('')

  def add_node(self,parent,last_node,current_depth,data):
    "Add current node to the tree"
    return self.widget.AppendItem(parent,str(data))

#### END
