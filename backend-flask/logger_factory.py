import logging
import sys
from datetime import datetime
from pathlib import Path


def init_log_dir(folder_name: str = ''):
    """
        Get directory for log files. Create folders if path doesn't exist.
        Path = logs/folder_name if folder_name is set. Otherwise, use datetime.now()

        :param folder_name: folder name as string
        :return: Directory for log files.
        """
    path = Path(__file__).parent.joinpath('logs')
    if folder_name:
        path = path.joinpath(folder_name)
    else:
        path = path.joinpath(str(datetime.now().strftime("%Y-%m-%d-%H-%M")))
    if not path.exists():
        Path.mkdir(path, parents=True)
    return path


global_log_dir = ''


def setup_logger(name, log_folder=None, lvl_file=None, lvl_stdout=None):
    """
    Create a new logger. Each logger has 3 handler: 0-root.log, 1-{name}.log, stdout.
    If name=='root', 1-root.log will not be created.

    :param name: name for the logger
    :param log_folder: folder path to save logfile
    :param lvl_file: logger level for file handler.
    :param lvl_stdout: logger level for stdout handler.
    :return:
    """

    logger = logging.getLogger(name)
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    if not lvl_file:
        lvl_file = logging.INFO
    if not lvl_stdout:
        lvl_stdout = logging.INFO
    formatter = logging.Formatter(
        'P%(process)d-T%(thread)d- %(funcName)s - %(asctime)s - %(name)s - %(levelname)s: %(message)s')

    # logfile = f'{name}-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    # logfile = f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    logfile = '0-root.log'
    if not log_folder:
        log_filepath = init_log_dir().joinpath(logfile)
    else:
        log_filepath = log_folder.joinpath(logfile)
    global_file_handler = logging.FileHandler(log_filepath)
    global_file_handler.setLevel(lvl_file)
    global_file_handler.setFormatter(formatter)
    logger.addHandler(global_file_handler)

    # separate_logfile = f'{name}-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log'
    separate_logfile = f'1-{name}.log'
    if name != 'root':
        if not log_folder:
            log_filepath = init_log_dir().joinpath(separate_logfile)
        else:
            log_filepath = log_folder.joinpath(separate_logfile)
        separate_file_handler = logging.FileHandler(log_filepath)
        separate_file_handler.setLevel(lvl_file)
        separate_file_handler.setFormatter(formatter)
        logger.addHandler(separate_file_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(lvl_stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)  # No STDOUT!!!

    if name == 'root':
        logger.info(
            f'Logger "{name}" logging to {logfile} with log_file level {lvl_file} and log_stdout level {lvl_stdout}.')
    else:
        logger.info(
            f'Logger "{name}" logging to {logfile} and {separate_logfile} with log_file level {lvl_file} and log_stdout level {lvl_stdout}.')
    return logger


loggers = {}


def mylogger(name, log_folder=None) -> logging.Logger:
    """
    Logger factory for getting singleton logger objects.

    :param name: Logger name
    :param log_folder: Logging subfolder inside 'Logs' as string
    :return: <name> logger object
    """

    global global_log_dir
    if 'root' not in loggers:
        print('Creating root logger')
        if log_folder is None:
            global_log_dir = init_log_dir()
        else:
            global_log_dir = init_log_dir(log_folder)
        loggers['root'] = setup_logger('root', log_folder=global_log_dir, lvl_file=logging.INFO,
                                       lvl_stdout=logging.INFO)
        loggers['root'].info(f'Global log folder is {global_log_dir}')
    if name not in loggers:
        loggers['root'].info(f'Creating logger {name}')
        loggers[name] = setup_logger(name, log_folder=global_log_dir, lvl_file=logging.INFO, lvl_stdout=logging.INFO)
    loggers['root'].debug('Using created logger')  # NOTE THIS IS DEBUG LEVEL!
    return loggers[name]


def mylogger_p(name, log_folder=None) -> logging.Logger:
    """
    Parallel logger factory with fixed log folder.

    :param name: Logger name
    :param log_folder: Logging subfolder inside 'Logs' as string
    :return: <name> logger object
    """

    global global_log_dir
    if 'root' not in loggers:
        print('Creating root logger')
        # if log_folder is None:
        #     global_log_dir = init_log_dir()
        # else:
        #     global_log_dir = init_log_dir(log_folder)
        global_log_dir = init_log_dir('0-single-log')
        loggers['root'] = setup_logger('root', log_folder=global_log_dir, lvl_file=logging.INFO,
                                       lvl_stdout=logging.INFO)
        loggers['root'].info(f'Global log folder is {global_log_dir}')
    if name not in loggers:
        loggers['root'].info(f'Creating logger {name}')
        loggers[name] = setup_logger(name, log_folder=global_log_dir, lvl_file=logging.INFO, lvl_stdout=logging.INFO)
    loggers['root'].debug('Using created logger')  # NOTE THIS IS DEBUG LEVEL!
    return loggers[name]


if __name__ == "__main__":
    a = mylogger('TEST')
    a.info('this is test1')
    b = mylogger('TEST')
    print(a is b)
    mylogger('TEST').info('this is test 2')
