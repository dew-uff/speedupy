"""What the tests use to clean up, on every operating system."""

import os
import shutil


def remove_paths(*paths: str) -> None:
    """Remove each file or folder, as `rm -rf` does: a missing path is fine.

    Anything else raises. Windows refuses to remove a file that is still open,
    so close it first.
    """
    for path in paths:
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        elif os.path.lexists(path):
            os.remove(path)
