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

"""Functionality for integration with SideFX Houdini.
"""

from __future__ import absolute_import, division, print_function

import json
import logging
import os
import subprocess
import time

import buildcat
import buildcat.worker

log = logging.getLogger("rq.worker")

def _hython_executable():
    return "hython"


def _buildcat_root():
    return os.getcwd()


def metadata():
    """Return version and path information describing the worker's local Houdini installation.

    Returns
    -------
    metadata: dict
        A collection of key-value pairs containing information describing the
        local Houdini installation.
    """

    code = metadata.code.format(BUILDCAT_ROOT=_buildcat_root())
    command = [_hython_executable(), "-c", code]
    result = json.loads(subprocess.check_output(command))
    return result

metadata.code = """
import json
import sys
json.dump({{
    "name": hou.applicationName(),
    "version": hou.applicationVersionString(),
    "BUILDCAT_ROOT": {BUILDCAT_ROOT!r},
}}, sys.stdout)
"""


def render(hipfile, rop, frames):
    """Render a range of frames from a Houdini .hip file.

    Parameters
    ----------
    hipfile: str, required
        Path to the file to be rendered.
    rop: str, required
        Absolute path of the ROP node to use for rendering.
    frames: tuple, required
        Contains the half-open range of frames to be rendered.
    """
    hipfile = str(hipfile)
    rop = str(rop)
    start = int(frames[0])
    end = int(frames[1])

    q = buildcat.worker.queue()
    for frame in range(start, end):
        q.enqueue("buildcat.hou.render_frame", hipfile, rop, frame)


def render_frame(hipfile, rop, frame):
    """Render a single frame from a Houdini .hip file.

    Parameters
    ----------
    hipfile: str, required
        Path to the file to be rendered.
    rop: str, required
        Absolute path of the ROP node to use for rendering.
    frame: int, required
        The frame to be rendered.
    """
    hipfile = os.path.abspath(hipfile.replace("$BUILDCAT_ROOT", _buildcat_root()))
    rop = str(rop)
    frame = int(frame)

    code = render_frame.code.format(hipfile=hipfile, rop=rop, frame=frame)
    log.debug(code)
    command = [_hython_executable(), "-c", code]
    subprocess.check_call(command)

render_frame.code = """
import hou

hou.hipFile.load({hipfile!r}, suppress_save_prompt=True, ignore_load_warnings=True)
rop = hou.node({rop!r})
rop.render(frame_range=({frame},{frame}), verbose=True, output_progress=True)
"""

