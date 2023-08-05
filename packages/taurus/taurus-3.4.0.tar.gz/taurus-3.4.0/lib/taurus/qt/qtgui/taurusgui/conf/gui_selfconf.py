#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
###########################################################################

'''An example of usage of TaurusGui in which the specific GUI is set up both 
programmatically and using the same file as the configuration file.
This can be launched directly as a stand-alone python script'''


GUI_NAME = 'MyGui' 

if __name__ == '__main__':
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.taurusgui import TaurusGui
    from taurus.external.qt import Qt
    app = TaurusApplication()
    gui = TaurusGui(confname=__file__)
    panel = Qt.QWidget()
    gui.createPanel(panel, 'Foo')
    gui.show()
    app.exec_()