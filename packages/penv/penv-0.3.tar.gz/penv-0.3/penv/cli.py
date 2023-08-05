# -*- coding: utf-8 -*-
import os
import click

from .base import Penv
from . import VERSION


abspath = os.path.abspath
startup_script_bash = """
function cd () {
    LOCK_FILE=/tmp/.penv-lock

    if [ -f $LOCK_FILE ]
    then
        builtin cd "$@"
    else
        touch $LOCK_FILE
        builtin cd "$@" && eval "$(penv scan)"
        rm $LOCK_FILE
    fi
}

function penv-ify () {
    VIRTUAL_ENV_DIRECTORY_PATH=$1

    mkdir -p .penv/.plugins

    if [ -d "$VIRTUAL_ENV_DIRECTORY_PATH" ]; then
        VIRTUAL_ENV_DIRECTORY_NAME="`basename $VIRTUAL_ENV_DIRECTORY_PATH`"
        echo "$VIRTUAL_ENV_DIRECTORY_NAME" > .penv/default
        builtin cd .penv                                                     && \
            ln -s ../$VIRTUAL_ENV_DIRECTORY_PATH $VIRTUAL_ENV_DIRECTORY_NAME && \
            builtin cd ..
    else
        echo "venv" > .penv/default
        virtualenv .penv/venv --prompt="(`basename \`pwd\``)"
    fi

    cd .
}
"""


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, default=False,
              help=('Prints version'))
@click.option('--startup-script', is_flag=True, default=False,
              help=('Just prints the command to be evaluated by given shell '
                    '(so far only bash supported)'))
@click.pass_context
def cli(ctx, version, startup_script):
    if ctx.invoked_subcommand is None and version:
        return click.echo(VERSION)

    if ctx.invoked_subcommand is None and startup_script:
        return click.echo(startup_script_bash)

    if ctx.invoked_subcommand is None:
        return click.echo(ctx.command.get_help(ctx))

    # Maybe I'll make "place" customizable at some point
    ctx.obj = {
        'place': abspath('.'),
        'startup_script': startup_script,
    }


# $> penv scan
@cli.command('scan')
@click.pass_context
def cli_scan(ctx, env=Penv()):
    place = ctx.obj['place']
    return click.echo(env.lookup(place))
