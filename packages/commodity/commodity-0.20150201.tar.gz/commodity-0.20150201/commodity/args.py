# -*- coding:utf-8; tab-width:4; mode:python -*-
import os
import argparse
import collections
import sys

import configobj
# import validate

from .pattern import Bunch, MetaBunch


def debug(msg):
#    return
    print msg


class ArgumentConfigParser(argparse.ArgumentParser):
    def __init__(self, *args, **kargs):
        self.config_chunks = []
        super(ArgumentConfigParser, self).__init__(*args, **kargs)

    def load_config_file(self, infile):
        if not os.path.exists(infile):
            debug("{} is not a file".format(infile))
            return

        self.load_config(file(infile).read().splitlines())

    def load_config(self, config_chunk):
        self.config_chunks.append(config_chunk)

    #  def _update_from_config(self, parser, section=None):
    #      debug("_update(): {}".format(section))
    #
    #      if section is None:
    #          return
    #
    #      self._load_from_section(section)
    #
    #      for action in parser._actions:
    #          key = action.dest
    #          value = section.get(key, None)
    #          debug("new_value [{}]: {}".format(key, value))
    #
    #          if value is None:
    #              continue
    #
    #          value = self._cast_value(action, value)
    #          args[key] = value
    #
    #      debug("args: {}".format(args))

    # def _update(self, parser, new_values=None, command=None):
    #     debug('----')
    #     debug("command: {}".format(command))
    #     debug("_update(): {}".format(new_values))
    #
    #     new_values = new_values or {}
    #
    #     for key, sec in new_values.items():
    #         if not key.startswith('cmd:'):
    #             continue
    #
    #         command = key.split(':')[1]
    #         if not isinstance(sec, collections.MutableMapping):
    #             print "{} must be a config section".format(command)
    #             sys.exit(1)
    #
    #         for key, val in sec.items():
    #             cmd_key = "{}_{}".format(command, key)
    #             debug("> {} = {}".format(cmd_key, val))
    # #             debug("> {}".format(args[cmd_key]))
    #             if args.get(cmd_key) is None:
    #                 args[cmd_key] = val
    #
    #     for action in parser._actions:
    #         key = action.dest
    #         value = new_values.pop(key, None)
    #         debug("new_value [{}]: {}".format(key, value))
    #
    #         if value is None:
    #             if key not in args:
    #                 args[key] = None
    #             continue
    #         if isinstance(action, argparse._SubParsersAction):
    #             parser = action.choices[value]
    #             self._update(parser, new_values, command=value)
    #
    #         if key in args:
    #             new_value = value
    #             value = self.promote(args.get(key), new_value)
    #             debug("promoting '{}' '{}' <= current '{}' new '{}'".format(
    #                 key, value, args.get(key), new_value))
    #
    #         value = self._cast_value(action, value)
    #
    #         if value is None and args.get(key) is not None:
    #             continue
    #
    #         args[key] = value
    #
    #     debug("args: {}".format(args))

    def parse_args(self, commandline=None, ns=None):
        self.update_config()
        self._update_casts()

        commandline = commandline or []

        ns = ns or Bunch()
        new_values = argparse.ArgumentParser.parse_args(
            self, args=commandline, namespace=ns)

        debug("pre-cli: {}".format(args))
        self._promote_config(new_values)
        debug("post-cli: {}".format(args))

        return args

    def update_config(self):
        for chunk in self.config_chunks:
            self._do_load_config(chunk)

        self.config_chunks = []

    def _do_load_config(self, config):
        new_config = configobj.ConfigObj(config)

        for name in new_config.sections:
            if name == 'ui':
                self._load_from_section(new_config.get('ui'))
            else:
                setattr(args, name, MetaBunch(new_config[name]))

    def _load_from_section(self, section):
        if section is None:
            return

        for key, value in section.items():
            if not key.startswith('cmd:'):
                args[key] = value
                continue

            command = key[4:]
            for key, val in value.items():
                fullkey = command + '_' + key
                args[fullkey] = val

    def _update_casts(self):
        for action in parser._actions:
            key = action.dest
            value = args.get(key)

            if value is None:
                continue

            value = self._cast_value(action, value)
            args[key] = value

    def _cast_value(self, action, value):
        if not isinstance(value, (str, unicode)) or action.type is None:
            return value

        debug("using '{}' to cast '{}'".format(action.type, value))

        try:
            value = action.type(value) if action.type and value is not None else value
        except ValueError:
            raise ValueError("Type mismatch for '{}' ({}) with value '{}'".format(
                action.dest, action.type.__name__, value))

        return value

    def _promote_config(self, src):
        debug("update from cli: {}".format(src))
        for key, val in src.items():
            if key not in args:
                args[key] = None

            new_value = val
            val2 = self._promote_single(args.get(key), new_value)
            debug("promoting '{}' '{}' <= current '{}' new '{}'".format(
                key, val2, args.get(key), new_value))

            args[key] = val2

    def _promote_single(self, prev, new):
        """
        >>> promote({'default':1}, None)
        1
        >>> promote({'foo':2}, 'foo')
        2
        >>> promote({'foo':3}, 'other')
        'other'
        >>> promote('foo', 'other')
        'other'
        >>> promote('foo', None)
        'foo'
        """

        if isinstance(prev, collections.MutableMapping):
            if new in prev:
                return prev[new]
            if new is None:
                return prev['default']
            return new

        return new or prev


class DebugBunch(Bunch):
    def __setitem__(self, key, value):
        debug("DebugBunch: {} = {}".format(key, value))
        Bunch.__setitem__(self, key, value)

args = DebugBunch()
parser = ArgumentConfigParser()
add_argument = parser.add_argument
