from pathlib import Path


def get_bot_root_dir() -> Path:
    return Path(__file__).parent
    # os.path.dirname(os.path.abspath(__file__))


def get_source_data_dir() -> Path:
    return get_bot_root_dir().joinpath("source_data")
