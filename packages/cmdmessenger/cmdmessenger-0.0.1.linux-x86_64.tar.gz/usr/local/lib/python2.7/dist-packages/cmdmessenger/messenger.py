#!/usr/bin/env python
"""
use stream.inWaiting to check if bytes are available

    A command is a python -> arduino
    A callback is arduino -> python

    Commands are defined by dictionaries with:
        name: [string] namespace name, only used for commands
        id: [int] message id, only used for commands
        params: [list of types, see params.py] if not present, no params
        function: [callable] only used for callbacks

"""

from . import params


class InvalidCommand(Exception):
    pass


def validate_command(cmd):
    if isinstance(cmd, (list, tuple)):
        return [validate_command(c) for c in cmd]
    if 'params' in cmd:
        for p in cmd['params']:
            if p not in params.types:
                raise InvalidCommand("Command %s unknown param %s" % (cmd, p))
    return True


def split_line(l, fs=',', ls=';', esc='\\'):
    sline = l.strip()
    start = 0
    if sline[-1] == ls:
        end = len(l) - 1
    else:
        end = len(l)
    if end <= start:
        raise Exception("Invalid line %s" % l)
    tokens = []
    while start < end:
        sub_line = sline[start:end]
        if fs not in sub_line:
            tokens.append(sub_line)
            break
        i = sub_line.index(fs)
        if i == 0:
            raise Exception("Invalid line %s" % l)
        while sub_line[i - 1] == esc:  # this fs is escaped
            if len(sub_line) > 1 and sub_line[i - 2] == esc:
                # this is an escaped escape ("0\\,1") so the fs is valid
                break
            sub_sub_line = sub_line[i+1:end]
            if fs not in sub_sub_line:  # this escaped fs was in the last token
                i = end
                break
            i += sub_sub_line.index(fs) + 1
        tokens.append(sub_line[:i])
        start += i + 1
        if len(tokens) > 5:
            raise Exception
    return tokens


def escape(s, fs=',', ls=';', esc='\\'):
    if isinstance(s, (tuple, list)):
        return [escape(i, esc) for i in s]
    s = s.replace(esc, esc + esc)
    s = s.replace(fs, esc + fs)
    s = s.replace(ls, esc + ls)
    return s


def unescape(s, esc='\\'):
    if isinstance(s, (tuple, list)):
        return [unescape(i, esc) for i in s]
    return s.replace(esc, '')


class Messenger(object):
    def __init__(self, stream, cmds, fs=',', ls=';', esc='\\'):
        """cmds should be a list"""
        self.stream = stream
        self.fs = fs
        self.ls = ls
        self.esc = esc
        # TODO validate commands
        validate_command(cmds)
        self.cmds = {}
        for (i, c) in enumerate(cmds):
            if not isinstance(c, dict):
                c = {'name': c}
            c['id'] = i
            self.cmds[i] = c
            if 'name' in c:
                self.cmds[c['name']] = c
        self.callbacks = {}

    # stream parsing
    def process_line(self, l):
        tokens = unescape(split_line(l, self.fs, self.ls, self.esc), self.esc)
        cmd_id = int(tokens[0])
        types = self.cmds[cmd_id].get('params', [])
        args = [t['from'](a) for (t, a) in zip(types, unescape(tokens[1:]))]
        if cmd_id not in self.callbacks:
            self.unknown(*args)
        else:
            self.callbacks[cmd_id](*args)

    def read_line(self):
        l = self.stream.read(1)  # TODO optimize this
        esc = l[-1] == self.esc
        while l[-1] != self.ls or esc:
            l += self.stream.read(1)
            if esc:
                esc = False
            else:
                esc = l[-1] == self.esc
        return l

    def send(self, cmd_id, *args):
        msg = self.fs.join((str(cmd_id), ) + tuple(escape(args))) + self.ls
        self.stream.write(msg)
        # TODO LFCF?

    # callbacks
    def attach(self, func, index):
        self.callbacks[index] = func

    def unknown(self, *args):
        pass  # called when an unknown command is received

    # commands
    def call(self, index, *args):
        # can be cmd_id or name
        cmd = self.cmds[index]
        types = cmd.get('params', [])
        self.send(cmd['id'], *[t['to'](a) for (t, a) in zip(types, args)])
