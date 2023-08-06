#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2014 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
The `kenozooid.uddf` module provides support for parsing, searching and
manipulation of data stored in UDDF files.

The functions implemented in this module can be divided into the following
categories

- XML nodes functions
- generic XML data searching and manipulation functions
- functions for searching and manipulation of diving specific data

Searching functions use XPath expressions (queries) to find data. Each tag
name in an query should be prefixed with 'uddf:' string to indicate UDDF
namespace, i.e. 'uddf:diver', 'uddf:waypoint' - appropriate namespace
mapping for this prefix is defined for each XPath call.

The result of parsing or search of data is usually iterator of XML nodes or
data records (named tuples in Python terms).

Module `lxml` is used for XML parsing and querying with XPath. Full
capabilities of underlying `libxml2` library is used by design. The
ElementTree XML data model is used for XML nodes.
"""

from collections import namedtuple, OrderedDict, Counter
from lxml import etree as et
from functools import partial
from datetime import datetime
from dateutil.parser import parse as dparse
from io import FileIO
from operator import itemgetter
from uuid import uuid4 as uuid
from copy import deepcopy
from dirty.xml import xml
from dirty import RawString
import base64
import bz2
import itertools
import hashlib
import logging
import os
import os.path
import pkg_resources

import kenozooid
import kenozooid.util as kt

log = logging.getLogger('kenozooid.uddf')

#
# Default UDDF namespace mapping.
#
_NSMAP = {'uddf': 'http://www.streit.cc/uddf/3.2/'}

# Node id formatter
FORMAT_ID = 'id-{}'

FMT_F = partial(str.format, '{0:.1f}')
FMT_F2 = partial(str.format, '{0:.2f}')
FMT_I = lambda v: '{}'.format(int(round(v)))
FMT_DT = lambda dt: format(dt, '%Y-%m-%dT%H:%M:%S%z')

#
# Parsing and searching.
#

XPath = partial(et.XPath, namespaces=_NSMAP)
XPath.__doc__ = """
    XPath query constructor for UDDF data.

    Use `uddf` prefix to create a query, i.e.::

        XPath('uddf:informationbeforedive/uddf:datetime/text()')

    .. seealso: lxml.etree.XPath
