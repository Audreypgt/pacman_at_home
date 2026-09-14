import sys
import os


def resource_path(relative_path: str) -> str:
    """Get the correct path for our executable made with pyinstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(
        __file__)))
    return os.path.join(base_path, relative_path)
