import os
import shutil
import tempfile
from pathlib import Path

from shprote.log import get_logger

logger = get_logger()


def get_tmp(sub_dir="") -> str:
    """Create tempdir in standard folder or in it's subfolder

    To change the standard folder, set `SHPROTE_TEMP` or it will be set via running `tempfile.gettempdir()`

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
        except:
            os.remove(pattern)
