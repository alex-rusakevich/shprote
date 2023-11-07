import datetime
import os
import sys
from getpass import getpass
from pathlib import Path
from typing import Callable

import telebot.types as tt
from dateutil.relativedelta import *
from sqlalchemy import extract
from telebot.apihelper import ApiTelegramException

from shprote.config import get_config, save_config
from shprote.db import DB_SESSION
from shprote.db.declarations import User
from shprote.db.management import get_user_id_list, remove_user_by_id

from ..bot import bot
from ..log import get_logger, logfile_dir
from .common import *

config = get_config()
logger = get_logger()


admin_pass = os.environ.get("ADMIN_PASS")
if not admin_pass:
    admin_pass = config["bot"]["admin-pass"]
if not admin_pass:
    config["bot"]["admin-pass"] = getpass("Admin password: ")
    save_config()
    admin_pass = config["bot"]["admin-pass"]

admin_id = os.environ.get("ADMIN_ID")
if admin_id:
    admin_id = list(map(int, admin_id.split(";")))
else:
    admin_id = config["bot"]["admin-id"]
    if not admin_id:
        config["bot"]["admin-id"] = list(
            map(int, getpass("Admin ids (XX;YY;ZZ): ").split(";"))
        )
        save_config()
        admin_id = config["bot"]["admin-id"]


def render_admin(translate_fn: Callable = lambda x: x):
    _ = translate_fn

    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_btn = tt.KeyboardButton(_("🍱 Menu"))
    shutdown_btn = tt.KeyboardButton(_("🔴 Shutdown"))
    log_btn = tt.KeyboardButton(_("📜 Log"))
    stats_btn = tt.KeyboardButton(_("🧮 Statistics"))
    glob_msg_btn = tt.KeyboardButton(_("📣 Message to all users"))
    markup.add(menu_btn, shutdown_btn, log_btn, stats_btn, glob_msg_btn)
    return markup


def check_tg_id(message):
    _ = get_translator(message.from_user.language_code)

    if int(message.chat.id) in admin_id:
        markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
        stop_btn = tt.KeyboardButton(_("🍱 Menu"))
        markup.add(stop_btn)

        bot.send_message(
            message.chat.id,
            _("✅ The id is correct. Now enter the password, please:"),
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, check_admin_password)
    else:
        bot.send_message(
            message.chat.id,
            _("⛔ Your id is not allowed, returning to the main menu"),
            reply_markup=render_main_menu(_),
        )


def check_admin_password(message):
    _ = get_translator(message.from_user.language_code)

    if message.text in (_("🍱 Menu"), "/menu"):
        bot.send_message(
            message.chat.id,
            _("Returning to the main menu"),
            reply_markup=render_main_menu(),
        )
        return

    if message.text != admin_pass:
        bot.send_message(
            message.chat.id,
            _("⛔ The password is wrong, returning to the main menu"),
            reply_markup=render_main_menu(),
        )
        return

    bot.delete_message(message.chat.id, message.id)

    usr = message.from_user
    logger.info(
        f"Somebody has logged in the admin panel. His name is {usr.first_name} {usr.last_name} (@{usr.username}, {usr.id})"
    )

    bot.send_message(message.chat.id, _("Hello, admin!"), reply_markup=render_admin())
    bot.register_next_step_handler(message, admin_commands)


