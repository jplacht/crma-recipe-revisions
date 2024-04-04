from typing import Union
from typing_extensions import Annotated

import typer


# Initialize Typer for CLI
app = typer.Typer(no_args_is_help=True)

from cli import cmd_show
from cli import cmd_run
from cli import cmd_init


@app.command()
def show(
    revision: Annotated[Union[str, None], typer.Argument(help="Revision ID")] = None,
    changes: Annotated[bool, typer.Argument(help="Show changes")] = False,
) -> None:
    """
    Shows available recipe revisions
    """
    cmd_show(revision=revision, changes=changes)


@app.command()
def run():
    """
    Creates a new revision
    """
    cmd_run()


@app.command()
def init():
    """
    Initializes folder structure
    """
    cmd_init()


if __name__ == "__main__":
    app()
