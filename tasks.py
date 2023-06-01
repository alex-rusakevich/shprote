from invoke import run, task
import os
import re
from pathlib import Path
import shutil

from shprote import __version__ as __program_version__

os.environ["PIPENV_VERBOSITY"] = "-1"
os.environ["SHPROTE_TEMP"] = ".shprote"


def prun(command, **kwargs):
    """ Pipenv run """
    run(f"pipenv run {command}", **kwargs)


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
    patterns = [l.strip() for l in open(
        '.gitignore', 'r', encoding='utf8').readlines()]
    patterns.remove('__pycache__/')
    patterns.remove('config.toml')

    patterns = [p for p in patterns if os.path.exists(p.strip())]
    found_smth = False

    for pattern in patterns:
        found_smth = True

        print("Removing %s" % pattern)
        try:
            shutil.rmtree(pattern)
        except:
            os.remove(pattern)

    if (log_files := list(Path(os.path.join(".", "log")).rglob("*.log*"))):
        found_smth = True
        print("Removing logs...")
        [os.remove(p) for p in log_files]

    if (pycache := list(Path('.').rglob('__pycache__'))):
        found_smth = True
        print("Removing python cache...")
        [shutil.rmtree(p) for p in pycache]

    if not found_smth:
        print("Nothing was found to delete, exitting...")


@task
def test(context):
    prun("pytest -W ignore::DeprecationWarning")


@task
def cloc(context):
    run("cloc .")


@task
def time(context):
    run('git-time .')


@task
def tag(context):
    """Auto add tag to git commit depending on shprote.__version__"""
    run(f"git tag {__program_version__}")
    run(f"git push --tags")
