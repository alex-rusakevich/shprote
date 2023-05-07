#!/usr/bin/env python
import sys
import pinyin
import Levenshtein
import re
from unicodedata import category

purificator_dict = dict.fromkeys([chr(i) for i in range(
    sys.maxunicode + 1) if category(chr(i)).startswith("P")], " ")
purificator_tr = str.maketrans(purificator_dict)


def main():
    if len(sys.argv) == 1:
        print("Interactive mode. Press Ctrl-C or Ctrl-Z to exit")

        while True:
            teacher_text = pinyin.get(
                input("\nTeacher's text: "), format='diacritical', delimiter=" ")  # Get pinyin representation
            # Replace all punctuation marks with spaces
            teacher_text = teacher_text.translate(purificator_tr)
            teacher_text = re.sub(
                r"(\s[āàáǎaēéěèeōóǒòo])", r"'\1", teacher_text)  # Add ' before words starting with a, e and o
            teacher_text = re.sub(r"\s", "", teacher_text)  # Remove spaces

            if len(teacher_text) == 0:
                print("Levenshtein mass cannot be empty. Retry")
                continue

            print("Levenshein mass:", teacher_text)

            student_text = pinyin.get(
                input("Student's text: "), format='diacritical', delimiter=" ")
            student_text = student_text.translate(purificator_tr)
            student_text = re.sub(
                r"(\s[āàáǎaēéěèeōóǒòo])", r"'\1", student_text)
            student_text = re.sub(r"\s", "", student_text)

            if len(student_text) == 0:
                print("Levenshtein mass cannot be empty. Retry")
                continue

            print("Levenshein mass:", student_text)

            max_len = max(len(teacher_text), len(student_text))
            leven_dist = Levenshtein.distance(teacher_text, student_text)
            result_ratio = (max_len - leven_dist) / max_len
            result_ratio = round(result_ratio * 100, 2)

            print(f"Total: {result_ratio}%, {leven_dist} mistake(s)")

    else:
        print("Arg mode is not supported yet")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Received stop signal.")
        sys.exit(0)
