# coding=UTF-8
# ex:ts=4:sw=4:et=on
#  -------------------------------------------------------------------------
#  Copyright (C) 2014 by Mathijs Dumon <mathijs dot dumon at gmail dot com>
#
#  mvc is a framework derived from the original pygtkmvc framework
#  hosted at: <http://sourceforge.net/projects/pygtkmvc/>
#
#  mvc is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2 of the License, or (at your option) any later version.
#
#  mvc is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110, USA.
#  -------------------------------------------------------------------------

import gtk
from .basic import GtkAdapter

class ToggleButtonAdapter(GtkAdapter):
    """
        An adapter for a gtk.ToggleButton widget
    """
    widget_types = ["toggle", "toggle_button"]
    _check_widget_type = gtk.ToggleButton

    _wid_read = GtkAdapter.static_to_class(gtk.ToggleButton.get_active)
    _wid_write = GtkAdapter.static_to_class(gtk.ToggleButton.set_active)
    _signal = "toggled"


    pass # end of class
