import itertools
from confetti import Metadata

_dest_generator = ("dest_{0}".format(i) for i in itertools.count())

# for use with callbacks
def _set_true(_):
    return True

def _set_false(_):
    return False

def _increase(value):
    return value + 1

def _decrease(value):
    return value - 1

class _Cmdline(object):
    def __init__(self, arg=None, on=None, off=None, increase=None, decrease=None, metavar="PARAM", required=False, append=None):
        super(_Cmdline, self).__init__()
        dest = next(_dest_generator)
        self.callback_dest = dest + ":callbacks"
        self.arg_dest = dest + ":arg"
        self.arg = arg
        self.on = on
        self.off = off
        self.required = required
        self.increase = increase
        self.decrease = decrease
        self.metavar = metavar
        self.append = append

    def configure_parser(self, parser, path, node):
        """
        Add all required flags to a parser to support updating the config value from commandline
        """
        description = node.metadata.get('doc', path)
        if self.arg is not None:
            parser.add_argument(self.arg,
                                dest=self.arg_dest,
                                metavar=self.metavar,
                                default=None,
                                required=self.required,
                                help=description)
        if self.append is not None:
            parser.add_argument(self.append,
                                dest=self.arg_dest,
                                action="append",
                                metavar=self.metavar,
                                default=None,
                                help=description)

        self._add_arg(parser, self.on, callback=_set_true,
                      description="Turn on " + description)
        self._add_arg(parser, self.off, callback=_set_false,
                      description="Turn off " + description)
        self._add_arg(parser, self.increase, callback=_increase,
                      description="Increase " + description)
        self._add_arg(parser, self.decrease, callback=_decrease,
                      description="Decrease " + description)

    def _add_arg(self, parser, flag, callback, description):
        if flag is None:
            return
        parser.add_argument(flag, dest=self.callback_dest, action="append_const", const=callback, help=description)

    def update_value(self, value, args):
        """
        given a previous configuration value and the parsed args, return the new value
        """
        arg_value = getattr(args, self.arg_dest, None)
        if arg_value is not None:
            if self.append:
                value = list(value) + (arg_value or [])
            else:
                value = arg_value
        callbacks = getattr(args, self.callback_dest, None)
        if callbacks:
            for callback in callbacks:
                value = callback(value)
        return value

def Cmdline(**kwargs):
    return Metadata(cmdline=_Cmdline(**kwargs))

def Doc(msg):
    return Metadata(doc=msg)
