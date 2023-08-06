#!/bin/python3

import os.path
import sys

# Check if we are working in the source tree or from the installed
# package and mangle the python path accordingly
realPath = os.path.realpath(sys.argv[0])  # If this file is run from a symlink, it needs to follow the symlink
if os.path.dirname(realPath) != ".":
    if realPath[0] == "/":
        fullPath = os.path.dirname(realPath)
    else:
        fullPath = os.getcwd() + "/" + os.path.dirname(realPath)
else:
    fullPath = os.getcwd()
sys.path.insert(0, os.path.dirname(fullPath))


from gi.repository import Gtk, Gio, Gdk
from budget.window import Window
from budget.data import Data

class main():

    def __init__(self):
        self.data = Data()
        self.data.import_data()
        self.win = Window(self.data)
        self.win.connect("delete-event", Gtk.main_quit)
        self.win.show_all()
    
        self.win.transactions.month_year_visible(True)
        self.win.transactions.range_visible(False)

        for i in range(0, len(self.win.transactions.menuListBox)):
            if self.win.transactions.editable_category(i):
                self.win.transactions.category_view_mode(i)
        
        self.win.connect('key-press-event', self.on_key_function)
        self.win.set_icon_name("budget.png")
        Gtk.main()

    def on_key_function(self, widget, event):
        # If ctrl is pressed
        if Gdk.ModifierType.CONTROL_MASK & event.state:
            # ctrl+q to quit
            if event.keyval == 113:
                Gtk.main_quit()
        # If ctrl is pressed
        if Gdk.ModifierType.MOD1_MASK & event.state:
            # alt+1
            if event.keyval == 49:
                self.win.notebook.set_current_page(0)
            # alt+2
            if event.keyval == 50:
                self.win.notebook.set_current_page(1)
            # alt+3
            #if event.keyval == 51:
            #    self.win.notebook.set_current_page(2)

if __name__=='__main__':
    main()
