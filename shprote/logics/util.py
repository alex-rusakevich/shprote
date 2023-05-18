import sys
import os
from unicodedata import category
from pathlib import Path
import tempfile

import numpy as np

from shprote.log import get_logger

logger = get_logger()
purificator_tr = {}


def get_ignored_char_tr():
    global purificator_tr

    if not purificator_tr:
        ignored_characters = ""
        purificator_tr = {}
        ignore_cache_path = os.path.join(tempfile.gettempdir(), "cache")
        Path(ignore_cache_path).mkdir(parents=True, exist_ok=True)
        ignore_cache_path = os.path.join(
            ignore_cache_path, "ignored-chars.npy")

        if not (os.path.exists(ignore_cache_path) and os.path.isfile(ignore_cache_path)):
            logger.info("No chached ignore characters.")
            ignored_characters = "".join([chr(i) for i in range(
                sys.maxunicode + 1) if category(chr(i)).startswith("P")])

            purificator_dict = dict.fromkeys(ignored_characters, " ")
            purificator_tr = str.maketrans(purificator_dict)

            logger.info(
                f"Writing cached ignore characters to '{ignore_cache_path}'...")
            np.save(ignore_cache_path, purificator_tr)
        else:
            logger.info(
                f"Reading cached ignore characters from '{ignore_cache_path}'...")
            purificator_tr = np.load(
                ignore_cache_path, allow_pickle=True).item()

    return purificator_tr
