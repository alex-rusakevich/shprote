# Shprote bot - Standardized Hanyu (Chinese) PROnunciation TEster
# Copyright (C) 2023, 2024 Alexander Rusakevich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import tempfile
from pathlib import Path

from shprote.log import get_logger

logger = get_logger()


def get_tmp(sub_dir="") -> str:
    """Create tempdir in standard folder or in it's subfolder

    To change the standard folder, set `SHPROTE_TEMP`
    or it will be set via running `tempfile.gettempdir()`

    :param sub_dir: subdirectory in default folder, defaults to ""
    :type sub_dir: str, optional
    :return: new directories path
    :rtype: str
    """

    temp_dir = ""
    if sh_tmp := os.environ.get("SHPROTE_TEMP"):
        temp_dir = sh_tmp
    else:
        temp_dir = os.path.join(tempfile.gettempdir(), "shprote")

    temp_dir = os.path.join(temp_dir, sub_dir)

    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    return temp_dir


def clean_temp():
    tmp_d = get_tmp()
    patterns = [
        os.path.join(tmp_d, "voice"),
    ]
    patterns = [p for p in patterns if os.path.exists(p)]

    for pattern in patterns:
        logger.debug("Removing %s" % pattern)
        try:
            shutil.rmtree(pattern)
        except Exception:
            os.remove(pattern)
