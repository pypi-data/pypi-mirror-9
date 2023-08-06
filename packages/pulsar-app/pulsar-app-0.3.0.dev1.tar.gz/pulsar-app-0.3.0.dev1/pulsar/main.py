import logging
from logging.config import fileConfig

import os
import functools
import time
import sys
from six.moves import configparser

try:
    import yaml
except ImportError:
    yaml = None

try:
    from daemonize import Daemonize
except ImportError:
    Daemonize = None

# Vaguely Python 2.6 compatibile ArgumentParser import
try:
    from argparser import ArgumentParser
except ImportError:
    from optparse import OptionParser

    class ArgumentParser(OptionParser):

        def __init__(self, **kwargs):
            self.delegate = OptionParser(**kwargs)

        def add_argument(self, *args, **kwargs):
            if "required" in kwargs:
                del kwargs["required"]
            return self.delegate.add_option(*args, **kwargs)

        def parse_args(self, args=None):
            (options, args) = self.delegate.parse_args(args)
            return options


from paste.deploy.loadwsgi import ConfigLoader

log = logging.getLogger(__name__)

REQUIRES_DAEMONIZE_MESSAGE = "Attempted to use Pulsar in daemon mode, but daemonize is unavailable."

PULSAR_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if "PULSAR_CONFIG_DIR" in os.environ:
    PULSAR_CONFIG_DIR = os.path.abspath(os.environ["PULSAR_CONFIG_DIR"])
else:
    PULSAR_CONFIG_DIR = PULSAR_ROOT_DIR

DEFAULT_INI_APP = "main"
DEFAULT_INI = "server.ini"
DEFAULT_APP_YAML = "app.yml"
DEFAULT_MANAGER = "_default_"

DEFAULT_PID = "pulsar.pid"
DEFAULT_VERBOSE = True
DESCRIPTION = "Daemonized entry point for Pulsar services."


def load_pulsar_app(
    config_builder,
    config_env=False,
    log=None,
    **kwds
):
    # Allow specification of log so daemon can reuse properly configured one.
    if log is None:
        log = logging.getLogger(__name__)

    # If called in daemon mode, set the ROOT directory and ensure Pulsar is on
    # sys.path.
    if config_env:
        try:
            os.chdir(PULSAR_ROOT_DIR)
        except Exception:
            log.exception("Failed to chdir")
            raise
        try:
            sys.path.append(PULSAR_ROOT_DIR)
        except Exception:
            log.exception("Failed to add Pulsar to sys.path")
            raise

    config_builder.setup_logging()
    config = config_builder.load()

    config.update(kwds)
    import pulsar.core
    pulsar_app = pulsar.core.PulsarApp(**config)
    return pulsar_app


def app_loop(args, log):
    pulsar_app = _app(args, log)
    sleep = True
    while sleep:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            sleep = False
        except SystemExit:
            sleep = False
        except Exception:
            pass
    try:
        pulsar_app.shutdown()
    except Exception:
        log.exception("Failed to shutdown Pulsar application")
        raise


def _app(args, log):
    try:
        config_builder = PulsarConfigBuilder(args)
        pulsar_app = load_pulsar_app(
            config_builder,
            config_env=True,
            log=log,
        )
    except BaseException:
        log.exception("Failed to initialize Pulsar application")
        raise
    return pulsar_app


def absolute_config_path(path, config_dir):
    if path and not os.path.isabs(path):
        path = os.path.join(config_dir, path)
    return path


def _find_default_app_config(*config_dirs):
    for config_dir in config_dirs:
        app_config_path = os.path.join(config_dir, DEFAULT_APP_YAML)
        if os.path.exists(app_config_path):
            return app_config_path
    return None


def load_app_configuration(ini_path=None, app_conf_path=None, app_name=None, local_conf=None, config_dir=PULSAR_CONFIG_DIR):
    """
    """
    if ini_path and local_conf is None:
        local_conf = ConfigLoader(ini_path).app_context(app_name).config()
    local_conf = local_conf or {}
    if app_conf_path is None and "app_config" in local_conf:
        app_conf_path = absolute_config_path(local_conf["app_config"], config_dir)
    elif ini_path:
        # If not explicit app.yml file found - look next to server.ini -
        # be it in pulsar root, some temporary staging directory, or /etc.
        app_conf_path = _find_default_app_config(
            os.path.dirname(ini_path),
        )
    if app_conf_path:
        if yaml is None:
            raise Exception("Cannot load confiuration from file %s, pyyaml is not available." % app_conf_path)

        with open(app_conf_path, "r") as f:
            app_conf = yaml.load(f) or {}
            local_conf.update(app_conf)

    return local_conf


