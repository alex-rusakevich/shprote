import telebot.types as tt


MSG_CHECK = "📝 Check"
MSG_HELP = "❓ Help"
MSG_MENU = "🍱 Menu"
MSG_STOP = "❌ Stop"


def render_main_menu():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    check_btn = tt.KeyboardButton(MSG_CHECK)
    help_btn = tt.KeyboardButton(MSG_HELP)
    markup.add(check_btn, help_btn)
    return markup
