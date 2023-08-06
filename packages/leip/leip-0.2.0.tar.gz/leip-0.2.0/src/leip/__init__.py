#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Leip
"""

from __future__ import print_function

import argparse
from collections import defaultdict, OrderedDict
import logging
import logging.config
import importlib
import os
import sys
import textwrap

PY3 = sys.version_info[0] > 2

if PY3:
    import pickle
else:
    import cPickle as pickle

import fantail

try:

    from colorlog import ColoredFormatter
    color_formatter = ColoredFormatter(
        "%(green)s#%(name)s %(log_color)s%(levelname)-8s%(reset)s "+
        "%(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={'DEBUG':    'cyan',
                    'INFO':     'green',
                    'WARNING':  'yellow',
                    'ERROR':    'red',
                    'CRITICAL': 'red'})

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(color_formatter)
    logging.getLogger('').addHandler(stream_handler)
except ImportError:
    logformat = "%(name)s %(levelname)s|%(name)s|%(message)s"
    logging.basicConfig(format=logformat)


lg = logging.getLogger(__name__)
lg.setLevel(logging.DEBUG)


#thanks: http://tinyurl.com/mznq746
class ArgumentParserError(Exception): pass
class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


# hack to quickly get the verbosity set properly:
# if '-v' in sys.argv:
#     lg.setLevel(logging.DEBUG)
# elif '-q' in sys.argv:
#     lg.setLevel(logging.WARNING)
# else:
lg.setLevel(logging.INFO)

# cache config files
CONFIG = {}


def get_config(name,
               package_name=None,
               rehash=False,
               clear_before_rehash=True
               ):

    global CONFIG

    if package_name is None:
        package_name = name

    if not rehash and name in CONFIG:
        return CONFIG[name]

    conf_dir = os.path.join(os.path.expanduser('~'), '.config', name)

    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)

    conf_location = get_conf_pickle_location(name)

    db_existed = (os.path.exists(conf_location) and
                  os.path.getsize(conf_location) > 0)

    if db_existed:
        lg.debug("opening cached configuration: %s", conf_location)
        with open(conf_location, 'rb') as F:
            try:
                conf = pickle.load(F)
            except ValueError as e:
                if 'unsupported pickle protocol' in e.message:
                    conf = fantail.Fantail()
                    db_existed=False
                else:
                    raise
    else:
        conf = fantail.Fantail()

    CONFIG[name] = conf

    if not rehash and db_existed:
        lg.debug("finished getting conf - returning cached")
        return conf

    # Ok - either the path did not exist - or - a rehash is required

    # if a clear is requested - create a clean empty object
    if clear_before_rehash:
        conf = fantail.Fantail()

    # From where to read configuration files???
    conf_fof = os.path.join(conf_dir, 'config.locations')

    if os.path.exists(conf_fof):
        conflocs = load_conf_locations(conf_fof)
    else:
        conflocs = OrderedDict()
        conflocs['package'] = 'pkg://{}/etc/'.format(package_name)
        conflocs['system'] = '/etc/{}/'.format(name)
        conflocs['user'] = \
            os.path.join(os.path.expanduser('~'),
                         '.config', name, 'config' + '/')
        save_conf_locations(conf_fof, conflocs)

    for name, location in conflocs.items():
        lg.debug("loading config '{}': {}".format(name, location))
        conf.update(fantail.load(location))

    with open(conf_location, 'wb') as F:
        pickle.dump(conf, F)

    return conf


def set_local_config(app, key, value):

    app.conf[key] = value
    with open(get_conf_pickle_location(app.name), 'wb') as F:
        pickle.dump(app.conf, F)

    localconf = get_local_config_file(app.name)
    localconf[key] = value
    save_local_config_file(localconf, app.name)


def get_conf_pickle_location(name):
    conf_dir = os.path.join(os.path.expanduser('~'), '.config', name)
    return os.path.join(conf_dir, '{}.config.pickle'.format(name))


def get_local_config_filename(name):
    return os.path.join(
        os.path.expanduser('~'),
        '.config', name, 'config', '_local.config')

def get_cache_dir(name, *args):

    cd = os.path.join(
            os.path.expanduser('~'),
            '.cache', name)
    if args:
        cd = os.path.join(cd, *args)

    if not os.path.exists(cd):
        os.makedirs(cd)
    return cd

def get_local_config_file(name):
    fn = get_local_config_filename(name)
    if os.path.exists(fn):
        return fantail.yaml_file_loader(fn)
    else:
        return fantail.Fantail()


def save_local_config_file(lconf, name):
    fn = get_local_config_filename(name)
    fnd = os.path.dirname(fn)
    if not os.path.exists(fnd):
        os.makedirs(fnd)
    fantail.yaml_file_save(lconf, fn)


def get_conf_locations_fof(name):
    conf_dir = os.path.join(os.path.expanduser('~'), '.config', name)
    conf_fof = os.path.join(conf_dir, 'config.locations')
    return conf_fof


def load_conf_locations(conf_fof):
    conflocs = OrderedDict()
    with open(conf_fof) as F:
        for line in F:
            name, location = line.split()
            conflocs[name] = location
    return conflocs


def save_conf_locations(conf_fof, conflocs):
    with open(conf_fof, 'w') as F:
        for name, location in conflocs.items():
            F.write("{}\t{}\n".format(name, location))


class app(object):

    def __init__(self,
                 name=None,
                 package_name=None,
                 config_files=None,
                 set_name='conf',
                 rehash_name='rehash',
                 delay_load_plugins=False,
                 disable_commands=False):
        """

        :param name: base name of the applications
        :type name: string
        :param config_files: list of configuration files, if ommitted
             the app defaults to `/etc/<NAME>.yaml` and
             `~/.config/<NAME>/config.yaml`. The order is important, the last
             config file is the one to which changes will be saved
        :type config_files: a list of tuples: (id, filename)
        :param set_name: name of the command to set new values,
           if set to None, no set function is available. Default='set'
        :type set_name: string
        :param disable_commands: Disable all command/subcommand &
           argparse related functionality - leaving the user with
           a configurable, hookable & pluginable core app.

        """
        lg.debug("Starting Leip app")

        if name is None:
            name = os.path.basename(sys.argv[0])
            
        if package_name is None:
            package_name = name

        self.name = name
        self.set_name = set_name
        self.package_name = package_name

        self.config_files = config_files

        self.leip_on_parse_error = None

        self.leip_commands = {}
        self.leip_subparsers = {}
        self.plugins = {}
        self.disable_commands = disable_commands

        self.hooks = defaultdict(list)
        self.hookstore = {}
        
        if not disable_commands:
            self.parser = ThrowingArgumentParser()

            self.parser.add_argument('-v', '--verbose', action='store_true')
            self.parser.add_argument('-q', '--quiet', action='store_true')
            self.parser.add_argument('--profile', action='store_true',
                                     help=argparse.SUPPRESS)

            self.subparser = self.parser.add_subparsers(
                title='command', dest='command',
                help='"{}" command to execute'.format(name))

        # contains transient data - execution specific
        self.trans = fantail.Fantail()

        # contains configuration data
        self.conf = get_config(self.name,
                               package_name=self.package_name)

        # now that we have configuration info - see if there is
        # a logging branch that we can feed to the logging module

        try:
            if 'logging' in self.conf:
                logging.config.dictConfig(self.conf['logging'])
        except Exception as e:
            lg.warning("unable to load logging configuration")
            lg.warning(str(e))

        if not delay_load_plugins:
            self.load_plugins()

            
    def load_plugins(self):
        # check for and load plugins
        plugins = self.conf['plugin']
        for plugin_name in plugins:

            plugin = plugins[plugin_name]

            lg.debug("loading plugin %s" % plugin_name)
            module_name = plugin.get('module')
            if not module_name:
                module_name = '{}.plugin.{}'.format(self.name, plugin_name)
                lg.debug("guessing module name: %s", module_name)

            enabled = plugin.get('enabled', True)
            if not enabled:
                continue

            lg.debug("attempting to load plugin from module {0}".format(
                module_name))
            try:
                mod = importlib.import_module(module_name)
            except ImportError as e:
                lg.error('Cannot import %s module "%s" (%s)',
                         self.name, plugin_name, module_name)
                lg.error('%s', e)
                continue

            self.plugins[plugin_name] = mod
            self.discover(mod)

        # register command run as a hook
        def _run_command(app):

            command = self.trans['args'].command

            profile = self.trans['args'].profile

            # if profile:
            #     lg.warning("running profiler!")
            #     import cProfile
            #     import os
            #     import pstats
            #     import tempfile
            #     pr = cProfile.Profile()
            #     pr.enable()
            #     app.run()
            #     pr.disable()
            #     handle = tempfile.NamedTemporaryFile(
            #         delete=False, dir=os.getcwd(), prefix='Mad2.', suffix='.profiler')
            #     sortby = 'cumulative'
            #     ps = pstats.Stats(pr, stream=handle).sort_stats(sortby)
            #     ps.print_stats()
            #     handle.close()

            if command is None:
                self.parser.print_help()
                sys.exit(0)

            lg.debug("run command: {}".format(command))
            if command in self.leip_subparsers:
                subcommand = getattr(self.trans['args'], command)
                function = self.leip_subparsers[command][subcommand]
                function(self, self.trans['args'])
            else:
                func = self.leip_commands[command]
                lg.debug("run function: {}".format(func))
                func(self, self.trans['args'])

        # register parse arguments as a hook
        def _prep_args(app):
            try:
                args = self.parser.parse_args()
            except ArgumentParserError as e:
                #invalid call - see if there is an overriding function
                #to capture invalid calls
                message = str(e)
                if app.leip_on_parse_error is None:
                    super(ThrowingArgumentParser,
                          self.parser).error(message)
                else:
                    lg.debug("parse error: %s", message)
                    rv = app.leip_on_parse_error(app, e)

                    #if the on_parse_error function returns a non-zero
                    #number the error is raised after all
                    if rv != 0:
                        super(ThrowingArgumentParser,
                              self.parser).error(message)
                    exit(0)

            self.trans['args'] = args
            rootlogger = logging.getLogger()
            if self.trans['args'].verbose:
                rootlogger.setLevel(logging.DEBUG)
            elif self.trans['args'].quiet:
                rootlogger.setLevel(logging.WARNING)

        # hook run order
        self.hook_order = ['prepare', 'run', 'finish']

        if not self.disable_commands:
            self.register_hook('run', 50, _run_command)
            self.register_hook('prepare', 50, _prep_args)

        # discover locally
        self.discover(globals())

    def cache_dir(self, group=None):
        """
        Return a (created) cache directory for this app
        """
        return get_cache_dir(self.name, group)

    def discover(self, mod):
        """
        discover all hooks & commands in the provided module or
        module namespace (globals())

        :param mod: an imported module or a globals dict
        """

        if isinstance(mod, dict):
            mod_objects = mod
        else:
            mod_objects = mod.__dict__

        self.run_init_hook(mod_objects)
        self.discover_2(mod_objects)

    def run_init_hook(self, mod_objects):
        """
        Run prediscovery initialization hook for this module.

        This might allow, for example, flexible creation of functions
        to be discovered later on.

        For a hook to be executed as a prediscovery init hook, it needs to be
        decorated with: ''@leip.init''
        """

        leip_init_hook = None

        for obj_name in mod_objects:
            obj = mod_objects[obj_name]

            if isinstance(obj, fantail.Fantail):
                continue

            # see if this is a function decorated as hook
            if hasattr(obj, '__call__') and \
                    hasattr(obj, '_leip_init_hook'):
                leip_init_hook = obj

        if not leip_init_hook is None:
            # execute init_hook - with the app - so
            # the module has access to configuration
            leip_init_hook(self)

    def discover_2(self, mod_objects):
        """
        Execute actual discovery of leip tagged functions & hooks
        """

        subcommands = []

        for obj_name in mod_objects:
            obj = mod_objects[obj_name]

            if isinstance(obj, fantail.Fantail):
                continue

            # if this is not a function - ignore
            if not hasattr(obj, '__call__'):
                continue


            # see if this is a hook
            if hasattr(obj, '__call__') and \
                    hasattr(obj, '_leip_parse_error_hook'):
                self.leip_on_parse_error = obj

            if hasattr(obj, '_leip_hook'):
                hook = obj._leip_hook
                if isinstance(hook, fantail.Fantail):
                    continue
                prio = obj.__dict__.get('_leip_hook_priority', 100)
                lg.debug("discovered hook %s (%d) in %s" % (
                    hook, prio, obj.__name__))
                hookname = obj.__name__
                self.hooks[hook].append(
                    (prio, hookname))
                self.hookstore[(hook, hookname)] = obj

            # see if this may be a command
            if not self.disable_commands:
                if hasattr(obj, '_leip_subcommand'):
                    subcommands.append(obj)
                elif hasattr(obj, '_leip_command'):
                    self.register_command(obj)

        # register subcommands
        if not self.disable_commands:
            for subcommand in subcommands:
                self.register_command(subcommand)

    def register_command(self, function):

        cname = function._leip_command

        is_subcommand = False
        parent = None
        subcommand_name = getattr(function, '_leip_subcommand', False)
        if subcommand_name:
            is_subcommand = True
            parent = function._leip_parent
            if hasattr(parent, '_leip_is_conf_subparser'):
                parent._leip_command = self.set_name

        is_subparser = False
        is_conf_subparser = False
        if hasattr(function, '_leip_is_subparser') and \
                function._leip_is_subparser:
            is_subparser = True

            if hasattr(function, '_leip_is_conf_subparser'):
                is_conf_subparser = True
                cname = self.set_name
#                function._leip_command = self.set_name
#                subcommand_name = self.set_name


        lg.debug("command %s subp %s subc %s",
                 cname, is_subparser, is_subcommand)
    
        if hasattr(function, '_leip_usage'):
            usage = function._leip_usage
        else:
            usage = None

        lg.debug("discovered command %s, %s", cname, function)
        self.leip_commands[cname] = function

        # create a help text from the docstring - if possible
        _desc = [cname]
        if function.__doc__:
            doc = function.__doc__.strip()
            if '---' in doc:
                doc = doc.split('---', 1)[0].strip()

            _desc = doc.split("\n", 1)

        if len(_desc) == 2:
            short_description, long_description = _desc
        else:
            short_description, long_description = _desc[0], ""

        long_description = textwrap.dedent(long_description)

        if not is_subcommand:
            # regular command:
            cp = self.subparser.add_parser(
                cname, usage=usage, help=short_description,
                description=long_description)

            # if this function is a subparser - add one - so we
            # can later add subcommands
            if is_subparser:
                self.leip_subparsers[cname] = {}
                subp = cp.add_subparsers(title=cname, dest=cname)
                function._leip_subparser = subp
        else:
            parent_name = parent._leip_command
            self.leip_subparsers[parent_name][subcommand_name] = function
            cp = parent._leip_subparser.add_parser(
                subcommand_name, usage=usage,
                help=short_description,
                description=long_description)

        if hasattr(function, '_leip_args'):
            for args, kwargs in function._leip_args:
                cp.add_argument(*args, **kwargs)

        function._leip_command_parser = cp

    def register_hook(self, name, priority, function):
        lg.debug("registering hook {0} / {1}".format(name, function))
        hookname = function.__name__
        self.hookstore[(name, hookname)] = function
        self.hooks[name].append(
            (priority, hookname))

    def run_hook(self, name, *args, **kw):
        """
        Execute hook
        """
        to_run = sorted(self.hooks[name])
        lg.debug("starting hook %s" % name)

        for priority, hookname in to_run:
            #print(priority, func)
            lg.debug("running hook %s" % hookname)
            func = self.hookstore[(name, hookname)]
            
            func(self, *args, **kw)

    def run(self):
        for hook in self.hook_order:
            lg.debug("running hook {}/{}".format(self.name, hook))
            self.run_hook(hook)


#
# Command decorators
#
def command(f):
    """
    Tag a function to become a command - take the function name and
    use it as the name of the command.
    """
    f._leip_command = f.__name__
    f._leip_args = []
    lg.debug("marking function as leip command: %s" % f.__name__)
    return f


def subparser(f):
    """
    Mark this function as being a subparser
    """
    f._leip_command = f.__name__
    f._leip_args = []
    f._leip_is_subparser = True
    lg.debug("marking function as leip subcommand: %s" % f.__name__)
    return f


def subcommand(parent, command_name=None):
    """
    Mark this function as being a subcommand
    """
    def decorator(f):
        lg.debug("marking function as leip subcommand: %s" % command_name)
        f._leip_subcommand = True
        f._leip_parent = parent
        f._leip_subcommand = command_name
        f._leip_command = "{}.{}".format(parent._leip_command, command_name)
        f._leip_args = []
        return f
    return decorator


def commandName(name):
    """
    as command, but provide a specific name
    """
    def decorator(f):
        lg.debug("marking function as leip command: %s" % name)
        f._leip_command = name
        f._leip_args = []
        return f
    return decorator


def usage(usage):
    """
    add a usage string to a command
    """
    def decorator(f):
        lg.debug("adding usage argument {0}".format(usage))
        f._leip_usage = usage
        return f
    return decorator


def arg(*args, **kwargs):
    """
    add an argument to a command - use the full argparse syntax
    """
    def decorator(f):
        lg.debug(
            "adding leip argument {0}, {1}".format(str(args), str(kwargs)))
        f._leip_args.append((args, kwargs))
        return f
    return decorator


def flag(*args, **kwargs):
    """
    Add a flag to (default false - true if specified) any command
    """
    def decorator(f):
        lg.debug("adding leip flag {0}, {1}".format(str(args), str(kwargs)))
        kwargs['action'] = kwargs.get('action', 'store_true')
        kwargs['default'] = kwargs.get('default', False)
        f._leip_args.append((args, kwargs))
        return f
    return decorator


#
# Pre discovery init hook decorators
#
def init(f):
    """
    Mark this function as a pre discovery init hook.get_config.

    Only one per module is expected.
    """
    f._leip_init_hook = f.__name__
    return f

def on_parse_error(f):
    """
    Execute this function on a parse_error

    Only one per applications is expected.
    """
    f._leip_parse_error_hook = f.__name__
    return f


#
# Hook decorators
#
def hook(name, priority=50):
    """
    mark this function as a hook for later execution

    :param name: name of the hook to call
    :type name: string
    :param priority: inidicate how soon this hook must be called.
        Lower means sooner (default: 50)
    :type priority: int
    """
    def _hook(f):
        lg.debug("registering '%s' hook in %s priority %d" % (
            name, f.__name__, priority))
        f._leip_hook = name
        f._leip_hook_priority = priority
        return f

    return _hook


#
# configuration code
#

@subparser
def conf(app, args):
    """
    Manage configuration
    """
    pass  # this function is never called - it's just a placeholder

conf._leip_is_conf_subparser = True


@arg('value', help="value to set it to")
@arg('key', help="key to set")
@subcommand(conf, "set")
def conf_set(app, args):
    """
    set a variable
    """
    app.conf[args.key] = args.value


@arg("key", nargs='?')
@subcommand(conf, "get")
def conf_get(app, args):
    """
    Get the value of a configuration variable
    """
    print(app.conf.get(args.key, ""))


@arg("field", nargs='?')
@subcommand(conf, "find")
def conf_find(app, args):
    """
    Find a key in the configuration
    """
    def _finder(conf, key, prefix=""):
        if key in conf:
            print('{}.{}'.format(prefix, key).strip('.'))
        for k in conf:
            if isinstance(conf[k], dict):
                _finder(conf[k], key,
                        '{}.{}'.format(prefix, k).strip('.'))

    _finder(app.conf, args.field, "")


@arg("prefix", nargs='?')
@subcommand(conf, "show")
def conf_show(app, args):
    """
    list all configuration variables
    """
    if args.prefix:
        data = app.conf[args.prefix]
    else:
        data = app.conf

    if not isinstance(data, fantail.Fantail):
        if data:
            print(data)
        else:
            print('{} has no keys/value'.format(args.prefix))
        exit(0)

    for k in data.keys():
        val = str(data[k])
        if len(val) > 60:
            val = (" ".join(val.split()))[:60] + '...'
        if args.prefix:
            print('{0}.{1} {2}'.format(args.prefix, k, val))
        else:
            print('{0} {1}'.format(k, val))


@arg("prefix", nargs='?')
@subcommand(conf, "keys")
def conf_keys(app, args):
    """
    list all configuration keys, optionally with a prefix
    """
    if args.prefix:
        data = app.conf[args.prefix]
    else:
        data = app.conf

    if not isinstance(data, fantail.Fantail):
        print('{} has no keys'.format(args.prefix))
        if data:
            print("  value: {}...".format(" ".join(data.split())[:50]))
        exit(0)

    for k in data.keys():
        if args.prefix:
            print('{0}.{1}'.format(args.prefix, k))
        else:
            print(k)


@flag('-c', '--clear', help='clear configuration db first')
@subcommand(conf, "rehash")
def conf_rehash(app, args):
    """
    Read & set configuration from the default pacakge data
    """
    app.conf = get_config(
        app.name,
        package_name=app.package_name,
        rehash=True,
        clear_before_rehash=args.clear)


@arg("location", help='location of the configuration data')
@arg("name", help='name')
@subcommand(conf, "addloc")
def _conf_addloc(app, args):
    """
    Add a location to load upon 'conf rehash'
    """
    conf_fof = get_conf_locations_fof(app.name)
    confloc = load_conf_locations(conf_fof)
    confloc[args.name] = args.location
    save_conf_locations(conf_fof, confloc)


@arg("value", help='value')
@arg("name", help='name')
@subcommand(conf, "set")
def _conf_set(app, args):
    """
    Set a configuration value
    """
    curval = app.conf[args.name]
    nval = args.value

    def isint(v):
        try:
            int(v)
            return True
        except ValueError:
            return False

    def isfloat(v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    if nval.lower() == 'true':
        nval = True
    elif nval.lower() == 'false':
        nval = False
    elif isfloat(nval):
        nval = float(nval)
    elif isint(nval):
        nval = int(nval)

    #print("{} {} {}".format(args.name, curval, nval))

    if curval and isinstance(curval, fantail.Fantail):
        lg.info("Cannot overwrite a branch")
        exit(-1)

    app.conf[args.name] = nval
    with open(get_conf_pickle_location(app.name), 'wb') as F:
        pickle.dump(app.conf, F)

    localconf = get_local_config_file(app.name)
    localconf[args.name] = nval
    save_local_config_file(localconf, app.name)
