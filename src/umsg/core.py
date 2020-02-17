# Copyright © 2020 R.A. Stern
# SPDX-License-Identifier: LGPL-3.0-or-later

import logging
import logging.handlers
import sys

from .util import _caller

this = sys.modules[__name__]

__profiles = {}

profile_keys = [
    'logger',
    'logger_name',
    'level',
    'date_format',
    'msg_format',
    'msg_prefix',
    'msg_prefix_format',
    'exc_info',
    'stack_info',
    'propagate',
    'verbose'
]

DEFAULT_LOGGER = None
""":py:class:`logging.Logger`: Default logger instance. Created when initialized by :py:func:`umsg.init`."""

DEFAULT_LOGGER_NAME = None
"""str: Default logger name. Module name is used if not defined."""

DEFAULT_LEVEL = logging.INFO
"""int: Default logging level to set the logger to."""

DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
"""str: Default logging date format."""

DEFAULT_MSG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
"""str: Default logging record message format."""

DEFAULT_MSG_PREFIX = None
"""str: Default message text prefix for logged message."""

DEFAULT_MSG_PREFIX_FORMAT = '[{prefix}] '
"""str: Default message text prefix `format <https://docs.python.org/3/library/string.html#format-string-syntax>`_ string."""

DEFAULT_EXC_INFO = False
"""bool: Default message exc_info setting."""

DEFAULT_STACK_INFO = False
"""bool: Default message stack_info setting."""

DEFAULT_PROPAGATE = False
"""bool: Default log propagation."""

DEFAULT_VERBOSE = False
"""bool: Default verbose mode."""


# -------------------------------------------------------------------- Classes -
class Profile:

    __slots__ = profile_keys

    def __init__(self):
        for k in profile_keys:
            setattr(self, k, getattr(this, 'DEFAULT_'+k.upper(), None))

    @property
    def mode(self):
        return self.level

    @mode.setter
    def mode(self, value):
        self.level = value


# ------------------------------------------------------------------ Functions -
def _init_profile():
    caller = _caller()
    # idempotent operator
    if caller not in this.__profiles:
        this.__profiles[caller] = Profile()

    return caller


def get_attr(name):
    """Get profile logging attribute.

    Retrieve the current module's logging profile attribute specified. If
    the logging profile does not exist, it will be created with the default
    values.

    Parameters:
        name (str): Name of the attribute to retrieve.

    Returns:
        The attribute value or ``None``.
    """
    module = _init_profile()

    return getattr(this.__profiles[module], name, None)


def set_attr(name, value):
    """Set profile logging attribute.

    Set the current module's logging profile attriube specified to the value
    given. If the logging profile does not exist, it will first be created with
    the default values, and then updated.

    Parameters:
        name (str): Name of the attribute to set.
        value: Value to set the attribute to.
    """
    module = _init_profile()

    setattr(this.__profiles[module], name, value)


def init(**kwargs):
    """Initialize logging based on module profile.

    Initialize the logging mechanism based on the current module's profile settings.
    If the module profile does not exist, it will first be created with the
    default values, and then initialized. The logger name will be set to the
    module name if the value is ``None``. :py:func:`init` accepts all profile
    attributes as parameters at call time. All values given will be recorded
    in the profile.

    Parameters:
        logger (:py:class:`logging.Logger`, optional): Logger object.
        logger_name (str, optional): Logger name.
        level (str or int, optional): Logging level to set the `logger` to.
        mode (str or int, optional): Alias for `level`, provided for compatibility.
        date_format (str, optional): Logging date format.
        msg_format (str, optional): Logging record message format.
        msg_prefix (str, optional): Custom prefix to prepend to logging message
            string.
        msg_prefix_format (str, optional): Custom prefix format string.
        exc_info (bool, optional): exc_info setting. If custom exc_info is desired
            in the form of an exception tuple, this will need to be supplied with
            the actual log message call. See :py:func:`_msg`.
        stack_info (bool, optional): stack_info setting.
        propagate (bool, optional): Propagate logging.
        verbose (bool, optional): Send messages to console instead of the logger.

    """
    module = _init_profile()

    # make init idempotent
    if get_attr('logger') is not None:
        return get_attr('logger')

    if 'logger_name' not in kwargs:
        kwargs['logger_name'] = get_attr('logger_name') or module

    # set any profile attributes received
    for k, v in kwargs.items():
        set_attr(k, v)

    logger = logging.getLogger(get_attr('logger_name'))
    logger.addHandler(logging.NullHandler())
    logger.setLevel(get_attr('level'))
    logger.propagate = get_attr('propagate')

    set_attr('logger', logger)

    return logger