def find_ini(supplied_ini, config_dir):
    if supplied_ini:
        return supplied_ini

    # If not explicitly supplied an ini, check server.ini and then
    # just resort to sample if that has not been configured.
    for guess in ["server.ini", "server.ini.sample"]:
        ini_path = os.path.join(config_dir, guess)
        if os.path.exists(ini_path):
            return ini_path

    return guess


class PulsarConfigBuilder(object):
    """ Generate paste-like configuration from supplied command-line arguments.
    """

    def __init__(self, args=None, **kwds):
        config_dir = kwds.get("config_dir", None) or PULSAR_CONFIG_DIR
        ini_path = kwds.get("ini_path", None) or (args and args.ini_path)
        app_conf_path = kwds.get("app_conf_path", None) or (args and args.app_conf_path)
        # If given app_conf_path - use that - else we need to ensure we have an
        # ini path.
        if not app_conf_path:
            ini_path = find_ini(ini_path, config_dir)
            ini_path = absolute_config_path(ini_path, config_dir=config_dir)
        self.config_dir = config_dir
        self.ini_path = ini_path
        self.app_conf_path = app_conf_path
        self.app_name = kwds.get("app") or (args and args.app) or DEFAULT_INI_APP

    @classmethod
    def populate_options(cls, arg_parser):
        arg_parser.add_argument("-c", "--config_dir", default=None)
        arg_parser.add_argument("--ini_path", default=None)
        arg_parser.add_argument("--app_conf_path", default=None)
        arg_parser.add_argument("--app", default=DEFAULT_INI_APP)
        # daemon related options...
        arg_parser.add_argument("-d", "--daemonize", default=False, help="Daemonzie process", action="store_true")
        arg_parser.add_argument("--daemon-log-file", default=None, help="log file for daemon script ")
        arg_parser.add_argument("--pid-file", default=DEFAULT_PID, help="pid file (default is %s)" % DEFAULT_PID)

    def load(self):
        config = load_app_configuration(
            config_dir=self.config_dir,
            ini_path=self.ini_path,
            app_conf_path=self.app_conf_path,
            app_name=self.app_name
        )
        return config

    def setup_logging(self):
        if not self.ini_path:
            # TODO: should be possible can configure using dict.
            return
        raw_config = configparser.ConfigParser()
        raw_config.read([self.ini_path])
        # https://github.com/mozilla-services/chaussette/pull/32/files
        if raw_config.has_section('loggers'):
            config_file = os.path.abspath(self.ini_path)
            fileConfig(
                config_file,
                dict(__file__=config_file, here=os.path.dirname(config_file))
            )

    def to_dict(self):
        return dict(
            config_dir=self.config_dir,
            ini_path=self.ini_path,
            app_conf_path=self.app_conf_path,
            app=self.app_name
        )


class PulsarManagerConfigBuilder(PulsarConfigBuilder):

    def __init__(self, args=None, **kwds):
        super(PulsarManagerConfigBuilder, self).__init__(args=args, **kwds)
        self.manager = kwds.get("manager", None) or (args and args.manager) or DEFAULT_MANAGER

    def to_dict(self):
        as_dict = super(PulsarManagerConfigBuilder, self).to_dict()
        as_dict["manager"] = self.manager
        return as_dict

    @classmethod
    def populate_options(cls, arg_parser):
        PulsarConfigBuilder.populate_options(arg_parser)
        arg_parser.add_argument("--manager", default=DEFAULT_MANAGER)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    arg_parser = ArgumentParser(description=DESCRIPTION)
    PulsarConfigBuilder.populate_options(arg_parser)
    args = arg_parser.parse_args(argv)

    pid_file = args.pid_file

    log.setLevel(logging.DEBUG)
    log.propagate = False

    if args.daemonize:
        if Daemonize is None:
            raise ImportError(REQUIRES_DAEMONIZE_MESSAGE)

        keep_fds = []
        if args.daemon_log_file:
            fh = logging.FileHandler(args.daemon_log_file, "w")
            fh.setLevel(logging.DEBUG)
            log.addHandler(fh)
            keep_fds.append(fh.stream.fileno())
        else:
            fh = logging.StreamHandler(sys.stderr)
            fh.setLevel(logging.DEBUG)
            log.addHandler(fh)

        daemon = Daemonize(
            app="pulsar",
            pid=pid_file,
            action=functools.partial(app_loop, args, log),
            verbose=DEFAULT_VERBOSE,
            logger=log,
            keep_fds=keep_fds,
        )
        daemon.start()
    else:
        app_loop(args, log)

if __name__ == "__main__":
    main()
