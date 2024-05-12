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
import threading

import toml

from shprote import __version__
from shprote.bot import bot
from shprote.config import get_config, get_translator
from shprote.db.management import upsert_user
from shprote.log import get_logger
from shprote.routes.admin import check_tg_id
from shprote.routes.common import *
from shprote.routes.listeningchk import start_listening_test
from shprote.routes.pronunchk import start_pronun_test

pipfile = toml.load(os.path.join(".", "Pipfile"))
used_packages = list(pipfile["packages"].keys())

logger = get_logger()
config = get_config()


@bot.message_handler(commands=["start"])
def send_welcome(message):
    _ = get_translator(message.from_user.language_code)

    markup = render_main_menu(_)
    bot.send_message(
        message.chat.id,
        _("Hello there, {name}! I'm ready to check your pronunciation! 🤓").format(
            name=message.from_user.first_name
        ),
        reply_markup=markup,
    )

    uu_thread = threading.Thread(target=upsert_user, args=(message.from_user.id,))
    uu_thread.start()


@bot.message_handler(content_types=["text"])
def main_text_handler(message):
    _ = get_translator(message.from_user.language_code)
    main_menu_markup = render_main_menu(_)

    if message.text in (_("🎤 Check pronunciation"), "/checkpr"):
        start_pronun_test(message)
    elif message.text in (_("👂 Check listening"), "/checklisten"):
        start_listening_test(message)
    elif message.text in (_("🍱 Menu"), "/menu"):
        bot.send_message(
            message.chat.id,
            _("Welcome to the main menu!"),
            reply_markup=main_menu_markup,
        )
    elif message.text.strip() in (_("❌ Stop"), "/stop"):
        bot.send_message(
            message.chat.id,
            _("The check has been stopped. Getting back to the menu..."),
            reply_markup=main_menu_markup,
        )
    elif message.text in (_("❓ Help"), "/help"):
        bot.send_message(
            message.chat.id,
            (
                _(
                    """
*Standardized 汉语 Pronunciation TEster {__version__}*
Created by Alexander Rusakevich (https://github.com/alex-rusakevich)

/start — start the bot and go to the main menu
/help — display this message
/checkpr — begin your pronunciation check. The special code / hash in bot replies is intended to avoid pupil cheating by sending different results or fake tasks
/checklisten — begin the listening check
/stop — stop the check and go to main menu

_May 汉语 be with you!_

_Special thanks to the authors of {used_packages_exc_last} and {used_packages_last} libraries_
"""
                )
                .format(
                    used_packages_exc_last=", ".join(used_packages[:-1]),
                    used_packages_last=used_packages[-1],
                    __version__=__version__,
                )
                .strip()
            ),
            reply_markup=main_menu_markup,
        )
    elif message.text.lower() in (
        "я тебя люблю",
        "i love you",
        "我爱你",
        "я тебя люблю!",
        "i love you!",
        "我爱你！",
        "521",
        "520",
    ):
        try:
            bot.send_sticker(
                message.chat.id,
                "CAACAgIAAxkBAAEJAkdkZJ2OU5DV1melgSjQGkkg7O9jkQACoBwAAipooUjogwEq_q_PRy8E",
                reply_markup=main_menu_markup,
            )
        except:
            bot.send_message(message.chat.id, "❤️", reply_markup=main_menu_markup)
    elif message.text == "/admin":
        bot.send_message(message.chat.id, _("Checking your telegram id..."))
        check_tg_id(message)

    uu_thread = threading.Thread(target=upsert_user, args=(message.from_user.id,))
    uu_thread.start()
