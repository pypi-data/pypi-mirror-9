# -*- coding:utf-8; tab-width:4; mode:python -*-
import os
import argparse
import collections
import sys

import configobj
# import validate

from .pattern import Bunch, MetaBunch


def debug(msg):
    return
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

    def _do_load_config(self, config):
        new_config = configobj.ConfigObj(config)

        for sec in new_config.sections:
            if sec == 'ui':
                continue

            setattr(args, sec, MetaBunch(new_config[sec]))

        self._update(self, new_config.get('ui'))

    def _update(self, parser, new_values=None, command=None):
        debug('----')
        debug("command: {}".format(command))
        debug("_update(): {}".format(new_values))

        new_values = new_values or {}

        for key, sec in new_values.items():
            if not key.startswith('cmd:'):
                continue

            command = key.split(':')[1]
            if not isinstance(sec, collections.MutableMapping):
                print "{} must be a config section".format(command)
                sys.exit(1)

            for key, val in sec.items():
                cmd_key = "{}_{}".format(command, key)
                debug("> {} = {}".format(cmd_key, val))
#                debug("> {}".format(args[cmd_key]))
                if args.get(cmd_key) is None:
                    args[cmd_key] = val

        for action in parser._actions:
            key = action.dest
            value = new_values.pop(key, None)
            debug("new_value [{}]: {}".format(key, value))

            if value is None:
                if key not in args:
                    args[key] = None
                continue

            if isinstance(action, argparse._SubParsersAction):
                parser = action.choices[value]
                self._update(parser, new_values, command=value)

            if key in args:
                new_value = value
                value = self.promote(args.get(key), new_value)
                debug("promoting '{}' '{}' <= current '{}' new '{}'".format(
                    key, value, args.get(key), new_value))

            value = self._cast_value(action, value)

            if value is None and args.get(key) is not None:
                continue

            args[key] = value

        debug("args: {}".format(args))

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

    def promote(self, prev, new):
        # print "promote:", prev, new

        if isinstance(new, collections.MutableMapping):
            if prev in new:
                return new[prev]
            if prev is None:
                return new['default']
            return prev

        if prev is None:
            return new

        return prev

    def parse_args(self, commandline=None, ns=None):
        commandline = commandline or []
        self.parse_args_chunk(commandline, ns)

        for chunk in self.config_chunks:
            self._do_load_config(chunk)

        return args

    def parse_args_chunk(self, commandline=None, ns=None):
        ns = ns or Bunch()
        new_values = argparse.ArgumentParser.parse_args(self, args=commandline, namespace=ns)
        self._update(self, new_values)
        args.update(new_values)

    def update_config(self):
        for chunk in self.config_chunks:
            self._do_load_config(chunk)

        self.config_chunks = []


args = Bunch()
parser = ArgumentConfigParser()
add_argument = parser.add_argument
