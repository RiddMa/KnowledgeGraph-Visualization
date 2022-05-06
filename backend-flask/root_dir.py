from pathlib import Path

from logger_factory import mylogger


def get_root_dir() -> Path:
    """
    Get the directory this file is in.
    eg: /path/to/root_dir.py -> gets /path/to

    :return: Path of the directory this file is in.
    """
    return Path(__file__).parent


def get_log_dir() -> Path:
    """
    Get directory for log files. Create folders if path doesn't exist.

    :return: Directory for log files.
    """
    path = get_root_dir().joinpath('logs')
    if not path.exists():
        mylogger('root').info(f"Log directory does not exist. Created log directory {repr(path)}")
        Path.mkdir(path, parents=True)
    return path


if __name__ == "__main__":
    get_log_dir()
