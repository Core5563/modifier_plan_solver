"""module to help with file handling"""
from os import remove

def remove_file(file_name) -> None:
    """remove a file"""
    try:
        remove(file_name)
    except Exception:
        pass