def admin_commands(message):
    _ = get_translator(message.from_user.language_code)

    def send_logs():
        log_files = [
            os.path.abspath(str(p))
            for p in Path(logfile_dir).glob("*.log*")
            if os.path.isfile(os.path.abspath(str(p)))
        ]
        for log_file_path in log_files:
            with open(log_file_path, "rb") as log_file:
                bot.send_document(message.chat.id, log_file)

    if message.text in ("/menu", _("🍱 Menu")):
        bot.send_message(
            message.chat.id,
            _("Switching back to the menu..."),
            reply_markup=render_main_menu(),
        )
        return
    elif message.text in ("/shutdown", _("🔴 Shutdown")):
        logger.warning("Admin has shutdowned the bot, stopping...")
        bot.send_message(message.chat.id, _("I do hope you know what you've done..."))
        bot.stop_bot()
        sys.exit(0)
    elif message.text in ("/log", _("📜 Log")):
        bot.send_message(message.chat.id, _("Here you are..."))
        send_logs()
        bot.send_message(
            message.chat.id,
            _("Done, no more logs left to send"),
            reply_markup=render_admin(),
        )
        bot.register_next_step_handler(message, admin_commands)
    elif message.text in (_("🧮 Statistics"), "/stats", "/statistics"):
        # region Calc date
        this_year = datetime.date.today()
        prev_year = (this_year - relativedelta(year=1)).year
        this_year = this_year.year

        this_month = datetime.date.today()
        prev_month = (this_month - relativedelta(month=1)).month
        this_month = this_month.month
        # endregion

        all_users = DB_SESSION.query(User)
        users_in_total = all_users.count()

        # region New users
        new_users_this_month = (
            all_users.filter(extract("year", User.joined) == this_year)
            .filter(extract("month", User.joined) == this_month)
            .count()
            - all_users.filter(extract("year", User.joined) == prev_year)
            .filter(extract("month", User.joined) == prev_month)
            .count()
        )

        new_users_this_year = (
            all_users.filter(extract("year", User.joined) == this_year).count()
            - all_users.filter(extract("year", User.joined) == prev_year).count()
        )
        # endregion

        # region Active users
        active_users_this_year = all_users.filter(
            extract("year", User.last_active) == this_year
        ).count()
        new_active_users_this_year = (
            active_users_this_year
            - all_users.filter(extract("year", User.last_active) == prev_year).count()
        )

        active_users_this_month = (
            all_users.filter(extract("year", User.last_active) == this_year)
            .filter(extract("month", User.last_active) == this_month)
            .count()
        )
        new_active_users_this_month = (
            active_users_this_month
            - all_users.filter(extract("year", User.last_active) == prev_year)
            .filter(extract("month", User.last_active) == prev_month)
            .count()
        )
        # endregion

        STATS_MSG = (
            _(
                """
*All users:* {users_in_total} ({new_users_month} this month, {new_users_year} this year)
*Active users this year:* {active_users_this_year} ({new_active_users_this_year})
*Active users this month:* {active_users_this_month} ({new_active_users_this_month})
        """
            )
            .format(
                users_in_total=users_in_total,
                new_users_month=f"{'{:+}'.format(new_users_this_month)}",
                new_users_year=f"{'{:+}'.format(new_users_this_year)}",
                active_users_this_year=active_users_this_year,
                new_active_users_this_year=f"{'{:+}'.format(new_active_users_this_year)}",
                active_users_this_month=active_users_this_month,
                new_active_users_this_month=f"{'{:+}'.format(new_active_users_this_month)}",
            )
            .strip()
        )

        bot.send_message(message.chat.id, STATS_MSG, reply_markup=render_admin())
        bot.register_next_step_handler(message, admin_commands)
    elif message.text in (_("📣 Message to all users"), "/globm"):
        markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
        stop_btn = tt.KeyboardButton(_("❌ Stop"))
        markup.add(stop_btn)

        bot.send_message(
            message.chat.id,
            _("Write to ⚠ *all* ⚠ the registred users:"),
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, global_mail)


def global_mail(message):
    _ = get_translator(message.from_user.language_code)
    glob_msg = message.text

    if glob_msg in (_("❌ Stop"), "/stop"):
        bot.send_message(
            message.chat.id,
            _("Getting back to the admin menu..."),
            reply_markup=render_admin(),
        )
        bot.register_next_step_handler(message, admin_commands)
        return

    msg_count = 0

    for usr_id in get_user_id_list():
        usr_id = usr_id[0]
        logger.debug("Trying to send a message to " + str(usr_id))

        try:
            bot.send_message(usr_id, glob_msg)
        except ApiTelegramException:
            remove_user_by_id(usr_id)
        else:
            msg_count += 1

    bot.send_message(
        message.chat.id,
        _("🟢 Done! {msg_count} messages sent!").format(msg_count=msg_count),
        reply_markup=render_admin(),
    )
    bot.register_next_step_handler(message, admin_commands)
