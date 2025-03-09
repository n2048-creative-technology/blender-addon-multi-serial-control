# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Serial Controller",
    "author": "Mauricio van der Maesen de Sombreff",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View3D",
    "category": "N2048",
}

from . import properties, operators, ui_list, panels, serial_manager

def register():
    properties.register()
    operators.register()
    ui_list.register()
    panels.register()
    serial_manager.register()

def unregister():
    panels.unregister()
    ui_list.unregister()
    operators.unregister()
    properties.unregister()
    serial_manager.unregister()

if __name__ == "__main__":
    register()