"""

# XPath queries for default dive data
XP_DEFAULT_DIVE_DATA = (
    XPath('uddf:informationbeforedive/uddf:divenumber/text()'),
    XPath('uddf:informationbeforedive/uddf:datetime/text()'),
    XPath('uddf:informationafterdive/uddf:greatestdepth/text()'),
    XPath('uddf:informationafterdive/uddf:diveduration/text()'),
    XPath('uddf:informationafterdive/uddf:lowesttemperature/text()'),
    XPath('uddf:informationafterdive/uddf:averagedepth/text()'),
    XPath('uddf:samples/uddf:waypoint/uddf:divemode[1]/@type'),
    None,
)

# XPath queries for default dive profile sample data
XP_DEFAULT_PROFILE_DATA =  (
    XPath('uddf:depth/text()'),
    XPath('uddf:divetime/text()'),
    XPath('uddf:temperature/text()'),
    XPath('uddf:setpo2/text()'),
    XPath('uddf:setpo2/@setby'),
    XPath('uddf:decostop/@duration'),
    XPath('uddf:decostop/@decodepth'),
    XPath('uddf:alarm/text()'),
    XPath('uddf:switchmix/@ref'),
)

XP_DEFAULT_GAS_DATA =  (
    XPath('@id'),
    XPath('uddf:name/text()'),
    XPath('uddf:o2/text()'),
    XPath('uddf:he/text()'),
)

# XPath query to locate dive profile sample
XP_WAYPOINT = XPath('./uddf:samples/uddf:waypoint')
# XPath query to locate gas mix
XP_MIX = XPath('/uddf:uddf/uddf:gasdefinitions/uddf:mix')

# XPath queries for default dive computer dump data
XP_DEFAULT_DUMP_DATA = (
    XPath('uddf:link/@ref'),
    # //uddf:divecomputerdump[position()] gives current()
    XPath('../../uddf:diver/uddf:owner//uddf:divecomputer[' \
            '@id = //uddf:divecomputerdump[position()]/uddf:link/@ref' \
        ']/uddf:model/text()'),
    XPath('uddf:datetime/text()'),
    XPath('uddf:dcdump/text()'),
)

# XPath queries for default buddy data
XP_DEFAULT_BUDDY_DATA = (
    XPath('@id'),
    XPath('uddf:personal/uddf:firstname/text()'),
    XPath('uddf:personal/uddf:middlename/text()'),
    XPath('uddf:personal/uddf:lastname/text()'),
    XPath('uddf:personal/uddf:membership/@organisation'),
    XPath('uddf:personal/uddf:membership/@memberid'),
)

# XPath queries for default dive site data
XP_DEFAULT_SITE_DATA = (
    XPath('@id'),
    XPath('uddf:name/text()'),
    XPath('uddf:geography/uddf:location/text()'),
    XPath('uddf:geography/uddf:longitude/text()'),
    XPath('uddf:geography/uddf:latitude/text()'),
)

# XPath query to find a buddy
XP_FIND_BUDDY = XPath('/uddf:uddf/uddf:diver/uddf:buddy[' \
    '@id = $buddy' \
    ' or uddf:personal/uddf:membership/@memberid = $buddy' \
    ' or uddf:personal/uddf:membership/@organisation = $buddy' \
    ' or contains(uddf:personal/uddf:firstname/text(), $buddy)' \
    ' or contains(uddf:personal/uddf:lastname/text(), $buddy)' \
    ']')

# XPath query to find a dive site
XP_FIND_SITE = XPath('/uddf:uddf/uddf:divesite/uddf:site[' \
    '@id = $site' \
    ' or contains(uddf:name/text(), $site)' \
    ' or contains(uddf:geography/uddf:location/text(), $site)' \
    ']')

# XPath query to find dives
XP_FIND_DIVES = XPath('/uddf:uddf/uddf:profiledata' \
    '/uddf:repetitiongroup/uddf:dive[in-range(position(), $nodes)' \
    ' and in-range(uddf:informationbeforedive/uddf:divenumber/text(), $dives)]')

# XPath query to find dive gases
XP_FIND_DIVE_GASES = XPath('/uddf:uddf/uddf:gasdefinitions' \
    '/uddf:mix[@id=/uddf:uddf/uddf:profiledata/uddf:repetitiongroup' \
    '/uddf:dive[in-range(position(), $nodes)]' \
    '/uddf:samples/uddf:waypoint/uddf:switchmix/@ref]')


class RangeError(ValueError):
    """
    Error raised when a range cannot be parsed.

    .. seealso::
        parse_range
    """
    pass


def parse(f, ver_check=True):
    """
    Parse XML file and return document object.

    File to parse can be anything supported by ``lxml`` library.

    If file to parse is file name and ends with '.bz2', then it is treated
    as file compressed with bzip2.

    :Parameters:
     f
        File to parse.
     ver_check
        Check version of UDDF file.
    """
    if isinstance(f, str) and (f.endswith('.bz2') or f.endswith('.bz2.bak')):
        log.debug('detected compressed file')
        f = bz2.BZ2File(f)
    doc = et.parse(f)
    if ver_check:
        v1, v2, *_ = doc.getroot().get('version').split('.')
        if (v1, v2) != ('3', '2'):
            raise ValueError('UDDF file version {}.{} is not supported.' \
                    ' Please upgrade file with "kz upgrade" command.' \
                    .format(v1, v2))
    return doc


def find(f, query, **params):
    """
    Find XML nodes in UDDF file using XPath query.

    UDDF file can be a file name, file object, URL and basically everything
    what is supported by `lxml` library.

    File to parse can be a file name ending with '.bz2'. It is treated as
    file compressed with bzip2.

    :Parameters:
     f
        UDDF file to parse.
     query
        XPath expression or XPath object.
     params
        XPath query parameters.

    .. seealso:: :py:func:`XPath`, :py:func:`parse`
    """
    log.debug('parsing and searching with query: {}; parameters {}' \
            .format(query, params))
    doc = parse(f)
    if isinstance(query, str):
        return xp(doc, query)
    else:
        return (n for n in query(doc, **params))


def xp(node, query):
    """
    Find items with XPath query.

    The query is performed using UDDF namespace.

    Iterator of items (strings, nodes) found by query is returned.
    
    :Parameters:
     node
        Document node or query starting node.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    for n in node.xpath(query, namespaces=_NSMAP):
        yield n 


def xp_first(node, query):
    """
    Get first element found with XPath query.

    The query is performed using UDDF namespace.

    First element is returned or None if it is not found.
    
    :Parameters:
     node
        Document node or query starting node.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    data = xp(node, query)
    return next(data, None)


def xp_last(node, query):
    """
    Get last element found with XPath query.

    The query is performed using UDDF namespace.

    Last element is returned or None if it is not found.
    
    :Parameters:
     node
        Document node or query starting node.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    nodes = node.xpath(query, namespaces=_NSMAP)
    return nodes[-1] if nodes else None


