import os
import toml

from shprote import __version__

pipfile = toml.load(os.path.join(".", "Pipfile"))
used_packages = list(pipfile["packages"].keys())

patchnote = ""
with open(os.path.join(".", "patchnote.txt")) as pnf:
    patchnote = pnf.read().strip()

patchnote_info = ""
if not (patchnote == "" or len(patchnote.split("\n")) == 1):
    patchnote = "\n".join(
        ["➡ " + new for new in patchnote.split("\n")[1:] if new.strip()])
    patchnote_info = f"""

*What's new in {__version__}?*
{patchnote}"""


HELP = f"""
*Standardized 汉语 Pronunciation TEster {__version__}*
Created by Alexander Rusakevich (https://github.com/alex-rusakevich)

/start — start the bot and go to the main menu
/help — display this message
/checkpr — begin your pronunciation check. The special code / hash in bot replies is intended to avoid pupil cheating by sending different results or fake tasks
/checklisten — begin the listening check
/stop — stop the check and go to main menu

_May 汉语 be with you!_{patchnote_info}

_Special thanks to the authors of {", ".join(used_packages[:-1])} and {used_packages[-1]} libraries_
""".strip()
