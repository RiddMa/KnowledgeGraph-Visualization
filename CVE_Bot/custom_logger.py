import logging
import sys
from datetime import datetime
from pathlib import Path


def init_log_dir():
    """
        Get directory for log files. Create folders if path doesn't exist.

        :return: Directory for log files.
        """
    path = Path(__file__).parent.joinpath('logs')
    if not path.exists():
        Path.mkdir(path, parents=True)
    return path


def setup_logger(name, log_folder=None, lvl_file=None, lvl_stdout=None):
    """
    Create a new logger.

    :param name: name for the logger
    :param log_folder: folder path to save logfile
    :param lvl_file: logger level for file handler.
    :param lvl_stdout: logger level for stdout handler.
    :return:
    """
    if not lvl_file:
        lvl_file = logging.INFO
    if not lvl_stdout:
        lvl_stdout = logging.INFO
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s:  %(message)s')

    # logfile = f'{name}-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    logfile = f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    if not log_folder:
        log_folder = init_log_dir().joinpath(logfile)
    file_handler = logging.FileHandler(log_folder)
    file_handler.setLevel(lvl_file)
    file_handler.setFormatter(formatter)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(lvl_stdout)
    stdout_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    logger.info(
        f'Logger "{name}" logging to {logfile} with log_file level {lvl_file} and log_stdout level {lvl_stdout}.')
    return logger


loggers = {}


def mylogger(name) -> logging.Logger:
    """
    Logger factory for getting singleton logger objects.

    :param name: Logger name
    :return: <name> logger object
    """
    if 'root' not in loggers:
        print('Creating root logger')
        loggers['root'] = setup_logger('root', lvl_file=logging.INFO, lvl_stdout=logging.INFO)
    if name not in loggers:
        loggers['root'].info(f'Creating logger {name}')
        loggers[name] = setup_logger(name, lvl_file=logging.INFO, lvl_stdout=logging.INFO)
    loggers['root'].debug('Using created logger')  # NOTE THIS IS DEBUG LEVEL!
    return loggers[name]


if __name__ == "__main__":
    a = mylogger('TEST')
    # a.info('this is test1')
    # b = mylogger('TEST')
    # print(a is b)
    # mylogger('TEST').info('this is test 2')


# import logging
# import sys
#
# from bot_root_dir import get_log_dir
#
#
# def setup_logger(name, log_filename, level_file=logging.INFO, level_stdout=logging.WARNING):
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s:  %(message)s')
#
#     file_handler = logging.FileHandler(get_log_dir().joinpath(log_filename))
#     file_handler.setLevel(level_file)
#     file_handler.setFormatter(formatter)
#
#     stdout_handler = logging.StreamHandler(sys.stdout)
#     stdout_handler.setLevel(level_stdout)
#     stdout_handler.setFormatter(formatter)
#
#     logger = logging.getLogger(name)
#     logger.addHandler(file_handler)
#     logger.addHandler(stdout_handler)
#
#     logger.setLevel(logging.DEBUG)
#     logger.info(
#         f'Logger {name} logging to {log_filename} with log_file level {level_file} and log_stdout level {level_stdout}.')
#     return logger