def find_data(name, node, fields, queries, parsers, nquery=None):
    """
    Find data records starting from specified XML node.

    A record type (namedtuple) is created with specified fields. The data
    of a record is retrieved with XPath expression objects, which is
    converted from string to appropriate type using parsers.

    A parser can be any type or function, i.e. `float`, `int` or
    `dateutil.parser.parse`.

    If XML node is too high to execture XPath expression objects, then the
    basis for field queries can be relocated with `nquery` parameter. If
    `nquery` parameter is not specified, then only one record is returned.
    Otherwise it is generator of records.

    The length of fields, field queries and field parsers should be the same.

    :Parameters:
     name
        Name of the record to be created.
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.
     nquery
        XPath expression object to relocate from node to more appropriate
        position in XML document for record data retrieval.

    .. seealso:: :py:func:`dive_data`, :py:func:`dive_profile`
    """
    T = namedtuple(name, ' '.join(fields))._make
    if nquery:
        data = nquery(node)
        return (_record(T, n, queries, parsers) for n in data)
    else:
        return _record(T, node, queries, parsers)


def dive_data(node, fields=None, queries=None, parsers=None):
    """
    Specialized function to return record of a dive data.

    At the moment record of dive data contains dive start time only, by
    default. It should be enhanced in the future to return more rich data
    record.

    Dive record data can be reconfigured with optional fields, field
    queries and field parsers parameters.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression object for each field to retrieve its value.
     parsers
        Parsers field values to be created in a record.

    .. seealso:: :py:func:`find_data`
    """
    if fields is None:
        fields = ('number', 'datetime', 'depth', 'duration', 'temp',
            'avg_depth', 'mode', 'profile')
        queries = XP_DEFAULT_DIVE_DATA
        parsers = (int, dparse, float, float, float, float, str, dive_profile)

    return find_data('Dive', node, fields, queries, parsers)


def dive_profile(node, fields=None, queries=None, parsers=None):
    """
    Specialized function to return generator of dive profiles records.

    By default, dive profile record contains following fields

    time
        dive time in seconds
    depth
        dive depth in meters
    temp
        temperature in Kelvins

    Dive profile record data can be reconfigured with optional fields,
    field queries and field parsers parameters.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.

    .. seealso:: :py:func:`find_data`
    """
    if fields is None:
        fields = ('depth', 'time', 'temp', 'setpoint', 'setpointby',
                'deco_time', 'deco_depth', 'alarm', 'gas')
        queries = XP_DEFAULT_PROFILE_DATA
        gases = dict(((gas.id, gas) for gas in gas_data(node)))
        parsers = (float, ) * 4 + (str, float, float, str, gases.get)

    return find_data('Sample', node, fields, queries, parsers,
            nquery=XP_WAYPOINT)


def gas_data(node, fields=None, queries=None, parsers=None):
    if fields is None:
        fields = ('id', 'name', 'o2', 'he')
        queries = XP_DEFAULT_GAS_DATA
        parsers = (str, str, int, int)

    return find_data('Gas', node, fields, queries, parsers,
            nquery=XP_MIX)


def dump_data(node, fields=None, queries=None, parsers=None):
    """
    Get dive computer dump data.

    The following data is returned

    dc_id
        Dive computer id.
    dc_model
        Dive computer model information.
    datetime
        Date and time when dive computer dump was obtained.
    data
        Dive computer dump data.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.

    .. seealso:: :py:func:`find_data`
    """
    if fields is None:
        fields = ('dc_id', 'dc_model', 'datetime', 'data')
        queries = XP_DEFAULT_DUMP_DATA
        parsers = (str, str, dparse, _dump_decode)
    return find_data('DiveComputerDump', node, fields, queries, parsers)


def buddy_data(node, fields=None, queries=None, parsers=None):
    """
    Get dive buddy data.

    The following data is returned by default

    id
        Buddy id.
    fname
        Buddy first name.
    mname
        Buddy middle name.
    lname
        Buddy last name.
    org
        Organization, which a buddy is member of.
    number
        Member number id in the organisation.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.

    .. seealso:: :py:func:`find_data`
    """
    if fields is None:
        fields = ('id', 'fname', 'mname', 'lname', 'org', 'number')
        queries = XP_DEFAULT_BUDDY_DATA
        parsers = (str, ) * 7
    return find_data('Buddy', node, fields, queries, parsers)


