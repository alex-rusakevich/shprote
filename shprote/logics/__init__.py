import shprote.logics.zh as zh


class Language:
    Chinese = "zh"
    Russian = "ru"
    English = "en"
    Belarusian = "be"
    Arabian = "ar"


def get_module_by_lang(lang):
    if lang == Language.Chinese:
        return zh
    else:
        raise Exception(f"Language not available: {lang}")
