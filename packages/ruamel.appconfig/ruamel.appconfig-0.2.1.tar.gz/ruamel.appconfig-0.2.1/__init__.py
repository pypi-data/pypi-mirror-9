# coding: utf-8
"""
The application configuration class AppConfig provides
standard location and reading of argparse defaults from
an .ini configuration file


relies on ConfigObj for reading and writing (including comments).
"""

from __future__ import print_function

import os
import sys
import argparse

from configobj import ConfigObj
from argparse import _UNRECOGNIZED_ARGS_ATTR

import ruamel.yaml


def _convert_version(tup):
    """create a PEP 386 pseudo-format conformant string from tuple tup"""
    ret_val = str(tup[0])  # first is always digit
    next_sep = "."  # separator for next extension, can be "" or "."
    for x in tup[1:]:
        if isinstance(x, int):
            ret_val += next_sep + str(x)
            next_sep = '.'
            continue
        first_letter = x[0].lower()
        next_sep = ''
        if first_letter in 'abcr':
            ret_val += 'rc' if first_letter == 'r' else first_letter
        elif first_letter in 'pd':
            ret_val += '.post' if first_letter == 'p' else '.dev'
    return ret_val


version_info = (0, 2, 1)
__version__ = _convert_version(version_info)

del _convert_version


