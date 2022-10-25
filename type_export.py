#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022      Christopher Horn
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
TypeExportTool
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import json
import os

# -------------------------------------------------------------------------
#
# Gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as configman
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.plug import tool

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# -------------------------------------------------------------------------
#
# TypeExportTool
#
# -------------------------------------------------------------------------
class TypeExportTool(tool.Tool, ManagedWindow):
    """
    Tool to export all the custom types in the database.
    """

    def __init__(self, dbstate, user, options_class, name, callback=None):
        self.title = _("Type Export Tool")
        self.dbstate = dbstate
        ManagedWindow.__init__(self, user.uistate, [], self.__class__)
        tool.Tool.__init__(self, dbstate, options_class, name)

        filename = self.get_file_name()
        if filename:
            data = self.get_type_data()
            with open(filename, "w", encoding="utf-8") as file_handle:
                file_handle.write(json.dumps(data, indent=4))

    def build_menu_names(self, _dummy_obj):
        """
        Return menu name.
        """
        return (self.title, None)

    def get_file_name(self):
        """
        Get the name of the file to save the types to.
        """
        export_dialog = Gtk.FileChooserDialog(
            title="Type Export File",
            transient_for=self.uistate.window,
            action=Gtk.FileChooserAction.SAVE,
        )
        export_dialog.add_buttons(
            _("_Cancel"),
            Gtk.ResponseType.CANCEL,
            _("Save"),
            Gtk.ResponseType.OK,
        )
        self.set_window(export_dialog, None, self.title)
        self.setup_configs("interface.type-export-dialog", 780, 630)

        file_filter = Gtk.FileFilter()
        file_filter.add_pattern("*.%s" % icase("json"))
        export_dialog.add_filter(file_filter)

        export_dialog.set_current_folder(
            configman.get("paths.recent-export-dir")
        )
        export_dialog.set_current_name(
            "gramps_type_export_%s.json"
            % self.dbstate.db.get_dbname().replace(" ", "_")
        )
        while True:
            response = export_dialog.run()
            if response == Gtk.ResponseType.CANCEL:
                self.close()
                return None
            if response == Gtk.ResponseType.DELETE_EVENT:
                self.close()
                return None
            if response == Gtk.ResponseType.OK:
                filename = export_dialog.get_filename()
                if check_errors(filename):
                    continue
                self.close()
                return filename

    def get_type_data(self):
        """
        Gather the type data.
        """
        db = self.dbstate.db
        return {
            "type_export_version": 1.0,
            "individual_attributes": list(db.individual_attributes),
            "name_types": list(db.name_types),
            "origin_types": list(db.origin_types),
            "family_attributes": list(db.family_attributes),
            "family_rel_types": list(db.family_rel_types),
            "child_ref_types": list(db.child_ref_types),
            "event_attributes": list(db.event_attributes),
            "event_names": list(db.event_names),
            "event_role_names": list(db.event_role_names),
            "media_attributes": list(db.media_attributes),
            "note_types": list(db.note_types),
            "place_types": list(db.place_types),
            "repository_types": list(db.repository_types),
            "source_attributes": list(db.source_attributes),
            "source_media_types": list(db.source_media_types),
            "url_types": list(db.url_types),
        }


def icase(ext):
    """
    Return a glob reresenting a case insensitive file extension.
    """
    return "".join(["[{}{}]".format(s.lower(), s.upper()) for s in ext])


def check_errors(filename):
    """
    Perform some sanity checks and return True if any found.
    """
    if not isinstance(filename, str):
        return True

    filename = os.path.normpath(os.path.abspath(filename))
    if len(filename) == 0:
        return True

    return False


# ------------------------------------------------------------------------
#
# TypeExportToolOptions
#
# ------------------------------------------------------------------------
class TypeExportToolOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
