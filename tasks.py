from invoke import run, task
from shprote import __version__ as __program_version__
import os
from pathlib import Path
import shutil


def prun(command, **kwargs):
    """ Pipenv run """
    run(f"pipenv run {command}", **kwargs)


@task
def stop_heroku(context):
    prun("heroku ps:scale bot=0 -a=shprote-bot")


@task
def start_heroku(context):
    prun("heroku ps:scale bot=1 -a=shprote-bot")


@task
def heroku_bash(context):
    prun("heroku run bash --app shprote-bot")


@task(pre=[stop_heroku,], post=[start_heroku,])
def srv(context):
    prun("shprote_server.py")


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
    prun("pytest")


@task()
def tg(context):
    """Auto add tag to git commit depending on shprote.__version__"""
    run(f"git tag {__program_version__}")
