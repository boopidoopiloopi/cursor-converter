#!/usr/bin/env python3
import sys
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ui_window import AppWindow

def main():
    app = AppWindow()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main()