def site_data(node, fields=None, queries=None, parsers=None):
    """
    Get dive site data.

    The following data is returned by default

    id
        Dive site id.
    name
        Dive site name.
    location
        Dive site location.
    x
        Dive site longitude.
    y
        Dive site latitude.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.

    .. seealso:: :py:func:`find_data`
    """
    if fields is None:
        fields = ('id', 'name', 'location', 'x', 'y')
        queries = XP_DEFAULT_SITE_DATA
        parsers = (str, str, str, float, float)
    return find_data('DiveSite', node, fields, queries, parsers)


def parse_range(s):
    """
    Parse textual representation of number range into Python expression.

    Examples of a ranges

    >>> parse_range('1-3,5')
    '1 <= n and n <= 3 or n == 5'

    >>> parse_range('-3,10')
    'n <= 3 or n == 10'

    Example of infinite range

    >>> parse_range('20-')
    '20 <= n'

    :Parameters:
     s
        Textual representation of number range.
    """
    data = []
    try:
        for r in s.split(','):
            d = r.split('-')
            if len(d) == 1:
                data.append('n == %d' % int(d[0]))
            elif len(d) == 2:
                p1 = d[0].strip()
                p2 = d[1].strip()
                if p1 and p2:
                    data.append('{} <= n and n <= {}'.format(int(p1), int(p2)))
                elif p1 and not p2:
                    data.append('{} <= n'.format(int(p1)))
                elif not p1 and p2:
                    data.append('n <= {}'.format(int(p2)))
            else:
                raise RangeError('Invalid range %s' % s)
    except ValueError as ex:
        raise RangeError('Invalid range %s' % s)
    return ' or '.join(data)


def in_range(ctx, pos, nodes):
    """
    XPath expression function to restrict position of a node to be within
    numeric range.

    :Parameters:
     ctx
        XPath context object.
     pos
        Node position.
     nodes
        Number range, i.e. "2-3".

    .. seealso:: :py:func:`parse_range`
    """
    if not nodes:
        return True

    if isinstance(pos, list):
        if len(pos) == 0:
            return False
        if len(pos) != 1:
            raise ValueError('Too many parameters')
        pos = int(pos[0])

    kf = 'in-range({})'.format(nodes)
    if kf not in ctx.eval_context:
        nr = parse_range(nodes)
        fstr = 'ctx.eval_context["{}"] = lambda n: {}'.format(kf, nr)
        exec(fstr)
    return ctx.eval_context[kf](pos)

# register in-range XPath function
ns = et.FunctionNamespace(None)
ns['in-range'] = in_range


def _field(node, query, parser):
    """
    Find text value of a node starting from specified XML node.

    The text value is converted with function `t` and then returned.

    If node is not found, then `None` is returned.

    :Parameters:
     node
        XML node.
     query
        XPath expression object to find node with text value.
     parser
        Parser to convert text value to requested type.
    """
    data = [node] if query is None else query(node)
    if data:
        return parser(data[0])


def _record(rt, node, queries, parsers):
    """
    Create record with data.

    The record data is found with queries (XPath expressions objects)
    starting from XML node.
    
    The data is converted to their appropriate type using parsers.

    If query is `None`, then record data is node itself.

    :Parameters:
     rt
        Record type (named tuple) of record data.
     node
        XML node.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.
    """
    return rt(_field(node, f, p) for f, p in zip(queries, parsers))


def _dump_decode(data):
    """
    Decode dive computer data, which is stored in UDDF dive computer dump
    file.
    """
    s = base64.b64decode(data.encode())
    return bz2.decompress(s)


#
# Creating UDDF data.
#

DEFAULT_FMT_DIVE_PROFILE = {
    'depth': lambda d: str.format('{0:.1f}', max(d, 0)),
    'temp': partial(str.format, '{0:.1f}'),
}

# basic data for an UDDF file
# fixme: obsolete
UDDF_BASIC = """\
<uddf xmlns="http://www.streit.cc/uddf/3.2/" version="3.2.0">
<generator>
    <name>kenozooid</name>
    <manufacturer id='kenozooid'>
      <name>Kenozooid Team</name>
      <contact>
        <homepage>http://wrobell.it-zone.org/kenozooid/</homepage>
      </contact>
    </manufacturer>
    <version>{kzver}</version>
    <datetime></datetime>
</generator>
<diver>
    <owner id='owner'>
        <personal>
            <firstname>Anonymous</firstname>
            <lastname>Guest</lastname>
        </personal>
    </owner>
</diver>
</uddf>
""".format(kzver=kenozooid.__version__)


