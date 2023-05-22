import shprote.logics.zh as zh


class Language:
    Chinese = "zh-CN"


def get_module_by_lang(lang):
    if lang == Language.Chinese:
        return zh
    else:
        raise Exception(f"Language not available: {lang}")


langcode_to_name = {
    Language.Chinese: "Chinese",
}
