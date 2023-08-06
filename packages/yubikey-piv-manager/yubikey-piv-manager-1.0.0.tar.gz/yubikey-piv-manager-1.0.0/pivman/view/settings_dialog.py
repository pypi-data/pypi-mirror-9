# Copyright (c) 2014 Yubico AB
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Additional permission under GNU GPL version 3 section 7
#
# If you modify this program, or any covered work, by linking or
# combining it with the OpenSSL project's OpenSSL library (or a
# modified version of that library), containing parts covered by the
# terms of the OpenSSL or SSLeay licenses, We grant you additional
# permission to convey the resulting work. Corresponding Source for a
# non-source form of such a combination shall include the source code
# for the parts of OpenSSL used as well as that of the covered work.

from PySide import QtGui
from pivman import messages as m
from pivman.view.utils import Dialog
from pivman.storage import settings, SETTINGS


class SettingsDialog(Dialog):

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle(m.settings)

        self._build_ui()

    def _build_ui(self):
        layout = QtGui.QFormLayout(self)

        layout.addRow(self.section(m.pin))

        self._complex_pins = QtGui.QCheckBox(m.use_complex_pins)
        self._complex_pins.setChecked(settings[SETTINGS.COMPLEX_PINS])
        self._complex_pins.setDisabled(
            settings.is_locked(SETTINGS.COMPLEX_PINS))
        layout.addRow(self._complex_pins)

        self._pin_expires = QtGui.QCheckBox(m.pin_expires)
        self._pin_expires_days = QtGui.QSpinBox()
        self._pin_expires_days.setMinimum(30)

        pin_expires = settings[SETTINGS.PIN_EXPIRATION]
        pin_expiry_locked = settings.is_locked(SETTINGS.PIN_EXPIRATION)
        self._pin_expires.setChecked(bool(pin_expires))
        self._pin_expires_days.setValue(pin_expires)
        self._pin_expires.setDisabled(pin_expiry_locked)
        self._pin_expires_days.setDisabled(
            pin_expiry_locked or not pin_expires)
        self._pin_expires.stateChanged.connect(
            self._pin_expires_days.setEnabled)
        layout.addRow(self._pin_expires)
        layout.addRow(m.pin_expires_days, self._pin_expires_days)

        layout.addRow(self.section(m.misc))
        reader_pattern = settings[SETTINGS.CARD_READER]
        self._reader_pattern = QtGui.QLineEdit(reader_pattern)
        layout.addRow(m.reader_name, self._reader_pattern)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                         QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _pin_expires_changed(self, val):
        print val
        self._pin_expires_days.setEnabled(val)

    def _save(self):
        settings[SETTINGS.COMPLEX_PINS] = self._complex_pins.isChecked()
        settings[SETTINGS.CARD_READER] = self._reader_pattern.text()
        if self._pin_expires.isChecked():
            settings[SETTINGS.PIN_EXPIRATION] = self._pin_expires_days.value()
        else:
            settings[SETTINGS.PIN_EXPIRATION] = 0
        self.accept()
