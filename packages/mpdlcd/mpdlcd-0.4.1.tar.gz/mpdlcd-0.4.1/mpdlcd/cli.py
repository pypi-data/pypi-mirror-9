#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Raphaël Barrois

from __future__ import print_function

from .compat import configparser
from .compat import urllib_parse

import collections
import logging
from logging import handlers as logging_handlers
import optparse
import socket
import time
import sys

from . import enums
from . import lcdrunner
from . import mpdwrapper
from . import display_fields
from . import display_pattern
from . import mpdhooks
from . import utils
from . import __version__

# General
DEFAULT_CONFIG_FILE = '/etc/mpdlcd.conf'

# Display

DEFAULT_REFRESH = 0.5
DEFAULT_LCD_SCREEN_NAME = 'MPD'
DEFAULT_PATTERN = ''
DEFAULT_BACKLIGHT_ON = enums.BACKLIGHT_ON_NEVER

# Connection
DEFAULT_MPD_PORT = 6600
DEFAULT_LCD_PORT = 13666
DEFAULT_LCDPROC_CHARSET = 'iso-8859-1'
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_WAIT = 3
DEFAULT_RETRY_BACKOFF = 2

# Logging
DEFAULT_SYSLOG_ENABLED = False
DEFAULT_LOGLEVEL = 'warning'
DEFAULT_SYSLOG_FACILITY = 'daemon'
DEFAULT_SYSLOG_ADDRESS = '/dev/log'
DEFAULT_LOGFILE = '-'
DEFAULT_DEBUG_MODULES = ''

BASE_CONFIG = {
    'display': {
        'refresh': ('float', DEFAULT_REFRESH),
        'lcdproc_screen': ('str', DEFAULT_LCD_SCREEN_NAME),
        'pattern': ('str', DEFAULT_PATTERN),
        'backlight_on': ('str', DEFAULT_BACKLIGHT_ON),
    },
    'connections': {
        'mpd': ('str', 'localhost:%s' % DEFAULT_MPD_PORT),
        'lcdproc': ('str', 'localhost:%s' % DEFAULT_LCD_PORT),
        'lcdproc_charset': ('str', DEFAULT_LCDPROC_CHARSET),
        'lcdd_debug': ('bool', False),
        'retry_attempts': ('int', DEFAULT_RETRY_ATTEMPTS),
        'retry_wait': ('int', DEFAULT_RETRY_WAIT),
        'retry_backoff': ('int', DEFAULT_RETRY_BACKOFF),
    },
    'logging': {
        'syslog': ('bool', DEFAULT_SYSLOG_ENABLED),
        'loglevel': ('str', DEFAULT_LOGLEVEL),
        'syslog_facility': ('str', DEFAULT_SYSLOG_FACILITY),
        'syslog_address': ('str', DEFAULT_SYSLOG_ADDRESS),
        'logfile': ('str', DEFAULT_LOGFILE),
        'debug': ('str', DEFAULT_DEBUG_MODULES),
    },
}

DEFAULT_PATTERNS = [
    # One line
    u"""{state} {song format="%(artist)s - %(title)s"} {elapsed}""",

    # Two lines
    u"""{song format="%(artist)s",speed=4} {elapsed}\n"""
    u"""{song format="%(title)s",speed=2} {state}""",

    # Three lines
    u"""{song format="%(artist)s",speed=4}\n"""
    u"""{song format="%(album)s - %(title)s",speed=2}\n"""
    u"""{state}  {elapsed} / {total}""",

    # Four lines
    u"""{song format="%(artist)s",speed=4}\n"""
    u"""{song format="%(album)s",speed=4}\n"""
    u"""{song format="%(title)s",speed=2}\n"""
    u"""{elapsed}  {state}  {remaining}""",
]


logger = logging.getLogger('mpdlcd')


Connection = collections.namedtuple('Connection',
    ['hostname', 'port', 'username', 'password'])


def _make_hostport(conn, default_host, default_port, default_user='', default_password=None):
    """Convert a '[user[:pass]@]host:port' string to a Connection tuple.

    If the given connection is empty, use defaults.
    If no port is given, use the default.

    Args:
        conn (str): the string describing the target hsot/port
        default_host (str): the host to use if ``conn`` is empty
        default_port (int): the port to use if not given in ``conn``.

    Returns:
        (str, int): a (host, port) tuple.
    """

    parsed = urllib_parse.urlparse('//%s' % conn)
    return Connection(
        parsed.hostname or default_host,
        parsed.port or default_port,
        parsed.username if parsed.username is not None else default_user,
        parsed.password if parsed.password is not None else default_password,
    )


