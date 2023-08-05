#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2013 CELLS / ALBA Synchrotron, Bellaterra, Spain
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
#############################################################################

"""This module provides some basic usable widgets based on TaurusReadWriteSwitcher
"""

__all__ = ["TaurusLabelEditRW", "TaurusLabelEditRW"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.display import TaurusLabel, TaurusBoolLed
from taurus.qt.qtgui.input import TaurusValueLineEdit, TaurusValueCheckBox
from abstractswitcher import TaurusReadWriteSwitcher

class TaurusLabelEditRW(TaurusReadWriteSwitcher):
    '''A Switcher combining a TaurusLabel and a TaurusValueLineEdit''' 
    readWClass = TaurusLabel
    writeWClass = TaurusValueLineEdit 
        
class TaurusBoolRW(TaurusReadWriteSwitcher):
    '''A Switcher combining a TaurusBoolLed and a TaurusValueCheckBox'''
    readWClass = TaurusBoolLed
    writeWClass = TaurusValueCheckBox
    
    def setWriteWidget(self, widget):
        widget.setShowText(False)
        TaurusReadWriteSwitcher.setWriteWidget(self, widget)
        
def _demo():
    '''demo of integrability in a form'''
    import sys
    from taurus.qt.qtgui.panel import TaurusForm
    from taurus.qt.qtgui.application import TaurusApplication
    
    app = TaurusApplication()
    
    f = TaurusForm()
    f.model = ['sys/tg_test/1/long_scalar', 'sys/tg_test/1/long_scalar',
               'sys/tg_test/1/boolean_scalar', 'sys/tg_test/1/boolean_scalar']
    
    f[0].setReadWidgetClass(TaurusLabelEditRW)
    f[0].setWriteWidgetClass(None)
    f[2].setReadWidgetClass(TaurusBoolRW)
    f[2].setWriteWidgetClass(None)
    
    
    f.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    _demo()
    