def create(datetime=datetime.now()):
    """
    fixme: obsolete

    Create basic UDDF structure.

    :Parameters:
     datetime
        Timestamp of file creation, current time by default.
    """
    root = et.XML(UDDF_BASIC)

    now = datetime.now()
    n = root.xpath('//uddf:generator/uddf:datetime', namespaces=_NSMAP)[0]
    n.text = FMT_DT(datetime)
    return root


def set_data(node, queries, formatters=None, **data):
    """
    Set data of nodes or attributes using XPath queries relative to
    specified XML node.

    The data values are converted to string with formatters functions.

    :Parameters:
     node
        XML node.
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Data formatters.
     data
        Data values to be set within XML document.
    """
    if formatters is None:
        formatters = {}

    nodes = {} # created nodes
    attrs = set() # created attributes

    for key, path in queries.items():
        value = data.get(key)
        if value is None:
            continue

        if isinstance(path, str):
            path = [path]
            value = [value]

        for p, v in zip(path, value):
            f = formatters.get(key, str)
            v = f(v)

            attr = None
            tags = p.rsplit('/', 1)
            if tags[-1].startswith('@'):
                attr = tags[-1][1:]  # skip '@'
                p = tags[0] if len(tags) > 1 else None

            n = node
            if p:
                n = nodes.get(p)
                # reuse node created in this call to make t/@a t/@b work,
                # but create new node to not overwrite attribute value
                if n is None or (p, attr) in attrs:
                    *_, n = create_node(p, parent=node)
                    nodes[p] = n
                    attrs.add((p, attr))

            assert n is not None

            if attr:
                n.set(attr, v)
            else:
                n.text = v


def create_node(path, parent=None, append=True):
    """
    TODO: get rid of parent, does not make sense

    Create a hierarchy of nodes using XML nodes path specification.

    Path is a string of node names separated by slash character, i.e. a/b/c
    creates::

        <a><b><c/></b><a>

    If parent node is specified and some part of node hierarchy already
    exists then only non-existant nodes are created, i.e. if parent is
    'x' node in

        <x><y/></x>

    then path 'x/z' modifies XML document as follows

        <x><y/><z/></x>

    :Parameters:
     path
        Hierarchy of nodes.
     parent
         Optional parent node.
    """
    # preserve namespace prefix option... please?!? :/
    T = lambda tag: tag.replace('uddf:', '{' + _NSMAP['uddf'] + '}')
    tags = path.split('/')
    n = parent
    for t in tags:
        is_last = tags[-1] == t
        k_exists = False

        k = None
        if n is not None:
            k = xp_first(n, t)
        if is_last or k is None:
            k = et.Element(T(t))
        elif k is not None:
            k_exists = True
        if n is not None and not k_exists:
            if append:
                n.append(k)
            else:
                n.insert(0, k)
        n = k
        yield n


def create_dive_data(node=None, queries=None, formatters=None, **data):
    """
    Create dive data.

    :Parameters:
     node
        Base node (UDDF root node).
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Dive data formatters.
     data
        Dive data.
    """
    if queries == None:
        bd = data.get('buddies')
        bno = len(bd) if bd else 0
        f = ('site', 'buddies', 'datetime', 'depth', 'duration', 'temp')
        q = ('uddf:informationbeforedive/uddf:link/@ref',
            ['uddf:informationbeforedive/uddf:link/@ref'] * bno,
            'uddf:informationbeforedive/uddf:datetime',
            'uddf:informationafterdive/uddf:greatestdepth',
            'uddf:informationafterdive/uddf:diveduration',
            'uddf:informationafterdive/uddf:lowesttemperature')
        queries = OrderedDict(zip(f, q))
    if formatters == None:
        formatters = {
            'datetime': FMT_DT,
            'depth': partial(str.format, '{0:.1f}'),
            'duration': partial(str.format, '{0:.0f}'),
            'temp': partial(str.format, '{0:.1f}'),
        }
    _, rg, dn = create_node('uddf:profiledata/uddf:repetitiongroup/uddf:dive',
            parent=node)
    _set_id(rg)
    _set_id(dn)
    set_data(dn, queries, formatters, **data)
    return dn


