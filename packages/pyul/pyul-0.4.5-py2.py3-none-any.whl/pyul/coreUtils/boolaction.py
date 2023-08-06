import argparse
import re

__all__ = ['BoolAction']


def boolean(string):
    string = string.lower()
    if string in ['0', 'f', 'false', 'no', 'off']:
        return False
    elif string in ['1', 't', 'true', 'yes', 'on']:
        return True
    else:
        raise ValueError()


class BoolAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None,
                 positive_prefixes=['--', '--with-', '--enable-'],
                 negative_prefixes=['--no-', '--without-', '--disable-']):
        strings = []
        self.positive_strings = set()
        self.negative_strings = set()
        for string in option_strings:
            assert re.match(r'--[A-z]+', string)
            suffix = string[2:]
            for positive_prefix in positive_prefixes:
                self.positive_strings.add(positive_prefix + suffix)
                strings.append(positive_prefix + suffix)
            for negative_prefix in negative_prefixes:
                self.negative_strings.add(negative_prefix + suffix)
                strings.append(negative_prefix + suffix)
        super(BoolAction, self).__init__(
            option_strings=strings,
            dest=dest,
            nargs='?',
            const=None,
            default=default,
            type=boolean,
            choices=None,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, value, option_string=None):
        if value is None:
            value = option_string in self.positive_strings
        elif option_string in self.negative_strings:
            value = not value
        setattr(namespace, self.dest, value)