def _make_lcdproc(lcd_host, lcd_port, retry_config,
        charset=DEFAULT_LCDPROC_CHARSET, lcdd_debug=False):
    """Create and connect to the LCDd server.

    Args:
        lcd_host (str): the hostname to connect to
        lcd_prot (int): the port to connect to
        charset (str): the charset to use when sending messages to lcdproc
        lcdd_debug (bool): whether to enable full LCDd debug
        retry_attempts (int): the number of connection attempts
        retry_wait (int): the time to wait between connection attempts
        retry_backoff (int): the backoff for increasing inter-attempt delay

    Returns:
        lcdproc.server.Server
    """

    class ServerSpawner(utils.AutoRetryCandidate):
        """Spawn the server, using auto-retry."""

        @utils.auto_retry
        def connect(self):
            return lcdrunner.LcdProcServer(
                lcd_host, lcd_port, charset, debug=lcdd_debug)

    spawner = ServerSpawner(retry_config=retry_config, logger=logger)

    try:
        return spawner.connect()
    except socket.error as e:
        logger.error(u'Unable to connect to lcdproc %s:%s.',
            lcd_host, lcd_port)
        raise SystemExit(1)


def _make_patterns(patterns):
    """Create a ScreenPatternList from a given pattern text.

    Args:
        pattern_txt (str list): the patterns

    Returns:
        mpdlcd.display_pattern.ScreenPatternList: a list of patterns from the
            given entries.
    """
    field_registry = display_fields.FieldRegistry()

    pattern_list = display_pattern.ScreenPatternList(
            field_registry=field_registry,
    )
    for pattern in patterns:
        pattern_list.add(pattern.split('\n'))
    return pattern_list


def run_forever(lcdproc='', mpd='', lcdproc_screen=DEFAULT_LCD_SCREEN_NAME,
        lcdproc_charset=DEFAULT_LCDPROC_CHARSET,
        lcdd_debug=False,
        pattern='', patterns=[],
        refresh=DEFAULT_REFRESH,
        backlight_on=DEFAULT_BACKLIGHT_ON,
        retry_attempts=DEFAULT_RETRY_ATTEMPTS,
        retry_wait=DEFAULT_RETRY_WAIT,
        retry_backoff=DEFAULT_RETRY_BACKOFF):
    """Run the server.

    Args:
        lcdproc (str): the target connection (host:port) for lcdproc
        mpd (str): the target connection ([pwd@]host:port) for mpd
        lcdproc_screen (str): the name of the screen to use for lcdproc
        lcdproc_charset (str): the charset to use with lcdproc
        lcdd_debug (bool): whether to enable full LCDd debug
        pattern (str): the pattern to use
        patterns (str list): the patterns to use
        refresh (float): how often to refresh the display
        backlight_on (str): the rules for activating backlight
        retry_attempts (int): number of connection attempts
        retry_wait (int): time between connection attempts
        retry_backoff (int): increase to between-attempts delay
    """
    # Compute host/ports
    lcd_conn = _make_hostport(lcdproc, 'localhost', 13666)
    mpd_conn = _make_hostport(mpd, 'localhost', 6600)

    # Prepare auto-retry
    retry_config = utils.AutoRetryConfig(
        retry_attempts=retry_attempts,
        retry_backoff=retry_backoff,
        retry_wait=retry_wait)

    # Setup MPD client
    mpd_client = mpdwrapper.MPDClient(
        host=mpd_conn.hostname,
        port=mpd_conn.port,
        password=mpd_conn.username,
        retry_config=retry_config,
    )

    # Setup LCDd client
    lcd = _make_lcdproc(lcd_conn.hostname, lcd_conn.port, lcdd_debug=lcdd_debug,
        charset=lcdproc_charset, retry_config=retry_config)

    # Setup connector
    runner = lcdrunner.MpdRunner(mpd_client, lcd,
        lcdproc_screen=lcdproc_screen,
        refresh_rate=refresh,
        retry_config=retry_config,
        backlight_on=backlight_on,
    )

    # Fill pattern
    if pattern:
        # If a specific pattern was given, use it
        patterns = [pattern]
    elif not patterns:
        # If no patterns were given, use the defaults
        patterns = DEFAULT_PATTERNS
    pattern_list = _make_patterns(patterns)

    mpd_hook_registry = mpdhooks.HookRegistry()
    runner.setup_pattern(pattern_list, hook_registry=mpd_hook_registry)

    # Launch
    mpd_client.connect()
    runner.run()

    # Exit
    logging.shutdown()


LOGLEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


def _make_parser():
    parser = optparse.OptionParser(version='%prog ' + __version__)

    # General options
    # ---------------
    parser.add_option('-c', '--config', dest='config',
            help='Read configuration from CONFIG (default: %s)' %
            DEFAULT_CONFIG_FILE, metavar='CONFIG', default=DEFAULT_CONFIG_FILE)
    # End general options

    # Display options
    # ---------------
    group = optparse.OptionGroup(parser, 'Display')
    group.add_option('--pattern', dest='pattern',
            help='Use this PATTERN (lines separated by \\n)',
            metavar='PATTERN', default='')
    group.add_option('--patterns', dest='patterns', action='append',
            help='Register a PATTERN; the actual pattern is chosen according '
            'to screen height.',
            metavar='PATTERN')
    group.add_option('--refresh', dest='refresh', type='float',
            help='Refresh the display every REFRESH seconds (default: %.1fs)' %
                    DEFAULT_REFRESH,
            metavar='REFRESH')
    group.add_option('--lcdproc-screen', dest='lcdproc_screen',
            help='Register the SCREEN_NAME lcdproc screen for mpd status '
            '(default: %s)' % DEFAULT_LCD_SCREEN_NAME,
            metavar='SCREEN_NAME')
    group.add_option('--backlight-on', dest='backlight_on',
            help="Activate backlight always|never|in play mode|in play/pause mode (default: %s)" %
            DEFAULT_BACKLIGHT_ON,
            choices=enums.BACKLIGHT_ON_CHOICES,
            metavar='BACKLIGHT_ON')

    # End display options
    parser.add_option_group(group)

    # Connection options
    # ------------------
    group = optparse.OptionGroup(parser, 'Connection')
    group.add_option('-l', '--lcdproc', dest='lcdproc',
            help='Connect to lcdproc at LCDPROC', metavar='LCDPROC')
    group.add_option('-m', '--mpd', dest='mpd',
            help='Connect to mpd running at MPD', metavar='MPD')
    group.add_option('--lcdproc-charset', dest='lcdproc_charset',
            help='Use CHARSET for communications to lcdproc', metavar='CHARSET')
    group.add_option('--lcdd-debug', dest='lcdd_debug', action='store_true',
            help='Add full debug output of LCDd commands', default=False)

    # Auto-retry
    group.add_option('--retry-attempts', dest='retry_attempts', type='int',
            help='Retry connections RETRY_ATTEMPTS times (default: %d)' %
                    DEFAULT_RETRY_ATTEMPTS,
            metavar='RETRY_ATTEMPTS')
    group.add_option('--retry-wait', dest='retry_wait', type='float',
            help='Wait RETRY_WAIT between connection attempts (default: %.1fs)' %
                    DEFAULT_RETRY_WAIT,
            metavar='RETRY_WAIT')
    group.add_option('--retry-backoff', dest='retry_backoff', type='int',
            help='Increase RETRY_WAIT by a RETRY_BACKOFF factor after each '
                'failure (default: %d)' % DEFAULT_RETRY_BACKOFF,
            metavar='RETRY_BACKOFF')

    # End connection options
    parser.add_option_group(group)

    # Logging options
    # ---------------
    group = optparse.OptionGroup(parser, 'Logging')
    group.add_option('-s', '--syslog', dest='syslog', action='store_true',
            help='Enable syslog logging (default: False)')
    group.add_option('--no-syslog', dest='syslog', action='store_false',
            help='Disable syslog logging (Useful when enabled in config file)')

    group.add_option('--syslog-facility', dest='syslog_facility',
            help='Log into syslog facility FACILITY (default: %s)' %
                    DEFAULT_SYSLOG_FACILITY,
            metavar='FACILITY')

    group.add_option('--syslog-address', dest='syslog_address',
            help='Log into syslog at ADDRESS (default: %s)' %
                    DEFAULT_SYSLOG_ADDRESS,
            metavar='ADDRESS')

    group.add_option('-f', '--logfile', dest='logfile',
            help="Log into LOGFILE ('-' for stderr)", metavar='LOGFILE')

    group.add_option('--loglevel', dest='loglevel', type='choice',
            help='Logging level (%s; default: %s)' %
                    ('/'.join(LOGLEVELS.keys()), DEFAULT_LOGLEVEL),
            choices=LOGLEVELS.keys())
    group.add_option('-d', '--debug', dest='debug',
            help="Log debug output from the MODULES components",
            metavar='MODULES')

    # End logging options
    parser.add_option_group(group)

    return parser


