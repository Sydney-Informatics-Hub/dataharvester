import datetime
import logging
import os


def logging_addLevel(levelName, levelNum, methodName=None):
    """Add new logging level to `logger`

    Credit to https://stackoverflow.com/a/35804945

    Args:
        levelName (_type_): Name of the logging level.
        levelNum (_type_): Numeric value of the logging level.
        methodName (_type_, optional): Name of the method to call. Defaults to None.

    Example:
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5
    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))

    # http://stackoverflow.com/q/2183233/2988730,
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


# =============================================================================
# Create new logging level that is between INFO and WARNING
# TODO: figure out where to put this?
logging_addLevel("PRINT", logging.INFO + 5)
# =============================================================================


def setup(path="data/debug", level="print"):
    """Set up the logging system for the AgReFed Data Harvester.

    Note that because this function is custom, 3 levels can be selected: "info", "print",
    "warning". Obviously, other levels are accessible, just not used (we assume that any level
    higher than WARNING should be in the log file, and not printed).

    Args:
        path (str, optional): path to log file. Defaults to "data/log".
        level (bool, optional): debug level. Defaults to "print". Valid options are "info", "print", and "warning".
    """

    printf = "%(message)s"  # print format
    logf = "%(asctime)s %(levelname)-8s - %(message)s"  # log format

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Validate directory, create if necessary
    dir = os.path.normpath(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Generate logfile
    logfile = os.path.join(dir, datetime.date.today().strftime("%Y-%m-%d") + ".log")

    # Log to file settings
    file = logging.FileHandler(logfile)
    fileformat = logging.Formatter(logf)
    file.setLevel(logging.INFO)
    file.setFormatter(fileformat)

    # Log to console settings
    stream = logging.StreamHandler()
    streamformat = logging.Formatter(printf)
    if level == "info":
        stream.setLevel(logging.INFO)
    elif level == "print":
        stream.setLevel(logging.PRINT)
    elif level == "warning":
        stream.setLevel(logging.WARNING)
    stream.setFormatter(streamformat)

    # Flush handlers (for compatibility with R)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Then, add handlers
    logger.addHandler(file)
    logger.addHandler(stream)
