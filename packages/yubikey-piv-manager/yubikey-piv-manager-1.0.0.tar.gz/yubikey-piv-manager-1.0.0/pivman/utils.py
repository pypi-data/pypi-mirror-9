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

from getpass import getuser
from pivman import messages as m
import re
import subprocess
import os
import tempfile


def has_ca():
    try:
        if subprocess.mswindows:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(
                ['certutil', '-dump'], stdout=subprocess.PIPE,
                startupinfo=startupinfo)
            out, _ = p.communicate()
            return out.startswith('Entry')
    except OSError:
        pass
    return False


def request_cert_from_ca(csr, cert_tmpl):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(csr)
            csr_fn = f.name

        with tempfile.NamedTemporaryFile() as f:
            cert_fn = f.name

        p = subprocess.Popen(['certreq', '-submit', '-attrib',
                              'CertificateTemplate:%s' % cert_tmpl, csr_fn,
                              cert_fn], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = p.communicate()
        if p.returncode != 0:
            raise ValueError(m.certreq_error_1 % out)

        with open(cert_fn, 'r') as cert:
            return cert.read()
    except OSError as e:
        raise ValueError(m.certreq_error_1 % e)
    finally:
        os.remove(csr_fn)
        if os.path.isfile(cert_fn):
            os.remove(cert_fn)


def test(fn, *args, **kwargs):
    e_type = kwargs.pop('catches', Exception)
    try:
        fn(*args, **kwargs)
        return True
    except e_type:
        return False


# https://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/504.mspx?mfr=true

# Password must contain characters from three of the following four categories:
CATEGORIES = [
    lambda c: c.isupper(),  # English uppercase characters (A through Z)
    lambda c: c.islower(),  # English lowercase characters (a through z)
    re.compile(r'[0-9]').match,  # Base 10 digits (0 through 9)
    re.compile(r'\W', re.UNICODE).match
    #   Nonalphanumeric characters (e.g., !, $, #, %)
]


def contains_category(password, category):
    return any(category(p) for p in password)


def complexity_check(password):
    # Be at least six characters in length
    if len(password) < 6:
        return False

    # Contain characters from at least 3 groups:
    if sum(contains_category(password, c) for c in CATEGORIES) < 3:
        return False

    # Not contain all or part of the user's account name
    parts = [p for p in re.split(r'\W', getuser().lower()) if len(p) >= 3]
    if any(part in password.lower() for part in parts):
        return False

    return True


def der_read(der_data, expected_t=None):
    t = ord(der_data[0])
    if expected_t is not None and expected_t != t:
        raise ValueError('Wrong tag. Expected: %x, got: %x' % (expected_t, t))
    l = ord(der_data[1])
    offs = 2
    if l > 0x80:
        n_bytes = l - 0x80
        l = b2len(der_data[offs:offs + n_bytes])
        offs = offs + n_bytes
    v = der_data[offs:offs + l]
    rest = der_data[offs + l:]
    if expected_t is None:
        return t, v, rest
    return v, rest


def b2len(bs):
    l = 0
    for b in bs:
        l *= 256
        l += ord(b)
    return l