def _setup_logging(syslog=False, syslog_facility=DEFAULT_SYSLOG_FACILITY,
        syslog_address=DEFAULT_SYSLOG_ADDRESS, logfile=DEFAULT_LOGFILE,
        loglevel=DEFAULT_LOGLEVEL, debug='', **kwargs):
    level = LOGLEVELS[loglevel]

    verbose_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s')
    quiet_formatter = logging.Formatter(
            '%(levelname)s %(name)s %(message)s')

    if syslog:
        if syslog_address and syslog_address[0] == '/':
            address = syslog_address
        else:
            syslog_conn = _make_hostport(syslog_address, 'localhost', logging.SYSLOG_UDP_PORT)
            address = (syslog_conn.hostname, syslog_conn.port)
        handler = logging_handlers.SysLogHandler(address, facility=syslog_facility)
        handler.setFormatter(quiet_formatter)

    elif logfile == '-':
        handler = logging.StreamHandler()
        handler.setFormatter(quiet_formatter)

    else:
        handler = logging.FileHandler(logfile)
        handler.setFormatter(verbose_formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    for module in debug.split(','):
        if not module.strip():
            continue
        module_logger = logging.getLogger(module)
        module_logger.setLevel(logging.DEBUG)
        if level != logging.DEBUG:
            # Make sure log messages are displayed
            module_logger.addHandler(handler)
        module_logger.info("Enabling debug")


def _read_config(filename):
    """Read configuration from the given file.

    Parsing is performed through the configparser library.

    Returns:
        dict: a flattened dict of (option_name, value), using defaults.
    """
    parser = configparser.RawConfigParser()
    if filename and not parser.read(filename):
        sys.stderr.write(
            u"Unable to open configuration file %s. Use --config='' to disable "
            u"this warning.\n" % filename)

    config = {}

    for section, defaults in BASE_CONFIG.iteritems():
        # Patterns are handled separately
        if section == 'patterns':
            continue

        for name, descr in defaults.iteritems():
            kind, default = descr
            if section in parser.sections() and name in parser.options(section):
                if kind == 'int':
                    value = parser.getint(section, name)
                elif kind == 'float':
                    value = parser.getfloat(section, name)
                elif kind == 'bool':
                    value = parser.getboolean(section, name)
                else:
                    value = parser.get(section, name)
            else:
                value = default
            config[name] = value

    if 'patterns' in parser.sections():
        patterns = [parser.get('patterns', opt) for opt in parser.options('patterns')]
    else:
        patterns = DEFAULT_PATTERNS
    config['patterns'] = patterns

    return config


def _extract_options(config, options, *args):
    """Extract options values from a configparser, optparse pair.

    Options given on command line take precedence over options read in the
    configuration file.

    Args:
        config (dict): option values read from a config file through
            configparser
        options (optparse.Options): optparse 'options' object containing options
            values from the command line
        *args (str tuple): name of the options to extract
    """
    extract = {}
    for key in args:
        if key not in args:
            continue
        extract[key] = config[key]
        option = getattr(options, key, None)
        if option is not None:
            extract[key] = option
    return extract


def main(argv):
    parser = _make_parser()
    options, args = parser.parse_args(argv)
    base_config = _read_config(options.config)
    if options.loglevel == 'debug':
        print("Base config: %s" % base_config)
        print("With overrides: %s" % _extract_options(base_config, options, *base_config.keys()))

    _setup_logging(**_extract_options(base_config, options,
        'syslog', 'syslog_facility', 'syslog_address',
        'logfile', 'loglevel', 'debug'))
    run_forever(**_extract_options(base_config, options,
        'lcdproc', 'mpd', 'lcdproc_charset', 'lcdproc_screen', 'lcdd_debug',
        'refresh', 'backlight_on',
        'pattern', 'patterns',
        'retry_attempts', 'retry_backoff', 'retry_wait'))
