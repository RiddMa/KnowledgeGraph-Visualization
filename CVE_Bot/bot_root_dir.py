import logging
from pathlib import Path


def get_bot_root_dir() -> Path:
    return Path(__file__).parent


def get_source_data_dir() -> Path:
    path = get_bot_root_dir().joinpath("source_data")
    if not path.exists():
        print("Data directory don't exist. Created directory.")
        Path.mkdir(path, parents=True)
    return path


def get_cve_data_dir() -> Path:
    path = get_bot_root_dir().joinpath("source_data").joinpath("cve_data")
    if not path.exists():
        print("Data directory don't exist. Created directory.")
        Path.mkdir(path, parents=True)
    return path


def get_cpe_data_dir() -> Path:
    path = get_bot_root_dir().joinpath("source_data").joinpath("cpe_data")
    if not path.exists():
        print("Data directory don't exist. Created directory.")
        Path.mkdir(path, parents=True)
    return path


def get_log_dir() -> Path:
    path = get_bot_root_dir().joinpath('logs')
    if not path.exists():
        logging.info("Log directory does not exist. Created log directory " +
                     repr(path))
        Path.mkdir(path, parents=True)
    return path