def create_buddy_data(node, queries=None, formatters=None, **data):
    """
    Create buddy data.

    :Parameters:
     node
        Base node (UDDF root node).
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Buddy data formatters.
     data
        Buddy data.
     
    """
    if queries == None:
        f = ('id', 'fname', 'mname', 'lname', 'org', 'number')
        q = ('@id',
            'uddf:personal/uddf:firstname',
            'uddf:personal/uddf:middlename',
            'uddf:personal/uddf:lastname',
            'uddf:personal/uddf:membership/@organisation',
            'uddf:personal/uddf:membership/@memberid')
        queries = OrderedDict(zip(f, q))

    if formatters == None:
        formatters = {}

    if 'id' not in data or data['id'] is None:
        data['id'] = uuid().hex
        
    _, buddy = create_node('uddf:diver/uddf:buddy', parent=node)
    set_data(buddy, queries, formatters, **data)
    return buddy


def create_site_data(node, queries=None, formatters=None, **data):
    """
    Create dive site data.

    :Parameters:
     node
        Base node (UDDF root node).
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Dive site data formatters.
     data
        Dive site data.
     
    """
    if queries == None:
        f = ('id', 'name', 'location', 'x', 'y')
        q = ('@id',
            'uddf:name',
            'uddf:geography/uddf:location',
            'uddf:geography/uddf:longitude',
            'uddf:geography/uddf:latitude')
        queries = OrderedDict(zip(f, q))

    if formatters == None:
        formatters = {}

    if 'id' not in data or data['id'] is None:
        data['id'] = uuid().hex
        
    _, site = create_node('uddf:divesite/uddf:site', parent=node)
    set_data(site, queries, formatters, **data)
    return site
        

def _dump_encode(data):
    """
    Encode dive computer data, so it can be stored in UDDF file.

    The encoded string is returned.
    """
    s = bz2.compress(data)
    return base64.b64encode(s)


def create_uddf(datetime=datetime.now(), equipment=None, gases=None, dives=None,
        dump=None):
    """
    Create UDDF XML data.

    :Parameters:
     datetime
        Timestamp of UDDF creation.
     equipment
        Diver's (owner) equipment XML data (see create_dc_data).
     gases
        List of gases used by the dives.
     dives
        Dives XML data (see create_dives).
     dump
        Dive computer dump XML data (see create_dump_data).
    """
    doc = xml.uddf(
        xml.generator(
            xml.name('kenozooid'),
            xml.manufacturer(
                xml.name('Kenozooid Team'),
                xml.contact(xml.homepage('http://wrobell.it-zone.org/kenozooid/')),
                id='kenozooid'),
            xml.version(kenozooid.__version__),
            xml.datetime(FMT_DT(datetime)),
        ),

        xml.diver(
            xml.owner(
                xml.personal(xml.firstname('Anonymous'), xml.lastname('Guest')),
                xml.equipment(equipment) if equipment else None,
                id='owner')),

        xml.divecomputercontrol(dump) if dump else None,
        xml.gasdefinitions(gases) if gases else None,
        xml.profiledata(xml.repetitiongroup(dives, id=gen_id()))
            if dives else None,

        xmlns=_NSMAP['uddf'],
        version='3.2.0',
    )
    return doc


def create_dives(dives, equipment=None):
    """
    Create dives UDDF XML data.

    :Parameters:
     dives
        Iterable of dive tuples.
     equipment
        List of used equipment references.
    """
    for dive in dives:
        log.debug('convert dive {0.datetime}/{0.depth:.1f}/{0.duration} into XML'
                .format(dive))
        yield create_dive(dive, equipment)


def create_dive(dive, equipment=None):
    """
    Create dive UDDF XML data.

    :Parameters:
     dive
        Dive to render as XML.
     equipment
        List of used equipment references.
    """
    eq = itertools.chain(kt.nit(dive.equipment), kt.nit(equipment))
    log.debug('convert dive {0.datetime}/{0.depth:.1f}/{0.duration} into XML'
            .format(dive))
    return xml.dive(
        xml.informationbeforedive(xml.datetime(FMT_DT(dive.datetime))),
        xml.samples(create_dive_samples(dive.profile, dive.mode)),
        xml.informationafterdive(
            xml.greatestdepth(FMT_F(dive.depth)),
            xml.diveduration(FMT_I(dive.duration)),
            None if dive.temp is None else xml.lowesttemperature(FMT_F(dive.temp)),
            xml.equipmentused((xml.link(ref=v) for v in eq)),
            None if dive.avg_depth is None else xml.averagedepth(FMT_F(dive.avg_depth)),
        ),
        id=gen_id(),
    )


