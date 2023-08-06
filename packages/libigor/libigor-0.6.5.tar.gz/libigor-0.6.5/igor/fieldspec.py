# -*- coding: utf-8 -*-
import sys
import re
from six import string_types


if sys.version_info >= (3, 0):
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

kFieldPtrn = re.compile(r'{name}(\({members}\))?'.format(
    name    = r'(?P<n>-?[\w\d_*]+)',
    members = r'(?P<m>[\w\d_\-,*)(]+)'
))


#==============================================================================
class Fieldspec(object):
    """
    ``Fieldspec`` represents field specification for REST queries. It describes
    the format in which the query result will be returned. What model fields
    should be present and which of them should be expanded. Expansion works
    for foreign keys, where instead of object key, we can insert the object
    itself (with all, or selected members).

    For usage examples see ``restapi.serialize.serialize()``.

    **Simple tests**

    >>> fs = Fieldspec('field1,field2(sub1,sub2),field3(*)')
    >>> fs
    <Fieldspec: field1,field2,field3>

    Easily check if the field is matched by the spec:
    >>> 'field1' in fs
    True
    >>> fs['field1']
    True
    >>> 'field7' in fs
    False

    Supports nested specifications:
    >>> fs['field2']
    <Fieldspec: sub1,sub2>
    >>> 'sub1' in fs['field2']
    True
    >>> fs['field2']['sub2']
    True

    And wildcards
    >>> 'asdf' in fs['field2']
    False
    >>> 'asdf' in fs['field3']
    True
    >>> fs['field3']['asdf']
    True

    Exclude
    >>> fs = Fieldspec('*,-field1')
    >>> 'asdf' in fs
    True
    >>> 'field1' in fs
    False

    """
    #-------------------------None-------------------------------------------//
    def __init__(self, spec = '*'):
        self.fields     = []
        self.exclude    = []
        self.spec       = spec
        self.all        = False

        if isinstance(spec, Fieldspec):
            # Clone
            self.fields = list(spec.fields)
            self.all    = spec.all
            self.spec   = spec.spec

        elif isinstance(spec, string_types):
            self._parse(spec)

        elif spec not in (None, True):
            raise ValueError('Invalid field specification')

    #------------------------------------------------------------------------//
    def empty(self):
        return len(self.fields) == 0 and not self.all

    #------------------------------------------------------------------------//
    def __contains__(self, name):
        for fname, members in self.exclude:
            if fname == name:
                return False

        if self.all:
            return True

        for fname, members in self.fields:
            if fname == name:
                return members
        return None

    #------------------------------------------------------------------------//
    def __getitem__(self, name):
        for fname, members in self.exclude:
            if fname == name:
                return None

        if self.spec == '**':
            return Fieldspec(self)

        for fname, members in self.fields:
            if fname == name:
                return members
        return None
        #if self.spec == '**':
        #    return Fieldspec(self)

        #for fname, members in self.fields:
        #    if fname == name:
        #        return members

        #if self.all:
        #    return True
        #return None

    #------------------------------------------------------------------------//
    def __repr__(self):
        return "<Fieldspec: {}>".format(
            ','.join(f[0] for f in self.fields),
            #','.join('-' + n for n, m in self.exclude)
        )

    #------------------------------------------------------------------------//
    def _parse(self, string):
        fields  = self._splitfields(string)
        for field in fields:
            m       = kFieldPtrn.match(field)

            if not m:
                raise ValueError("Invalid field specification")

            name    = m.group('n')
            if name[0] == '-':
                name    = name[1:]
                group   = self.exclude
            else:
                group   = self.fields

            membstr = m.group('m')
            members = True if membstr is None else Fieldspec(membstr)
            group.append((name, members))
            if name in ('*', '**'):
                self.all = True

        #if not string:
        #    return {'*': '*'}

        ## <name>(<members>)
        #pttrn   = re.compile(r'(?P<n>[\w\d_*]+)(\((?P<m>[\w\d_,*)(]+)\))?')
        #fields  = self._splitfields(string)
        #expand  = {}
        #for field in fields:
        #    m = pttrn.match(field)
        #    name    = m.group('n')
        #    members = m.group('m')
        #    members = self._parse(members) if members else {'*': '*'}
        #    expand[name] = members

        #return expand or {'*': '*'}

    #------------------------------------------------------------------------//
    def _splitfields(self, string):
        """
        Split field list into separate fields. Takes into account nesting
        specification (inside parenthesis) by ignoring commas inside it.

        >>> fs = Fieldspec()
        >>> fs._splitfields('one,two,three')
        ['one', 'two', 'three']

        >>> fs._splitfields('one(mem1,mem2),two,three')
        ['one(mem1,mem2)', 'two', 'three']

        """
        fields      = []
        start       = 0
        numparen    = 0
        for i in range(len(string)):
            ch = string[i]
            if ch == ',':
                if i != start and numparen == 0:
                    fields.append(string[start:i])
                    start = i + 1
            elif ch == '(':
                numparen += 1
            elif ch == ')':
                numparen -= 1
        fields.append(string[start:])
        return fields

    #------------------------------------------------------------------------//
    @classmethod
    def from_query(self, qs):
        qs  = dict(parse_qsl(qs)) if isinstance(qs, string_types) else qs
        return Fieldspec(qs.get('_fields', '*'))
