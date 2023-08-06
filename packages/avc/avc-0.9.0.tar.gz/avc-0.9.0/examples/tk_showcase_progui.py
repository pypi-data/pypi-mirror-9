#!/usr/bin/python
# .+
#
# .identifier :	$Id: example2.py,v 1.1 2006/11/20 17:31:56 fabrizio Exp $
# .context    : Application View Controller
# .title      : A table of all supported widget/control type conbinations (Tk)
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Revello - Italy
# .creation   :	19-Nov-2006
# .copyright  : (c) 2006 Fabrizio Pollastri.
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


from Tkinter import * 			# Tk interface

from avc import *			# AVC

INCREMENTER_PERIOD = 0.333		# seconds


class Example(AVC):
  """
  A table of all supported widget/control type conbinations
  """

  def __init__(self):

    ## create GUI
    self.root = Tk()
    self.root.title('AVC Tk showcase example')

    # row 0: titles
    Label(self.root,text='Control Type').grid(row=0)
    Label(self.root,text='Widgets').grid(row=0,column=1,columnspan=3)
    Label(self.root,text='Control Value').grid(row=0,column=4)

    # row 1: button/boolean variable
    Label(self.root,text='boolean').grid(row=1,rowspan=2)
    button1 = Button(self.root,text='button',name='boolean1__button1')
    button1.grid(row=1,column=1,columnspan=3)
    label1 = Label(self.root,text='boolean1',name='boolean1__label1')
    label1.grid(row=1,column=4)
    
    # row 2: checkbutton/boolean variable 
    button2 = Checkbutton(self.root,text='button',name='boolean2__button2')
    button2.grid(row=2,column=1,columnspan=3)
    label2 = Label(self.root,text='boolean2',name='boolean2__label2')
    label2.grid(row=2,column=4)

    # row 3: triple radio button/index variable (integer)
    Label(self.root,text='index').grid(row=3)
    radiobutton0 = Radiobutton(self.root,text='radiobutton0',value=0,
      name='radio__radiobutton0')
    radiobutton1 = Radiobutton(self.root,text='radiobutton1',value=1,
      name='radio__radiobutton1')
    radiobutton2 = Radiobutton(self.root,text='radiobutton2',value=2,
      name='radio__radiobutton2')
    radiobutton0.grid(row=3,column=1)
    radiobutton1.grid(row=3,column=2)
    radiobutton2.grid(row=3,column=3)
    label3 = Label(self.root,text='index',name='radio__label3')
    label3.grid(row=3,column=4)

    # row 4: spin button/text entry/integer variable
    Label(self.root,text='integer').grid(row=4)
    spinbox1 = Spinbox(self.root,name='integer__spinbox1',increment=1,
      to=100)
    spinbox1.grid(row=4,column=1)
    entry1 = Entry(self.root,textvariable=StringVar(),name='integer__entry1')
    entry1.grid(row=4,column=2,columnspan=2)
    label4 = Label(self.root,text='integer',name='integer__label4')
    label4.grid(row=4,column=4)

    # row 5: spin button/text entry/float variable
    Label(self.root,text='float').grid(row=5)
    spinbox2 = Spinbox(self.root,name='float__spinbox2',increment=1.0,
      to=100.0)
    spinbox2.grid(row=5,column=1)
    entry2 = Entry(self.root,textvariable=StringVar(),name='float__entry2')
    entry2.grid(row=5,column=2,columnspan=2)
    label5 = Label(self.root,text='float',name='float__label5')
    label5.grid(row=5,column=4)

    # row 6: entry/string variable
    Label(self.root,text='string').grid(row=6)
    entry3 = Entry(self.root,textvariable=StringVar(),name='string__entry3')
    entry3.grid(row=6,column=1,columnspan=3)
    label6 = Label(self.root,text='string',name='string__label6')
    label6.grid(row=6,column=4)

    # the control variables
    self.boolean1 = False
    self.boolean2 = False
    self.radio = 0
    self.integer = 0
    self.float = 0.0
    self.string = ''

    # start variables incrementer
    increment = self.incrementer()
    self.timer_function = increment.next
    self.root.after(int(INCREMENTER_PERIOD * 1000.0),self.timer_wrap)


  def timer_wrap(self):
    "Call given function, reschedule it after return"
    self.timer_function()
    self.root.after(int(INCREMENTER_PERIOD * 1000.0),self.timer_wrap)


  def incrementer(self):
    """
    Booleans are toggled, radio button index is rotated from first to last,
    integer is incremented by 1, float by 0.5, string is appended a char
    until maxlen when string is cleared. Return True to keep timer alive.
    """
    while True:
      self.boolean1 = not self.boolean1
      yield True

      self.boolean2 = not self.boolean2
      yield True

      if self.radio == 2:
        self.radio = 0
      else:
        self.radio += 1
      yield True

      self.integer += 1
      yield True

      self.float += 0.5
      yield True

      if len(self.string) >= 20:
        self.string = 'A'
      else:
        self.string += 'A'
      yield True


#### MAIN

example = Example()			# instantiate the application
example.avc_init()			# connect widgets with variables
mainloop()				# run Tk event loop until quit

#### END

