import os
import shutil

from pydub import AudioSegment
import speech_recognition as sr

from shprote.log import get_logger


logger = get_logger()
DATA_DIR = os.path.abspath(".")


FRAMERATE = 16000
CHANNELS = 1


def unpack_models():
    logger.info("Unpacking language models...")

    sphinx_folder = os.path.dirname(sr.__file__)
    sphinx_archives = {
        "zh-CN": os.path.join(DATA_DIR, "models", "sphinx-zh-CN.zip")
    }

    for k, v in sphinx_archives.items():
        sphinx_unpack_path = os.path.join(
            sphinx_folder, "pocketsphinx-data", k)
        if not os.path.exists(sphinx_unpack_path) or not os.path.isdir(sphinx_unpack_path):
            shutil.unpack_archive(v, sphinx_folder)
            logger.info(f"Unpacked sphinxes {k} into {sphinx_unpack_path}")
    logger.info("Language models are ready")


unpack_models()


def voice_msg_to_text(ogg_path, lang) -> str:
    def _voice_msg_to_text(ogg_path, lang) -> str:
        wav_path = os.path.splitext(ogg_path)[0] + ".wav"
        song = AudioSegment.from_ogg(ogg_path)
        song = song.set_channels(CHANNELS)
        song = song.set_frame_rate(FRAMERATE)
        song.export(wav_path, format="wav")

        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)

        result = ""

        try:
            result = r.recognize_google(audio, language=lang)
        except:
            try:
                result = r.recognize_sphinx(audio, language=lang)
            except:
                pass

        logger.debug(f"Speech-to-text result: '{result}'")
        return result

    return _voice_msg_to_text(ogg_path, lang)