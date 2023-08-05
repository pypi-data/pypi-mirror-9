#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
formatters
==========
``string.Formatter``s for converting standard pythong string templates to regex
and glob patterns. ``RegexFormatter`` formats to a regex pattern with named
groups perfect for use with ``re.search``. ``GlobFormatter`` formats to a glob
pattern that can be used with ``glob.glob``, ``fnmatch.fnmatch`` and
``fnmatch.filter``. ``format_regex`` and ``format_glob`` are instances of
``RegexFormatter`` and ``GlobFormatter`` respectively. Use these instead of
instancing them yourself.
::

    template = 'assets/{asset.name}/{stage}/'

    regex_pattern = format_regex(template)
    glob_pattern = format_glob(template)

    assert regex_pattern == 'assets/(?P<asset_name>.*?)/(?P<stage>.*?)/'
    assert glob_pattern == 'assets/*/*/'
'''
import string


class BaseFormatter(string.Formatter):
    '''BaseFormatter calls ``format`` when called directly. Maintains a cache
    of all previously formatted templates. BaseFormatter uses the mechanics of
    string formatting to find and replace all format fields with string values
    returned from ``get_field``. You can think of this like a string template
    converter.'''

    def __init__(self):
        self.cache = {}

    def __call__(self, template):
        return self.format(template)

    def format(self, template):
        '''Extends format to support caching.'''

        try:
            return self.cache[template]
        except KeyError:
            formatted = super(BaseFormatter, self).vformat(template, [], {})
            self.cache[template] = formatted
            return formatted

    def format_field(self, value, format_spec):
        '''Ignore all format_specs. Necessary to make sure get_field receives
        the original field_name.'''

        return value


class RegexFormatter(BaseFormatter):
    '''Substitues standard Python string template fields with regex named
    groups.

    .. Note:: Any dots used for attribute access are converted to underscores
    '''

    def format(self, template):
        self.groups = set()
        return super(RegexFormatter, self).format(template)

    def get_field(self, field_name, args, kwargs):

        field_name = field_name.split('[')[0]

        if field_name in self.groups:
            return '(?:.*?)', field_name

        self.groups.add(field_name)
        return '(?P<{}>.*?)'.format(field_name.replace('.', '_')), field_name


class GlobFormatter(BaseFormatter):
    '''Substitues standard Python string template fields with *.'''

    def get_field(self, field_name, args, kwargs):
        return '*', field_name


class PartialFormatter(string.Formatter):
    '''Partially format a python string template. Fill in only the fields
    provided leave the rest alone.
    '''

    def __call__(self, *args, **kwargs):
        return self.format(*args, **kwargs)

    def get_field(self, field_name, args, kwargs):
        '''Try standard field lookup, return the field_name if it fails.'''

        try:
            value = super(PartialFormatter, self).get_field(
                field_name, args, kwargs)
        except (KeyError, AttributeError):
            base_field, _ = field_name._formatter_field_name_split()
            value = '{' + field_name + '}', base_field

        return value

    def format_field(self, value, format_spec):
        '''Make sure we include the format_spec in the final output.'''
        try:
            if value.startswith('{'):
                if format_spec:
                    return value[:-1] + ':' + format_spec + value[-1]
                return value
        except AttributeError:
            pass

        return super(PartialFormatter, self).format_field(value, format_spec)

format_regex = RegexFormatter()
format_glob = GlobFormatter()
format_partial = PartialFormatter()
