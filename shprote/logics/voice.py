import os
import shutil
from pathlib import Path

import speech_recognition as sr
from pydub import AudioSegment

from shprote.log import get_logger
from shprote.logics import *
from shprote.temp import get_tmp

logger = get_logger()
DATA_DIR = os.path.abspath(".")


FRAMERATE = 16000
CHANNELS = 1


rec = sr.Recognizer()

TEMP = get_tmp()
SPHINX_MODELDIR = os.path.join(TEMP, "pocketsphinx-data")

sphinx_lng_to_path = {
    Language.Chinese: (
        os.path.join(SPHINX_MODELDIR, Language.Chinese, "acoustic-model"),
        os.path.join(SPHINX_MODELDIR, Language.Chinese, "language-model.lm.bin"),
        os.path.join(
            SPHINX_MODELDIR, Language.Chinese, "pronounciation-dictionary.dict"
        ),
    ),
}


def unpack_models():
    logger.info("Unpacking language models...")

    sphinx_archives = {
        Language.Chinese: os.path.join(DATA_DIR, "models", "sphinx-zh-CN.zip")
    }

    for k, v in sphinx_archives.items():
        sphinx_unpack_path = os.path.join(SPHINX_MODELDIR, k)
        if not os.path.exists(sphinx_unpack_path) or not os.path.isdir(
            sphinx_unpack_path
        ):
            shutil.unpack_archive(v, TEMP)
            logger.info(f"Unpacked sphinx'es {k} into {sphinx_unpack_path}")
        else:
            logger.info(f"Sphinx'es {k} at {sphinx_unpack_path} is already ready")

    logger.info("Language models are unpacked")


def audio_file_to_text(file_path, lang) -> str:
    wav_path = os.path.splitext(file_path)[0] + ".wav"
    file_in_type = Path(file_path).suffix[1:]

    song = AudioSegment.from_file(file_path, file_in_type)
    song = song.set_channels(CHANNELS)
    song = song.set_frame_rate(FRAMERATE)
    song.export(wav_path, format="wav")

    with sr.AudioFile(wav_path) as source:
        audio = rec.record(source)

    result = ""

    try:
        result = rec.recognize_google(audio, language=lang)
    except:
        try:
            result = rec.recognize_sphinx(audio, language=sphinx_lng_to_path[lang])
        except:
            pass

    logger.debug(f"Speech-to-text result: '{result.encode('utf8')}'")
    return result


if True:  # On module loaded
    unpack_models()
