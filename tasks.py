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
import shutil
import tempfile
from pathlib import Path

from invoke import run, task

from shprote import __version__ as __program_version__

os.environ["PIPENV_VERBOSITY"] = "-1"
os.environ["SHPROTE_TEMP"] = ".shprote"


def prun(command, **kwargs):
    """Pipenv run"""
    run(f"pipenv run {command}", **kwargs)


@task
def makemessages(command):
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf_name = tf.name
    tf.seek(0)
    tf.write("\n".join((str(i) for i in Path(".").rglob("*.py"))).encode("utf-8"))
    tf.flush()
    tf.close()
    print(tf_name)

    run(
        "xgettext --verbose --from-code=utf-8 "
        + f"--files-from={tf_name} -o locale/base.pot"
    )

    for folder in (f.path for f in os.scandir("locale") if f.is_dir()):
        lc_messages = os.path.join(folder, "LC_MESSAGES")
        po_file = os.path.join(lc_messages, "base.po")

        Path(lc_messages).mkdir(exist_ok=True)
        Path(po_file).touch()

        run(f'msgcat --use-first locale/base.pot "{po_file}" --output-file="{po_file}"')


@task
def compilemessages(command):
    for folder in (f.path for f in os.scandir("locale") if f.is_dir()):
        print(f"Compiling {folder}...", end=" ")

        lc_messages = os.path.join(folder, "LC_MESSAGES")
        po_file = os.path.join(lc_messages, "base.po")
        mo_file = os.path.join(lc_messages, "base.mo")

        run(f"msgfmt -o {mo_file} {po_file}")
        print("OK")


@task
def heroku(context, command):
    if command == "stop":
        prun("heroku ps:scale web=0 -a=shprote-bot")
    elif command == "start":
        prun("heroku ps:scale web=1 -a=shprote-bot")
    elif command == "bash":
        prun("heroku run bash --app shprote-bot")


@task
def hs(context):
    heroku(context, "start")


@task
def dev(context):
    prun("python devsrv.py")


@task
def clean(context):
    patterns = [
        ln.strip() for ln in open(".gitignore", "r", encoding="utf8").readlines()
    ]
    patterns.remove("__pycache__/")
    patterns.remove("config.toml")

    patterns = [p for p in patterns if os.path.exists(p.strip())]
    found_smth = False

    for pattern in patterns:
        found_smth = True

        print("Removing %s" % pattern)
        try:
            shutil.rmtree(pattern)
        except Exception:
            os.remove(pattern)

    if log_files := list(Path(os.path.join(".", "log")).rglob("*.log*")):
        found_smth = True
        print("Removing logs...")
        [os.remove(p) for p in log_files]

    if pycache := list(Path(".").rglob("__pycache__")):
        found_smth = True
        print("Removing python cache...")
        [shutil.rmtree(p) for p in pycache]

    if not found_smth:
        print("Nothing was found to delete, exitting...")


@task
def docs(context):
    prun("pdoc -o ./docs shprote")


@task
def test(context):
    prun("pytest -W ignore::DeprecationWarning")


@task
def cloc(context):
    run("cloc .")


@task
def time(context):
    run("git-time .")


@task
def tag(context):
    """Auto add tag to git commit depending on shprote.__version__"""
    run(f"git tag {__program_version__}")
    run("git push --tags")