def log(msg, level=None, prefix=None, logger=None, exc_info=False,
        stack_info=False, extra=None,  end='\n'):
    """Logs the given message.

    Notes:
        This function is an alias for :py:func:`_msg` in order to provide a PEP8
        compliant name.
    """
    _msg(msg=msg, level=level, prefix=prefix, logger=logger, exc_info=exc_info,
         stack_info=stack_info, extra=extra, end=end)


def _msg(msg, level=None, prefix=None, logger=None, exc_info=False,
         stack_info=False, extra=None, end='\n'):
    """Base log message facilitator.

    Parameters:
        msg (str): Message to be logged.
        level (str or int, optional): Logging level to use. Logging levels may
            be provided as either a string literal, or as a standard :py:mod:`logging`
            library `logging level <https://docs.python.org/3/library/logging.html#logging-levels>`_
            enum or direct numeric value. Custom levels are not supported.
            (Default: 'info')
        prefix (str, optional): Message prefix to apply. This will override any
            prefix defined in the profile. (Default: profile value).
        logger (:py:class:`logging.Logger`, optional): Specific logger to send
            the message to. This will override the logger value defined in the
            profile. (Default: profile value)
        exc_info (bool or tuple, optional): If an exception tuple (in the format
            returned by :py:func:`sys.exc_info`) or an exception instance is
            provided, it is used; otherwise, :py:func:`sys.exc_info` is called
            to get the exception information. (Default: ``False``)
        stack_info (bool or tuple, optional): If true, stack information is added
            to the logging message, including the actual logging call; the same
            as the standard `logging facilities <https://docs.python.org/3/library/logging.html#logging.debug>`_.
            (Default: ``False``)
        extra (dict, optional): Dictionary of user-defined attributes. These are
            generally parameters to the :py:class:`~logging.Formatter` as would
            be passed to the standard `logging facilities <https://docs.python.org/3/library/logging.html#logging.debug>`_.
        end (str, optional): Final character appended to printed messages in
            `Verbose` mode only. This is passed to the :py:func:`print` function.
            (Default: '\\\\n')
    """
    try:
        level = level.lower()
    except AttributeError:
        if level not in (10, 20, 30, 40, 50):
            level = 'info'

    logger = logger if logger is not None else get_attr('logger')
    prefix = prefix if prefix is not None else get_attr('msg_prefix')
    exc_info = exc_info if exc_info is not None else get_attr('exc_info')
    stack_info = stack_info if stack_info is not None else get_attr('stack_info')

    if level == 'verbose' or get_attr('verbose'):
        print(msg, end=end, flush=True)
    else:
        if prefix:
            msg = get_attr('msg_prefix_format').format(prefix=prefix) + msg

        if level in ('crit', 'critical', logging.CRITICAL):
            logger.critical(msg, exc_info=exc_info, stack_info=stack_info, extra=extra)
        elif level in ('error', logging.ERROR):
            logger.error(msg, exc_info=exc_info, stack_info=stack_info, extra=extra)
        elif level in ('warn', 'warning', logging.WARNING):
            logger.warning(msg, exc_info=exc_info, stack_info=stack_info, extra=extra)
        elif level in ('debug', logging.DEBUG):
            logger.debug(msg, exc_info=exc_info, stack_info=stack_info, extra=extra)
        else:
            logger.info(msg, exc_info=exc_info, stack_info=stack_info, extra=extra)
