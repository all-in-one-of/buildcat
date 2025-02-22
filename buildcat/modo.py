# Copyright 2018 Timothy M. Shead
#
# This file is part of Buildcat.
#
# Buildcat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Buildcat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Buildcat.  If not, see <http://www.gnu.org/licenses/>.

"""Functionality for integration with Foundry Modo.
"""

from __future__ import absolute_import, division, print_function

import getpass
import os
import re
import socket
import subprocess
import sys
import time

import rq

import buildcat


def _modo_executable():
    return "modo_cl"


def _buildcat_root():
    return os.getcwd()


def _expand_path(path):
    path = path.replace("$BUILDCAT_ROOT", _buildcat_root())
    path = os.path.abspath(path)
    path = path.replace("\\", "/")
    return path


def _log_command(command):
    buildcat.log.debug("\n\n" + " ".join(command) + "\n\n")


def ping():
    """Return version and path information describing the worker's local Modo installation.

    Returns
    -------
    metadata: dict
        A collection of key-value pairs containing information describing the
        local Houdini installation.
    """

    code = ping.code.format(BUILDCAT_ROOT=_buildcat_root())
    command = [_modo_executable()]
    _log_command(command)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, universal_newlines=True)
    stdout, stderr = process.communicate(code)
    version = re.search("> : (\d+)", stdout).group(1)

    return {
        "host": socket.gethostname(),
        "modo": _modo_executable(),
        "modo-version": version,
        "pid": os.getpid(),
        "platform": sys.platform,
        "python": sys.version,
        "prefix": sys.prefix,
        "root": os.getcwd(),
        "user": getpass.getuser(),
    }

ping.code = """
query platformservice appversion ?
app.quit
"""

def split_frames(lxofile, frames):
    """Render individual frames from a Modo .lxo file.

    Parameters
    ----------
    lxofile: str, required
        Path to the file to be rendered.
    frames: tuple, required
        Contains the half-open (start, end, step) of frames to be rendered.
    """
    lxofile = str(lxofile)
    start = int(frames[0])
    end = int(frames[1])
    step = int(frames[2])

    q = rq.Queue(rq.get_current_job().origin, connection=rq.get_current_connection())
    for frame in range(start, end, step):
        q.enqueue("buildcat.modo.render_frames", lxofile, (frame, frame+1, 1))


def render_frames(lxofile, frames):
    """Render a range of frames from a Modo .lxo file.

    Parameters
    ----------
    lxofile: str, required
        Path to the file to be rendered.
    frames: tuple, required
        Contains the half-open (start, stop, step) range of frames to be rendered.
    """
    lxofile = _expand_path(lxofile)
    start = int(frames[0])
    stop = int(frames[1])
    step = int(frames[2])

    code = render_frames.code.format(lxofile=lxofile, start=start, stop=stop-1, step=step)
    buildcat.log.debug(code)
    command = [_modo_executable()]
    _log_command(command)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, universal_newlines=True)
    stdout, stderr = process.communicate(code)

render_frames.code = """
log.toConsole true
log.toConsoleRolling true
scene.open "{lxofile}"
pref.value render.threads auto
select.Item Render
item.channel first {start}
item.channel last {stop}
item.channel step {step}
render.animation {{*}}
app.quit
"""
