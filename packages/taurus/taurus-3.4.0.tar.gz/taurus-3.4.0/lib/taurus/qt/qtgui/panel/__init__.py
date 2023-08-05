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
#############################################################################

"""This package contains a collection of taurus Qt widgets representing various
panels like forms or panels to be inserted in dialogs"""

__docformat__ = 'restructuredtext'

from .qrawdatachooser import *
from .qdataexportdialog import *
from .taurusmessagepanel import *
from .taurusinputpanel import *
from .taurusattributechooser import TaurusAttributeChooser as TaurusAttributeChooserOLD
from .taurusmodelchooser import *
TaurusAttributeChooser = TaurusModelChooser #for backwards compatibility
from .taurusvalue import *
from .taurusform import *
from .taurusmodellist import *
from .taurusconfigeditor import *
from .qdoublelist import *
from .taurusdevicepanel import *

