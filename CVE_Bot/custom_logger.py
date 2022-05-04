import logging
import sys

from bot_root_dir import get_log_dir


def setup_logger(name, log_filename, level_file=logging.INFO, level_stdout=logging.WARNING):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s:  %(message)s')

    file_handler = logging.FileHandler(get_log_dir().joinpath(log_filename))
    file_handler.setLevel(level_file)
    file_handler.setFormatter(formatter)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level_stdout)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    logger.info(
        f'Logger {name} logging to {log_filename} with log_file level {level_file} and log_stdout level {level_stdout}.')
    return logger
