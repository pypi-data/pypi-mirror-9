# -*- coding: utf-8 -*-
"""
    PyScanFCS

    Module edclasses
    Contains classes that we edited.
    Makes these classes more useful for us.

    (C) 2012 Paul Müller

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License 
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import numpy as np
from wx.lib.agw import floatspin        # Float numbers in spin fields
import wx 

class FloatSpin(floatspin.FloatSpin):
    def __init__(self, parent, digits=10, increment=.01, value=1.0):
        floatspin.FloatSpin.__init__(self, parent, digits=digits,
                                     increment = increment, value = value)
        self.Bind(wx.EVT_SPINCTRL, self.increment)
        #self.Bind(wx.EVT_SPIN, self.increment)
        #self.increment()

    def increment(self, event=None):
        # Find significant digit
        # and use it as the new increment
        x = self.GetValue()
        if x == 0:
            incre = 0.1
        else:
            digit = int(np.ceil(np.log10(abs(x)))) - 2
            incre = 10**digit
        self.SetIncrement(incre)


class ChoicesDialog(wx.Dialog):
    def __init__(self, parent, dropdownlist, title, text):
        # parent is main frame
        self.parent = parent

        super(ChoicesDialog, self).__init__(parent=parent, 
            title=title)
        # Get the window positioning correctly
        #pos = self.parent.GetPosition()
        #pos = (pos[0]+100, pos[1]+100)
        #wx.Frame.__init__(self, parent=parent, title=title,
        #         pos=pos, style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

        #self.Filename = None
        ## Controls
        panel = wx.Panel(self)

        # text1
        textopen = wx.StaticText(panel, label=text)
        btnok = wx.Button(panel, wx.ID_OK)
        btnabort = wx.Button(panel, wx.ID_CANCEL)

        # Dropdown
        self.dropdown = wx.ComboBox(panel, -1, "", (15, 30),
              wx.DefaultSize, dropdownlist, wx.CB_DROPDOWN|wx.CB_READONLY)
        self.dropdown.SetSelection(0)
        # Bindings
        self.Bind(wx.EVT_BUTTON, self.OnOK, btnok)
        self.Bind(wx.EVT_BUTTON, self.OnAbort, btnabort)

        # Sizers
        topSizer = wx.BoxSizer(wx.VERTICAL)

        topSizer.Add(textopen)
        topSizer.Add(self.dropdown)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(btnok)
        btnSizer.Add(btnabort)

        topSizer.Add(btnSizer)

        panel.SetSizer(topSizer)
        topSizer.Fit(self)
        self.Show(True)

    def OnOK(self, event=None):
        self.SelcetedID = self.dropdown.GetSelection()
        self.EndModal(wx.ID_OK)

    def OnAbort(self, event=None):
        self.EndModal(wx.ID_CANCEL)

