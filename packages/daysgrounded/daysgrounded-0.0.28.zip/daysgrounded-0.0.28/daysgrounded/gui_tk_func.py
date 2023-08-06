#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2009-2015 Joao Carlos Roseta Matos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""GUI allows setting the grounded days per child or auto update."""

# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime as dt
import sys

import localization as lcl
import shared as shrd
import utils

if utils.PY < 3:
    import Tkinter as tk
    import ttk as tk_ttk
    import tkMessageBox as tk_msg_box
else:
    import tkinter as tk
    import tkinter.ttk as tk_ttk
    import tkinter.messagebox as tk_msg_box


prev_child = child = childs = last_upd = None


def start():
    """Print banner, read/create data & log file and start GUI."""
    global prev_child, child, childs, last_upd

    def plus_btn(*args):
        """Plus button was pressed. Update days_var."""
        if int(days_var.get()) < 0:
            days_var.set(0)
        else:
            days_var.set(min(shrd.MAX_DAYS, int(days_var.get()) + 1))

    def minus_btn(*args):
        """Minus button was pressed. Update days_var."""
        if int(days_var.get()) > shrd.MAX_DAYS:
            days_var.set(shrd.MAX_DAYS)
        else:
            days_var.set(max(0, int(days_var.get()) - 1))

    def days_scale_chg(*args):
        """Days scale changed. Update. Update days_var."""
        days_var.set(int(float(days_var.get())))  # fix increment to integer

    def childs_combo_chg(*args):
        """
        Child selection changed.
        Save current child's grounded days and update all fields with new
        child's.
        """
        global child, prev_child

        try:
            int(days_var.get())
        except ValueError:  # as err:
        #except ValueError:  # , err:
            days_var.set(0)

        if 0 <= int(days_var.get()) <= shrd.MAX_DAYS:
            childs[prev_child] = int(days_var.get())
            child = prev_child = childs_combo.get()
            days_var.set(childs[child])
        else:
            childs_combo.set(prev_child)
            tk_msg_box.showwarning(lcl.WARNING, lcl.DAYS_RANGE +
                                                shrd.MAX_DAYS_STR)

    def set_upd_btn(upd):
        """Set or update selected child's grounded days."""
        global last_upd

        try:
            int(days_var.get())
        except ValueError:
            days_var.set(0)

        if 0 <= int(days_var.get()) <= shrd.MAX_DAYS:
            childs[childs_combo.get()] = int(days_var.get())
            if upd:
                last_upd = shrd.auto_upd_datafile(childs, last_upd)
            else:
                last_upd = dt.date.today()
                shrd.update_file(childs, last_upd)
            last_upd_var.set(value=str(last_upd))
        else:
            tk_msg_box.showwarning(lcl.WARNING, lcl.DAYS_RANGE +
                                                shrd.MAX_DAYS_STR)

    def confirm_exit():
        """Confirm exit from program."""
        if tk_msg_box.askokcancel(lcl.EXIT, lcl.CONFIRM_EXIT):
            root.destroy()
            sys.exit(0)  # ToDo: other return codes

    def digits_only(up_down, idx, value, prev_val, char, val_type, source,
                    widget):
        """Only allow digits in source field."""
        return char in '0123456789' and len(value) <= len(shrd.MAX_DAYS_STR)

    def center(window):
        """Center window."""
        window.update_idletasks()
        width = window.winfo_width()
        frm_width = window.winfo_rootx() - window.winfo_x()
        win_width = width + 2 * frm_width
        height = window.winfo_height()
        titlebar_height = window.winfo_rooty() - window.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = window.winfo_screenwidth() // 2 - win_width // 2
        y = window.winfo_screenheight() // 2 - win_height // 2
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        if window.attributes('-alpha') == 0:
            window.attributes('-alpha', 1.0)
        window.deiconify()

    def show_help(*args):
        """Show help message."""
        tk_msg_box.showinfo(lcl.HELP, shrd.usage())

    print(shrd.banner())
    childs, last_upd = shrd.open_create_datafile()

    root = tk.Tk()
    root.withdraw()
    win = tk.Toplevel(root)

    # for exit confirmation
    win.protocol('WM_DELETE_WINDOW', confirm_exit)

    win.title(lcl.DAYS_GROUNDED)

    # not resizable
    win.resizable(False, False)

    # resizable (limits)
    #win.minsize(250, 125)
    #win.maxsize(500, 250)

    # needed by center function?
    #win.attributes('-alpha', 0.0)

    win.bind('<F1>', show_help)
    win.bind('+', plus_btn)
    win.bind('-', minus_btn)

    # menu
    win.option_add('*tearOff', False)
    menubar = tk.Menu(win)
    win.config(menu=menubar)
    filemenu = tk.Menu(menubar)
    helpmenu = tk.Menu(menubar)

    menubar.add_cascade(label=lcl.FILE, menu=filemenu, underline=0)
    menubar.add_cascade(label=lcl.HELP, menu=helpmenu, underline=0)

    filemenu.add_command(label=lcl.EXIT, underline=0, command=confirm_exit)

    helpmenu.add_command(label=lcl.HELP, underline=0, command=show_help,
                         accelerator='F1')
    helpmenu.add_separator()
    helpmenu.add_command(label=lcl.ABOUT, underline=0, state='disabled')

    # ToDo: log menu item
    ## filemenu.add_separator()
    ## check = StringVar(value=1)
    ## filemenu.add_checkbutton(label='Log', variable=check, onvalue=1,
    ##                          offvalue=0)

    frame = tk_ttk.Frame(win, padding='3 3 3 3')
    frame.grid(column=0, row=0, sticky='WNES')

    # if the main window is resized, the frame should expand
    #frame.columnconfigure(0, weight=1)
    #frame.rowconfigure(0, weight=1)

    # must convert to list for Python 3 compatibility
    prev_child = child = list(childs.keys())[0]

    child_lbl = tk.StringVar(value=lcl.CHILD)
    last_upd_lbl = tk.StringVar(value=lcl.LAST_UPDATE)

    days_var = tk.StringVar(value=childs[child])
    last_upd_var = tk.StringVar(value=str(last_upd))

    # 1st row
    tk_ttk.Button(frame, text='+', command=plus_btn).grid(column=3, row=1)
    days_scale = tk_ttk.Scale(frame, orient=tk.VERTICAL, length=100,
                              from_=shrd.MAX_DAYS, to=0,
                              command=days_scale_chg, variable=days_var)
    days_scale.grid(column=4, row=1, rowspan=3)

    # 2nd row
    tk_ttk.Label(frame, textvariable=child_lbl).grid(column=1, row=2)
    childs_combo = tk_ttk.Combobox(frame, state='readonly',  # width=10,
                                   values=list(childs.keys()))
    childs_combo.grid(column=2, row=2)
    childs_combo.set(child)
    childs_combo.bind('<<ComboboxSelected>>', childs_combo_chg)

    # validate command, used below by some widgets
    vcmd = (win.register(digits_only),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

    days_entry = tk_ttk.Entry(frame, width=len(shrd.MAX_DAYS_STR) + 1,
                              justify=tk.RIGHT, textvariable=days_var,
                              validate='key', validatecommand=vcmd)
    days_entry.grid(column=3, row=2)  # , sticky='WE')  # for expanding
    tk.Spinbox(frame, from_=0, to=shrd.MAX_DAYS,
               width=len(shrd.MAX_DAYS_STR) + 1, justify=tk.RIGHT,
               textvariable=days_var, validate='key',
               validatecommand=vcmd).grid(column=5, row=2)

    # 3rd row
    tk_ttk.Button(frame, text='-', command=minus_btn).grid(column=3, row=3)

    # 4th row
    # lambda is necessary so that the function is called on button creation
    tk_ttk.Button(frame, text=lcl.UPDATE,
                  command=lambda: set_upd_btn(upd=True)).grid(column=1, row=4)
    tk_ttk.Label(frame, textvariable=last_upd_lbl).grid(column=2, row=4,
                                                        sticky='E')
    tk_ttk.Label(frame, textvariable=last_upd_var).grid(column=3, row=4,
                                                        sticky='W')
    tk_ttk.Button(frame, text=lcl.SET,
                  command=lambda: set_upd_btn(upd=False)).grid(column=4, row=4,
                                                               columnspan=2)
    # remove if windows is non resizable
    #tk_ttk.Sizegrip(frame).grid(column=999, row=999, sticky=(E,S))

    # padding around all widgets
    for widget in frame.winfo_children():
        widget.grid_configure(padx=5, pady=5)

    days_entry.focus()

    # center window
    center(win)

    root.mainloop()


if __name__ == '__main__':
    #import doctest
    #doctest.testmod(verbose=True)
    pass
