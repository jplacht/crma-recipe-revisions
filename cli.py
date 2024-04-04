from typing import Optional

from tool import init_structure
from tool import find_previous
from tool import extract_recipe_json
from tool import show_revisions
from tool import show_revision


def cmd_show(revision: Optional[str], changes: bool) -> None:

    if revision is not None:
        show_revision(revision=revision, changes=changes)
    else:
        show_revisions()


def cmd_run() -> None:
    previous = find_previous()
    extract_recipe_json(previous)


def cmd_init() -> None:
    init_structure()