def create_dive_samples(samples, mode=None):
    """
    Create dive samples UDDF XML data.

    :Parameters:
     samples
        Iterable of tuples of dive samples.
     mode
        Dive mode, i.e. opencircuit, closedcircuit.
    """
    for i, s in enumerate(samples):
        yield xml.waypoint(
            None if s.alarm is None else (xml.alarm(a) for a in s.alarm),
            None if s.deco_time is None else
                xml.decostop(
                    duration=FMT_I(s.deco_time),
                    decodepth=FMT_I(s.deco_depth),
                    kind='mandatory'
                ),
            xml.depth(FMT_F(s.depth)),
            xml.divetime(FMT_I(s.time)),
            None if s.setpoint is None else xml.setpo2(FMT_F2(s.setpoint),
                setby=s.setpointby),
            None if s.gas is None else xml.switchmix(ref=str(s.gas.id)),
            None if s.temp is None else xml.temperature(FMT_F(s.temp)),
            None if mode is None or i > 0 else xml.divemode(type=mode),
        )


def create_gas(gas):
    """
    Create gas UDDF XML data.

    :Parameters:
     gas
        Gas information to render as XML.
    """
    return xml.mix(
        xml.name(gas.name),
        xml.o2(str(gas.o2)),
        xml.he(str(gas.he)),
        id=gas.id,
    )


def create_dc_data(dc_id, model):
    """
    Create dive computer UDDF XML data.

    :Parameters:
     dc_id
        Dive computer id.
     model
        Dive computer model.
    """
    yield xml.divecomputer(xml.name(model), xml.model(model), id=dc_id)


def create_dump_data(dc_id, datetime, data):
    """
    Create dive computer dump UDDF XML data.

    :Parameters:
     dc_id
        Dive computer id.
     datetime
        Date and time when the dump was created.
     data
        Dive computer binary data.
    """
    yield xml.divecomputerdump(
        xml.link(ref=dc_id),
        xml.datetime(FMT_DT(datetime)),
        xml.dcdump(_dump_encode(data).decode()),
    )


def save(doc, fout, validate=True):
    """
    Save UDDF XML data into a file.

    If output file is file name ending with '.bz2', then it is compressed
    with bzip2.

    The UDDF XML data can be ElementTree XML object or iterable of strings.

    If output file exists then backup file with ``.bak`` extension is
    created.

    :Parameters:
     doc
        UDDF XML data.
     fout
        Output file.
     validate
        Validate UDDF file after saving if True.
    """
    log.debug('saving uddf file')
    is_fn = isinstance(fout, str)
    openf = open
    if is_fn and fout.endswith('.bz2'):
        openf = bz2.BZ2File
        log.debug('uddf file will be compressed')

    fbk = '{}.bak'.format(fout)
    if is_fn and os.path.exists(fout):
        os.rename(fout, fbk)
        log.debug('backup file created')
    try:
        f = openf(fout, 'wb') if is_fn else fout

        if et.iselement(doc):
            et.ElementTree(doc).write(f,
                    encoding='utf-8',
                    xml_declaration=True,
                    pretty_print=True)
        else:
            f.writelines(l.encode('utf-8') for l in doc)

        if validate:
            log.debug('validating uddf file')
            fs = pkg_resources.resource_stream('kenozooid', 'uddf/uddf_3.2.0.xsd')
            if hasattr(fs, 'name'):
                log.debug('uddf xsd found: {}'.format(fs.name))
            schema = et.XMLSchema(et.parse(fs))
            if is_fn:
                f = openf(fout)
            else:
                f.seek(0)
            schema.assertValid(et.parse(f))
            log.debug('uddf file is valid')
    except Exception as ex:
        if os.path.exists(fbk):
            os.rename(fbk, fout)
            log.debug('backup file restored')
        raise ex


#
# Removing UDDF data.
#

def remove_nodes(node, query, **params):
    """
    Remove nodes from XML document using XPath query.

    :Parameters:
     node
        Starting XML node for XPath query.
     query
        XPath query to find nodes to remove.
     params
        XPath query parameters.
    """
    log.debug('node removal with query: {}, params: {}'.format(query, params))
    for n in query(node, **params):
        p = n.getparent()
        p.remove(n)

#
# Processing UDDF data.
#


