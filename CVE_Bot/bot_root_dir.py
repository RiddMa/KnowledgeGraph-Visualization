from pathlib import Path


def get_bot_root_dir() -> Path:
    return Path(__file__).parent
    # os.path.dirname(os.path.abspath(__file__))