class AppConfig(object):
    """ToDo: update

    derives configuration filename and location from package name

    package_name is also stored to find 'local' configurations based
    on passed in directory name.
    The Config object allows for more easy change to e.g. YAML config files
    """

    class Config(ConfigObj):
        """ Config should have a __getitem__,
        preserve comments when writing
        (write config if changed)
        """
        def __init__(self, file_name, **kw):
            ConfigObj.__init__(self, file_name, *kw)

    class YamlConfig:
        def __init__(self, file_name, **kw):
            self._file_name = file_name
            try:
                self._data = ruamel.yaml.load(
                    open(file_name), ruamel.yaml.RoundTripLoader)
            except IOError:
                self._data = ruamel.yaml.compat.ordereddict()

        def __getitem__(self, key):
            return self._data[key]

        def __setitem__(self, key, val):
            self._data[key] = val

        def setdefault(self, *args, **kw):
            return self._data.setdefault(*args, **kw)

        def write(self):
            ruamel.yaml.dump(
                self._data,
                open(self._file_name, 'w'),
                ruamel.yaml.RoundTripDumper,
            )

    def __init__(self, package_name, **kw):
        """create a config file if no file_name given,
        complain if multiple found"""
        self._package_name = package_name
        self._file_name = None
        warning = kw.pop('warning', None)
        self._parser = parser = kw.pop('parser', None)
        #create = kw.pop('create', True)
        #if not create:
        #    return
        file_name = self.get_file_name(
            kw.pop('filename', None),
            warning=warning,
        )
        if kw.pop('add_save', None):
            self.add_save_defaults(parser)
            if parser._subparsers is not None:
                assert isinstance(parser._subparsers, argparse._ArgumentGroup)
                subparsers = {}  # aliases filtered out
                for spa in parser._subparsers._group_actions:
                    if not isinstance(spa, argparse._SubParsersAction):
                        continue
                    #print ('spa ', type(spa), spa)
                    for key in spa.choices:
                        #print ('key ', key)
                        sp = spa.choices[key]
                        #print ('sp ', type(sp), sp)
                        self.add_save_defaults(sp)
        self._config_kw = kw
        self._config = self.get_config(file_name, **self._config_kw)
        try:
            self._config_dts = os.path.getmtime(file_name)
        except OSError:
            self._config_dts = 0
        argparse._SubParsersAction.__call__ = self.sp__call__
        #super(AppConfig, self).__init__(file_name, **kw)


    def get_config(self, file_name, **config_kw):
        ext = file_name.rsplit('.', 1)[-1]
        if ext in ['yaml', 'yml']:
            return self.YamlConfig(file_name, **self._config_kw)
        if ext in ['ini']:
            return self.Config(file_name, **self._config_kw)

    def get_file_name(self, file_name=None, warning=None, add_save=None):
        if self._file_name:
            return self._file_name
        if warning is None:
            warning = self.no_warning
        add_config_to_parser = False
        if file_name is self.check:
            file_name = None
            if self._parser:
                add_config_to_parser = True
            # check if --config was given on commandline
            for idx, arg in enumerate(sys.argv[1:]):
                if arg.startswith('--config'):
                    if len(arg) > 8 and arg[8] == '=':
                        file_name = arg[9:]
                    else:
                        try:
                            file_name = sys.argv[idx+2]
                        except IndexError:
                            print('--config needs an argument')
                            sys.exit(1)
        expanded_file_names = [os.path.expanduser(x) for x in
                               self.possible_config_file_names]
        #print(expanded_file_names)
        existing = [x for x in expanded_file_names if os.path.exists(x)]
        # possible check for existence of preferred directory and less
        # preferred existing file
        # e.g. empty ~/.config/repo and existing ~/.repo/repo.ini
        if file_name and existing:
            warning("Multiple configuration files", [file_name] + existing)
        elif len(existing) > 1:
            warning("Multiple configuration files:", ', '.join(existing))
        if file_name:
            self._file_name = os.path.expanduser(file_name)
        elif existing:
            self._file_name = existing[0]
        else:
            self._file_name = expanded_file_names[0]
        try:
            dir_name = os.path.dirname(self._file_name)
            os.mkdir(dir_name)
            warning('created directory', dir_name)
        except OSError:
            #warning('did not create directory ', dir_name)
            pass
        if not self.has_config() and add_config_to_parser:
            if '/XXXtmp/' not in self._file_name:
                default_path = self._file_name.replace(
                    os.path.expanduser('~/'), '~/')
            else:
                default_path = self._file_name
            self._parser.add_argument(
                '--config',
                metavar='FILE',
                default=default_path,
                help="set %(metavar)s as configuration file [%(default)s]",
            )
        return self._file_name

    def file_in_config_dir(self, file_name):
        return os.path.join(os.path.dirname(self._file_name), file_name)

    def __getitem__(self, key):
        return self._config[key]

    def get(self, key, default=None):
        try:
            return self._config[key]
        except KeyError:
            return default

    def set_defaults(self):
        _glbl = 'global'
        parser = self._parser
        self._set_section_defaults(self._parser, _glbl)
        if parser._subparsers is None:
            return
        assert isinstance(parser._subparsers, argparse._ArgumentGroup)
        progs = set()
        subparsers = {}  # aliases filtered out
        for sp in parser._subparsers._group_actions:
            if not isinstance(sp, argparse._SubParsersAction):
                continue
            for k, action in sp.choices.iteritems():
                if self.query_add(progs, action.prog):
                    self._set_section_defaults(action, k, glbl=_glbl)

    def _set_section_defaults(self, parser, section, glbl=None):
        defaults = {}
        for action in parser._get_optional_actions():
            if isinstance(action,
                          (argparse._HelpAction,
                           argparse._VersionAction,
                           #SubParsersAction._AliasesChoicesPseudoAction,
                           )):
                continue
            for x in action.option_strings:
                if not x.startswith('--'):
                    continue
                try:
                    # get value based on long-option (without --)
                    # store in .dest
                    defaults[action.dest] = self[section][x[2:]]
                except KeyError:  # not in config file
                    if glbl is not None and \
                       getattr(action, "_global_option", False):
                        try:
                            defaults[action.dest] = self[glbl][x[2:]]
                        except KeyError:  # not in config file
                            pass
                break  # only first --option
        parser.set_defaults(**defaults)

    def has_config(self):
        """check if self._parser has --config already added"""
        if self._parser is not None:
            for action in self._parser._get_optional_actions():
                if '--config' in action.option_strings:
                    return True
        return False

    def parse_args(self, *args, **kw):
        """call ArgumentParser.parse_args and handle --save-defaults"""
        parser = self._parser
        opt = parser._optionals
        #print('paropt', self._parser._optionals, len(opt._actions),
        #      len(opt._group_actions))
        #for a in self._parser._optionals._group_actions:
        #    print('    ', a)
        pargs = self._parser.parse_args(*args, **kw)
        if hasattr(pargs, 'save_defaults') and pargs.save_defaults:
            self.extract_default(opt, pargs)
            #for elem in self._parser._optionals._defaults:
            #    print('elem ', elem)
            if hasattr(parser, '_sub_parser_sel'):
                name, sp = parser._sub_parser_sel
                # print('====sp', sp)
                opt = sp._optionals
                self.extract_default(opt, pargs, name)
            self._config.write()
        return pargs

    def extract_default(self, opt, pargs, name='global'):
        for a in opt._group_actions:
            #print('+++++', name, a)
            if isinstance(a, (argparse._HelpAction,
                              argparse._VersionAction,
                              )):
                continue
            if a.option_strings[0] in ["--config", "--save-defaults"]:
                continue
            #print('    -> ', name, a.dest, a)
            if hasattr(pargs, a.dest):
                sec = self._config.setdefault(name, {})
                sec[a.dest] = getattr(pargs, a.dest)

    @property
    def possible_config_file_names(self, ext=None):
        """return all the paths to check for configuration
        first is the one created if none found"""
        pn = self._package_name
        if ext is None:
            exts = ['.yaml', '.yml', '.ini']
        else:
            exts = [ext]
        #ud = '~'
        ret_val = []
        for ext in exts:
            if sys.platform.startswith('linux'):
                ud = os.environ['HOME']
                ret_val.extend([
                    # ~/.config/repo/repo.ext
                    os.path.join(AppConfig._config_dir(), pn, pn + ext),
                    # ~/.repo/repo.ext
                    os.path.join(ud, '.' + pn, pn + ext),
                    # ~/.repo.ext
                    os.path.join(ud, '.' + pn + ext),
                ])
            elif sys.platform.startswith('win32'):
                ud = AppConfig._config_dir()
                ret_val.extend([
                    os.path.join(ud, pn, pn + ext),  # %APPDATA%/repo/repo.ext
                    os.path.join(ud, pn + ext),  # %APPDATA%/repo.ext
                ])
        return ret_val

    @staticmethod
    def add_save_defaults(p):
        p.add_argument(
            '--save-defaults',
            action='store_true',
            help='save option values as defaults to config file',
        )

    @classmethod
    def _config_dir(self):
        if sys.platform.startswith('linux'):
            return os.path.join(os.environ['HOME'], '.config')
        elif sys.platform.startswith('win32'):
            return os.environ['APPDATA']

    @staticmethod
    def no_warning(*args, **kw):
        """sync for warnings"""
        pass

    @staticmethod
    def check():
        """to have an object to check against initing sys.argv parsing"""
        pass

    @staticmethod
    def query_add(s, value):
        """check if value in s(et) and add if not

        return True if added, False if already in.

        >>> x = set()
        >>> if query_add(x, 'a'):
        ...     print 'hello'
        hello
        >>> if query_add(x, 'a'):
        ...     print 'hello'
        >>>

        """
        if value not in s:
            s.add(value)
            return True
        return False

    @staticmethod
    def sp__call__(self, parser, namespace, values, option_string=None):
        from argparse import SUPPRESS
        parser_name = values[0]
        arg_strings = values[1:]

        # set the parser name if requested
        if self.dest is not SUPPRESS:
            setattr(namespace, self.dest, parser_name)

        # select the parser
        try:
            glob_parser = parser
            parser = self._name_parser_map[parser_name]
            glob_parser._sub_parser_sel = (parser_name, parser)
        except KeyError:
            tup = parser_name, ', '.join(self._name_parser_map)
            msg = _('unknown parser %r (choices: %s)') % tup
            raise ArgumentError(self, msg)

        # parse all the remaining options into the namespace
        # store any unrecognized options on the object, so that the top
        # level parser can decide what to do with them
        namespace, arg_strings = parser.parse_known_args(
            arg_strings, namespace)
        if arg_strings:
            vars(namespace).setdefault(_UNRECOGNIZED_ARGS_ATTR, [])
            getattr(namespace, _UNRECOGNIZED_ARGS_ATTR).extend(arg_strings)

    def reread(self):
        """reread the config file, in case it changed on disc"""
        file_name = self.get_file_name()
        try:
            dts = os.path.getmtime(file_name)
        except OSError:
            dts = 0
        if dts > self._config_dts:
            self._config_dts = dts
            self._config = self.get_config(file_name, **self._config_kw)
            #print('rereading config ' + file_name)
            return True
        return False