def reorder(doc):
    """
    fixme: obsolete

    Reorder and cleanup dives in UDDF document.

    Following operations are being performed

    - dives are sorted by dive start time 
    - duplicate dives and repetition groups are removed

    :Parameters:
     doc
        UDDF document.
    """
    find = partial(doc.xpath, namespaces=_NSMAP)

    profiles = find('//uddf:profiledata')
    rgroups = find('//uddf:profiledata/uddf:repetitiongroup')
    if not profiles or not rgroups:
        raise ValueError('No profile data to reorder')
    pd = profiles[0]

    q = '/uddf:uddf/uddf:profiledata/uddf:repetitiongroup/uddf:dive'
    qt = q + '/uddf:informationbeforedive/uddf:datetime/text()'
    nodes = find(q)
    times = find(qt)

    dives = {}
    for n, t in zip(nodes, times):
        dt = dparse(t) # don't rely on string representation for sorting
        if dt not in dives:
            dives[dt] = n

    log.debug('removing old repetition groups')
    for rg in rgroups: # cleanup old repetition groups
        pd.remove(rg)
    rg, = create_node('uddf:repetitiongroup', parent=pd)
    _set_id(rg)

    # sort dive nodes by dive time
    log.debug('sorting dives')
    for dt, n in sorted(dives.items(), key=itemgetter(0)):
        rg.append(n)


class NodeCopier(object):
    """
    UDDF dcument node copier.

    See :py:func:`NodeCopier.copy` for details.

    :Attributes:
     doc
        The target document.
     doc_ids
        The cache of target document ids.
    """
    def __init__(self, doc):
        """
        Initialize node copier.
        """
        self.doc = doc
        self.doc_ids = set(xp(doc, '//uddf:*/@id'))


    def __enter__(self):
        """
        Create UDDF node copier context manager.
        """
        return self


    def __exit__(self, *args):
        """
        Close UDDF node copier context manager.
        """
        pass


    def copy(self, node, target):
        """
        Copy node from UDDF document to target node in destination UDDF
        document. Target node becomes parent of node to be copied.

        The copying works under following assumptions

        - whole node is being copied including its descendants
        - node is not copied if it has id and id already exists in the target
        - if copied nodes reference non-descendant nodes and they do _not_
          exist in destination document, then referencing nodes are _removed_
        - if, due to node removal, its parent node becomes empty, then parent
          is removed, too

        Copy of the node is returned.

        :Parameters:
         node
            Node to copy.
         target
            The future parent of the copied node.
        """
        cn = deepcopy(node)

        cn_id = cn.get('id')
        if cn_id in self.doc_ids:
            log.debug('id {} already exists, not copying'.format(cn_id))
            return None

        s_ids = set(xp(cn, 'descendant-or-self::uddf:*/@id'))
        self.doc_ids.update(s_ids)

        # get referencing nodes
        nodes = list(xp(cn, 'descendant-or-self::uddf:*[@ref]'))
        refs = set(k.get('ref') for k in nodes)

        left = refs - self.doc_ids
        if __debug__:
            log.debug('references to remove: {} = {} - {}'.format(left,
                refs, self.doc_ids))

        if cn.get('ref') in left:
            raise ValueError('Node to copy references non-existing node')

        # remove nodes referencing missing data
        to_remove = (n for n in nodes if n.get('ref') in left)
        assert cn.getparent() is None
        for n in to_remove:
            p = n.getparent()
            while p is not None and len(p) == 1:
                n = p
                p = n.getparent()
            if p is not None:
                p.remove(n)

        target.append(cn)
        return cn


def _set_id(node):
    """
    Generate id for a node if there is no id yet.

    :Parameters:
     node
        Node for which id should be generated.
    """
    if node.get('id') is None:
        node.set('id', FORMAT_ID.format(uuid().hex))


def gen_id(value=None):
    """
    Generate id for a value.
    
    If value is specified then id is MD5 hash of value. If not specified,
    then id is generated with UUID 4.

    The returned id is a string prefixed with ``id-`` to make it XML
    compliant.
    """
    if value is None:
        vid = uuid().hex
    else:
        vid = hashlib.md5(str(value).encode()).hexdigest()
    return 'id-{}'.format(vid)


def xml_file_copy(f):
    """
    Iterator of raw XML data from a file to data into ``dirty.xml`` nodes.

    :Parameters:
     f
        File containing XML data.
    """
    while True:
        l = f.read(4096)
        if not l:
            break
        yield RawString(l)


def get_version(f):
    """
    Get major version of UDDF file.

    Tuple (major, minor) is returned, i.e. (3, 0), (3, 1), etc.

    :Parameters:
     f
        File to check.
    """
    n = parse(f, ver_check=False).getroot()
    v1, v2, *_ = n.get('version').split('.')
    if isinstance(f, FileIO):
        f.seek(0, 0)
    log.debug('detected version {}.{}'.format(v1, v2))
    return int(v1), int(v2)


# vim: sw=4:et:ai
