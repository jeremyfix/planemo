from __future__ import print_function
import contextlib
import os
import shutil
import sys
import tempfile

import click
from galaxy.tools.deps import commands
from galaxy.tools.deps.commands import which


def communicate(cmds, **kwds):
    info(cmds)
    p = commands.shell_process(cmds, **kwds)
    ret_val = p.communicate()
    if p.returncode != 0:
        template = "Problem executing commands {0} - ({1}, {2})"
        msg = template.format(cmds, ret_val[0], ret_val[1])
        raise RuntimeError(msg)
    return ret_val


def shell(cmds, **kwds):
    info(cmds)
    return commands.shell(cmds, **kwds)


def info(message, *args):
    if args:
        message = message % args
    _echo(click.style(message, bold=True, fg='green'))


def can_write_to_path(path, **kwds):
    if not kwds["force"] and os.path.exists(path):
        error("%s already exists, exiting." % path)
        return False
    return True


def error(message, *args):
    if args:
        message = message % args
    _echo(click.style(message, bold=True, fg='red'), err=True)


def warn(message, *args):
    if args:
        message = message % args
    _echo(click.style(message, fg='red'), err=True)


def _echo(message, err=False):
    if sys.version_info[0] == 2:
        click.echo(message, err=err)
    else:
        print(message)


def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def untar_to(url, path, tar_args):
    if which("wget"):
        download_cmd = "wget -q --recursive -O - '%s'"
    else:
        download_cmd = "curl '%s'"
    download_cmd = download_cmd % url
    if tar_args:
        if not os.path.exists(path):
            os.makedirs(path)

        untar_cmd = "tar %s" % tar_args
        shell("%s | %s" % (download_cmd, untar_cmd))
    else:
        shell("%s > '%s'" % (download_cmd, path))


@contextlib.contextmanager
def temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)
