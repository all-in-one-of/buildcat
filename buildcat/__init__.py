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

"""Provides the Buildcat public API."""

from __future__ import absolute_import, division, print_function

import logging
import os

__version__ = "0.3.0-dev"

formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s:%(name)s:%(message)s", datefmt="%H:%M:%S")

handler = logging.StreamHandler()
handler.setFormatter(formatter)

log = logging.getLogger(__name__)
log.setLevel(os.environ.get("BUILDCAT_LOG_LEVEL", logging.INFO))
log.addHandler(handler)

class Error(Exception):
    """Base class for all Buildcat exceptions.

    Parameters
    ----------
    message: str, required
        Short message describing the failure.
    description: str, required
        Detailed description of the failure, including possible remediations.
    """
    def __init__(self, message, description):
        self.message = message
        self.description = description

    def __repr__(self):
        return "<buildcat.Error message={!r} description={!r}>".format(self.message, self.description)


def rooted_path(root, path):
    if not root:
        raise Error("Buildcat Root not specified.", "You must specify the path to the Buildcat shared storage directory for this machine.")

    if not (os.path.exists(root) and os.path.isdir(root)):
        raise Error("Buildcat Root path does not exist.", "The Buildcat shared storage location must be an existing directory.")

    if not os.path.isabs(root):
        raise Error("Buildcat Root must be absolute.", "The Buildcat Root path must be an absolute (not relative) path.")

    if not os.path.isabs(path):
        raise Error("Internal error.", "The path must be an absolute (not relative) path.")

    if not path.startswith(root):
        raise Error("File stored outside Buildcat Root.", "This file and its assets must be saved to the Buildcat shared storage location to be rendered.")
    path = os.path.join("$BUILDCAT_ROOT", os.path.relpath(path, root))

    return path
