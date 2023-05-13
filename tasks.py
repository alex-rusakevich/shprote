from invoke import run, task
from shprote import __version__ as __program_version__
import os
import configparser
import toml
from pathlib import Path

os.environ["SHPROTE_HOME"] = "."


def prun(command, **kwargs):
    """ Pipenv run """
    run(f"pipenv run {command}", **kwargs)


@task
def ui(context):
    prun("shprote.pyw")


@task
def srv(context):
    prun("shprote_server.py")


@task
def build(context):
    pipenv_config = toml.load("Pipfile")

    config = configparser.ConfigParser()
    config['Application'] = {}
    config['Application']['name'] = 'shprote'
    config['Application']['version'] = __program_version__
    config['Application']['script'] = os.path.join('.', 'shprote.pyw')
    config['Application']['icon'] = os.path.join('ui', 'favicon.ico')
    config['Application']['license_file'] = os.path.join('.', 'LICENSE')

    config['Python'] = {}
    config['Python']['version'] = pipenv_config['requires']['python_version']
    config['Python']['bitness'] = '64'
    config['Python']['include_msvcrt'] = 'true'

    reqs = run('pipenv requirements', hide=True).stdout.split('\n')[1:]
    for i, req in enumerate(reqs):
        if (fnd := req.find(';')) != -1:
            reqs[i] = req[:fnd]
        reqs[i] = reqs[i].strip()

    config['Include'] = {}

    extra_wheel_sources = os.path.abspath(os.path.join(
        '.', 'build', 'wheels'))
    Path(extra_wheel_sources).mkdir(parents=True, exist_ok=True)
    config['Include']['extra_wheel_sources'] = extra_wheel_sources

    PRE_WHEELS = ('pinyin',)
    for req in reqs:
        if req.startswith(PRE_WHEELS):
            prun(f'pip wheel {req.strip()} -w {extra_wheel_sources}')
    reqs = '\n'.join(reqs)

    config['Include']['pypi_wheels'] = reqs

    file_list = os.listdir('.')
    ignored_paths = [l.strip() for l in open(
        '.gitignore', 'r', encoding='utf8').readlines()]
    ignored_paths = [p[:-1] for p in ignored_paths if p.endswith('/')]
    ignored_paths += ['.git', 'tests', 'tasks.py',
                      'pytest.ini', '.gitignore', '.shprote']  # Extra paths to ignore
    file_list = '\n'.join([p for p in file_list if p not in ignored_paths])

    config['Include']['files'] = file_list

    with open('install.cfg', 'w', encoding='utf-8') as install_file:
        config.write(install_file)

    prun('pynsist install.cfg')


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


@task()
def datadir(context):
    """Open app's temporary data folder at '~'"""
    run("explorer %s" % os.path.join(os.path.expanduser("~"), ".shprote"))


@task()
def cudd(context):
    """Open app's temporary data folder in vscodium"""
    run("codium %s" % os.path.join(os.path.expanduser("~"), ".shprote"))


@task()
def tg(context):
    """Auto add tag to git commit depending on shprote.__version__"""
    run(f"git tag {__program_version__}")
