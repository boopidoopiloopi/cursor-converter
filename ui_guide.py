#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from guide_data import get_current_guide_data

def create_manual_content_widget():
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_hexpand(True)
    scrolled.set_vexpand(True)
    scrolled.set_min_content_height(350)

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.NONE)

    data = get_current_guide_data()
    for name, desc in data.items():
        row = Gtk.ListBoxRow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_property("margin", 8)

        lbl_title = Gtk.Label()
        lbl_title.set_markup(f"<b>{name}</b>")
        lbl_title.set_xalign(0)

        lbl_desc = Gtk.Label(label=desc)
        lbl_desc.set_xalign(0)
        lbl_desc.set_line_wrap(True)

        vbox.pack_start(lbl_title, False, False, 0)
        vbox.pack_start(lbl_desc, False, False, 0)
        row.add(vbox)
        listbox.add(row)

    scrolled.add(listbox)
    return scrolled
