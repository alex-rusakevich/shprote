from getpass import getpass
import os
import sys
from pathlib import Path
import datetime
from dateutil.relativedelta import *

import telebot.types as tt
from sqlalchemy import extract

from shprote.config import get_config, save_config
from ..bot import bot
from ..common import *
from ..log import logfile_dir, get_logger
from shprote.db import DB_SESSION
from shprote.db.declarations import User


MSG_SHUTDOWN = "🔴 Shutdown"
MSG_LOG = "📜 Log"
MSG_STATS = "🧮 Statistics"


config = get_config()
logger = get_logger()


admin_pass = os.environ.get("ADMIN_PASS")
if not admin_pass:
    admin_pass = config["main"]["admin-pass"]
if not admin_pass:
    config["main"]["admin-pass"] = getpass("Admin password: ")
    save_config()
    admin_pass = config["main"]["admin-pass"]

admin_id = os.environ.get("ADMIN_ID")
if admin_id:
    admin_id = list(map(int, admin_id.split(";")))
else:
    admin_id = config["main"]["admin-id"]
    if not admin_id:
        config["main"]["admin-id"] = list(map(int,
                                          getpass("Admin ids (XX;YY;ZZ): ").split(";")))
        save_config
        admin_id = config["main"]["admin-id"]


def render_admin():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_btn = tt.KeyboardButton(MSG_MENU)
    shutdown_btn = tt.KeyboardButton(MSG_SHUTDOWN)
    log_btn = tt.KeyboardButton(MSG_LOG)
    stats_btn = tt.KeyboardButton(MSG_STATS)
    markup.add(menu_btn, shutdown_btn, log_btn, stats_btn)
    return markup


def check_tg_id(message):
    if int(message.chat.id) in admin_id:
        markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
        stop_btn = tt.KeyboardButton(MSG_MENU)
        markup.add(stop_btn)

        bot.send_message(
            message.chat.id, "✅ The id is correct. Now enter the password, please:", reply_markup=markup)
        bot.register_next_step_handler(
            message, check_admin_password)
    else:
        bot.send_message(
            message.chat.id, "⛔ Your id is not allowed, returning to the main menu", reply_markup=render_main_menu())


def check_admin_password(message):
    if message.text in (MSG_MENU, "/menu"):
        bot.send_message(
            message.chat.id, "Returning to the main menu", reply_markup=render_main_menu())
        return

    if message.text != admin_pass:
        bot.send_message(
            message.chat.id, "⛔ The password is wrong, returning to the main menu", reply_markup=render_main_menu())
        return

    bot.delete_message(message.chat.id, message.id)

    usr = message.from_user
    logger.info(
        f"Somebody has logged in the admin panel. His name is {usr.first_name} {usr.last_name} (@{usr.username}, {usr.id})")

    bot.send_message(message.chat.id, "Hello, admin!",
                     reply_markup=render_admin())
    bot.register_next_step_handler(
        message, admin_commands)


def admin_commands(message):
    def send_logs():
        log_files = [os.path.abspath(str(p)) for p in Path(logfile_dir).glob("*.log*")
                     if os.path.isfile(os.path.abspath(str(p)))]
        for log_file_path in log_files:
            with open(log_file_path, "rb") as log_file:
                bot.send_document(message.chat.id, log_file)

    if message.text in ("/menu", MSG_MENU):
        bot.send_message(
            message.chat.id, "Switching back to the menu...", reply_markup=render_main_menu())
        return
    elif message.text in ("/shutdown", MSG_SHUTDOWN):
        logger.warning("Admin has shutdowned the bot, stopping...")
        bot.send_message(
            message.chat.id, "I do hope you know what you've done...")
        bot.stop_bot()
        sys.exit(0)
    elif message.text in ("/log", MSG_LOG):
        bot.send_message(
            message.chat.id, "Here you are...")
        send_logs()
        bot.send_message(
            message.chat.id, "Done, no more logs left to send", reply_markup=render_admin())
        bot.register_next_step_handler(
            message, admin_commands)
    elif message.text in (MSG_STATS, "/stats", "/statistics"):
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
        new_users_this_month = all_users.filter(extract("year", User.joined) == this_year)\
            .filter(extract("month", User.joined) == this_month).count() - all_users\
            .filter(extract("year", User.joined) == prev_year).filter(extract("month", User.joined) == prev_month).count()

        new_users_this_year = all_users.filter(extract("year", User.joined) == this_year).count() - all_users\
            .filter(extract("year", User.joined) == prev_year).count()
        # endregion

        # region Active users
        active_users_this_year = all_users.filter(
            extract("year", User.last_active) == this_year).count()
        new_active_users_this_year = active_users_this_year - \
            all_users.filter(extract("year", User.last_active)
                             == prev_year).count()

        active_users_this_month = all_users.filter(extract("year", User.last_active) == this_year)\
            .filter(extract("month", User.last_active) == this_month).count()
        new_active_users_this_month = active_users_this_month - all_users.filter(extract("year", User.last_active) == prev_year)\
            .filter(extract("month", User.last_active) == prev_month).count()
        # endregion

        STATS_MSG = f"""
*All users:* {users_in_total} ({'{:+}'.format(new_users_this_month)} this month, {'{:+}'.format(new_users_this_year)} this year)
*Active users this year:* {active_users_this_year} ({'{:+}'.format(new_active_users_this_year)})
*Active users this month:* {active_users_this_month} ({'{:+}'.format(new_active_users_this_month)})
        """.strip()

        bot.send_message(
            message.chat.id, STATS_MSG, reply_markup=render_admin())
        bot.register_next_step_handler(
            message, admin_commands)
