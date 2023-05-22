import telebot.types as tt


MSG_CHECK_PRONUN = "🎤 Check pronunciation"
MSG_CHECK_LISTEN = "👂 Check listening"
MSG_HELP = "❓ Help"
MSG_MENU = "🍱 Menu"
MSG_STOP = "❌ Stop"


def render_main_menu():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    check_prn_btn = tt.KeyboardButton(MSG_CHECK_PRONUN)
    check_listen = tt.KeyboardButton(MSG_CHECK_LISTEN)
    help_btn = tt.KeyboardButton(MSG_HELP)
    markup.add(check_listen, check_prn_btn, help_btn)
    return markup
