#!/usr/bin/python

import gtk

window = gtk.Window()
window.connect('destroy',gtk.main_quit)

calendar = gtk.Calendar()
window.add(calendar)

print '1 ', calendar.get_date()
calendar.select_day(1)
print '2 ', calendar.get_date()
calendar.select_month(2,2000)
print '3 ', calendar.get_date()

window.show_all()

gtk.main()
