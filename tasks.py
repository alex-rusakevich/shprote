from invoke import run, task
import os


def prun(command, **kwargs):
    """ Pipenv run """
    run(f"pipenv run {command}", **kwargs)


@task
def ui(context):
    prun("shprote.py")


@task
def srv(context):
    prun("shprote_server.py")


@task
def clean(context):
    patterns = ['.pytest_cache']
    for pattern in patterns:
        run("rm -rf %s" % pattern)


@task
def test(context):
    prun("pytest")


@task
def designer(context):
    prun("pyqt6-tools designer")


@task
def ddir(context):
    """ App's data dir in ~"""
    run("explorer %s" % os.path.join(os.path.expanduser("~"), ".shprote"))
