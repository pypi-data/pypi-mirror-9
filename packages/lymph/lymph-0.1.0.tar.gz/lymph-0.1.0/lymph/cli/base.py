import abc
import six
import textwrap
import pkg_resources
import logging


logger = logging.getLogger(__name__)


docstring_format_vars = {k: textwrap.dedent(v).strip() for k, v in six.iteritems({
    'COMMON_OPTIONS': """
Common Options:
  --config=<file>, -c <file>   Load configuration from the given path.
  --help, -h                   Print this help message and exit.
  --logfile=<file>             Redirect log output to the given file.
  --loglevel=<level>           Set the log level to one of DEBUG, INFO, WARNING,
                               ERROR. [default: WARNING]
  --version                    Show the lymph version and exit.
  --color                      Force colored output.
  --no-color                   Disable colored output.
    """,
    'INSTANCE_OPTIONS': """
Instance Options:
  --isolated, -i               Don't register this service.
  --port=<port>, -p <port>     Use this port for the RPC endpoint.
  --ip=<address>               Use this IP for all sockets.
  --guess-external-ip, -g      Guess the public facing IP of this machine and
                               use it instead of the provided address.
  --reload                     Automatically stop the service when imported
                               python files in the current working directory
                               change. The process will be restarted by the
                               node. Do not use this in production.
    """,
})}


def format_docstring(doc):
    return textwrap.dedent(doc).format(**docstring_format_vars).strip()


@six.add_metaclass(abc.ABCMeta)
class Command(object):
    needs_config = True
    short_description = ''

    def __init__(self, args, config, terminal):
        self.args = args
        self.config = config
        self.terminal = terminal

    @classmethod
    def get_help(cls):
        return format_docstring(cls.__doc__)

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError


class ListCommand(Command):
    """
    Usage: lymph list [options]

    {COMMON_OPTIONS}
    """

    short_description = 'List available commands.'
    needs_config = False

    def run(self):
        for name, cls in six.iteritems(get_command_classes()):
            print(u'%-15s   %s' % (name, cls.short_description))


_command_class_cache = None


def get_command_classes():
    global _command_class_cache
    if _command_class_cache is None:
        _command_class_cache, entry_points = {}, {}
        for entry_point in pkg_resources.iter_entry_points('lymph.cli'):
            name = entry_point.name
            if name in entry_points:
                logger.error('ignoring duplicate command definition for %s (already installed: %s)', entry_point, entry_points[name])
                continue
            entry_points[name] = entry_point
            cls = entry_point.load()
            cls.name = name
            _command_class_cache[name] = cls
    return _command_class_cache


def get_command_class(name):
    return get_command_classes()[name]

