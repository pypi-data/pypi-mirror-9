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
Kenozooid's logbook command line user interface.
"""

import sys
import os.path
from functools import partial
import logging

from kenozooid.component import inject
from kenozooid.cli import CLICommand, ArgumentError, add_master_command, \
    add_uddf_input
from kenozooid.component import query, params
from kenozooid.util import nformat

log = logging.getLogger('kenozooid.cli.logbook')


# for commands 'dive add', 'dive list', etc
add_master_command('dive',
        'Kenozooid dive management commands',
        'manage dives in UDDF file')

# for commands 'site add', 'site list', etc
add_master_command('site',
        'Kenozooid dive site management commands',
        'manage dive sites in UDDF file')

# for commands 'buddy add', 'buddy list', etc
add_master_command('buddy',
        'Kenozooid dive buddy management commands',
        'manage dive buddies in UDDF file')


@inject(CLICommand, name='dive list')
class ListDives(object):
    """
    List dives from UDDF file.
    """
    description = 'list dives stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive list fetched from UDDF file.
        """
        parser.add_argument('input',
                nargs='+',
                help='UDDF files with dive data')


    def __call__(self, args):
        """
        Execute command for list of dives in UDDF file.
        """
        import kenozooid.logbook as kl

        for fin in args.input:
            dives = kl.find_dives([fin])
            print('{}:'.format(fin))
            for i, d in enumerate(kl.list_dives(dives), 1):
                print('{:5}: {:>4} {:>9} {:>9} ({:>5}) {:>9} {:>9}'.format(i,
                    d[0] or ' -- ', d[1], d[2], d[3] or ' --- ', d[4], d[5]))



@inject(CLICommand, name='dive add')
class AddDive(object):
    """
    Add a dive to logbook file.
    """
    description = 'add dive to logbook file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive adding to logbook file.
        """
        parser.add_argument('datetime', help='date and optional time of a dive')
        parser.add_argument('depth', help='maximum depth of a dive')
        parser.add_argument('duration', help='duration of a dive')
        parser.add_argument('-s', '--site', metavar='site', help='dive site')
        parser.add_argument('-b', '--buddy',
                nargs='+',
                metavar='buddy',
                help='dive buddies')
        parser.add_argument('logbook', help='logbook file')


    def __call__(self, args):
        """
        Execute command for adding dives into logbook file.
        """
        import kenozooid.logbook as kl
        import kenozooid.data as kd
        from dateutil.parser import parse as dparse

        lfile = args.logbook

        datetime = dparse(args.datetime)
        depth = float(args.depth)
        duration = float(args.duration) * 60

        site = args.site
        buddy = args.buddy

        dive = kd.Dive(datetime=datetime, depth=depth, duration=duration)
        kl.add_dive(dive, lfile, qsite=site, qbuddies=buddy)



@inject(CLICommand, name='dive copy')
class CopyDive(object):
    """
    Copy dives to logbook file.
    """
    description = 'copy dives to logbook file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive copying to logbook file.
        """
        add_uddf_input(parser)
        parser.add_argument('logbook', help='logbook file')


    def __call__(self, args):
        """
        Execute command for copying dives into logbook file.
        """
        import kenozooid.logbook as kl

        r, f = args.input
        kl.copy_dives(f, r, args.dives, args.logbook)



@inject(CLICommand, name='site add')
class AddDiveSite(object):
    """
    Add dive site to UDDF file.
    """
    description = 'add dive site to UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive site adding to UDDF file.
        """
        parser.add_argument('-c', '--coords',
                nargs=2,
                metavar=('x', 'y'),
                type=float,
                help='coordinates (longitude and latitude) of dive site')
        #parser.add_argument('-c', '--country',
        #        nargs=1,
        #        metavar='country',
        #        help='dive site country, i.e. Ireland')
        #parser.add_argument('-p', '--province',
        #        nargs=1,
        #        metavar='province',
        #        help='dive site province, i.e. Howth')
        parser.add_argument('id',
                nargs='?',
                help='id of dive site')
        parser.add_argument('location',
                nargs=1,
                help='location of dive site, i.e. Scapa Flow, Red Sea')
        parser.add_argument('name',
                nargs=1,
                help='name of dive site, i.e. SMS Markgraf, SS Thistlegorm')
        parser.add_argument('output',
                nargs=1,
                help='UDDF output file')


    def __call__(self, args):
        """
        Execute command for adding dive site into UDDF file.
        """
        import kenozooid.uddf as ku

        id = args.id
        if args.coords:
            x, y = args.coords
        else:
            x, y = None, None
        location = args.location[0]
        name = args.name[0]
        fout = args.output[0]

        if os.path.exists(fout):
            doc = ku.parse(fout).getroot()
        else:
            doc = ku.create()

        ku.create_site_data(doc, id=id, location=location, name=name, x=x, y=y)
        ku.save(doc, fout)



@inject(CLICommand, name='site list')
class ListDiveSites(object):
    """
    List dive sites from UDDF file.
    """
    description = 'list dive sites stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive site list fetched from UDDF file.
        """
        parser.add_argument('site',
                nargs='?',
                help='dive site search string; matches id or partially dive' \
                    ' site name')
        parser.add_argument('input',
                nargs='+',
                help='UDDF files with dive sites')


    def __call__(self, args):
        """
        Execute command for list of dive sites in UDDF file.
        """
        import kenozooid.uddf as ku

        fmt = '{0:4}: {1.id:10} {1.location:20} {1.name:20}'

        if args.site:
            query = ku.XP_FIND_SITE
        else:
            query = '//uddf:site'
        files = args.input

        for fin in files:
            nodes = ku.find(fin, query, site=args.site)
            print('{}:'.format(fin))
            for i, n in enumerate(nodes):
                n = ku.site_data(n)

                coords = ''
                if n.x is not None:
                    coords = '  {0.x: #.9},{0.y: #.9}'.format(n)

                print(nformat(fmt, i + 1, n) + coords)



@inject(CLICommand, name='site del')
class DelDiveSite(object):
    """
    Remove dive site from UDDF file.
    """
    description = 'remove dive site stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for removal of dive site from UDDF file.
        """
        parser.add_argument('site',
                nargs=1,
                help='dive site search string; matches id or partially dive' \
                    ' site name')
        parser.add_argument('input',
                nargs=1,
                help='UDDF file with dive sites')


    def __call__(self, args):
        """
        Execute command for removal of dive sites from UDDF file.
        """
        import kenozooid.uddf as ku

        query = ku.XP_FIND_SITE
        fin = args.input[0]

        doc = ku.parse(fin)
        ku.remove_nodes(doc, query, site=args.site[0])
        ku.save(doc.getroot(), fin)



@inject(CLICommand, name='buddy add')
class AddBuddy(object):
    """
    Add dive buddy to UDDF file.
    """
    description = 'add dive buddy to UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive buddy adding to UDDF file.
        """
        parser.add_argument('-m', '--member',
                nargs=2,
                metavar=('org', 'number'),
                help='organization and its member id number i.e. CFT 123')
        parser.add_argument('id',
                nargs='?',
                help='id of a buddy, i.e. tcora')
        parser.add_argument('name',
                nargs=1,
                help='buddy name, i.e. "Tom Cora", "Thomas Henry Corra"'
                    ' or "Corra, Thomas Henry"')
        parser.add_argument('output',
                nargs=1,
                help='UDDF output file')


    def __call__(self, args):
        """
        Execute command for adding dive buddy into UDDF file.
        """
        import kenozooid.uddf as ku

        if args.member:
            org, number = args.member
        else:
            org, number = None, None

        id = args.id
        fn, mn, ln = _name_parse(args.name[0])
        fout = args.output[0]

        if os.path.exists(fout):
            doc = ku.parse(fout).getroot()
        else:
            doc = ku.create()

        ku.create_buddy_data(doc, id=id, fname=fn, mname=mn,
                lname=ln, org=org, number=number)

        ku.save(doc, fout)


@inject(CLICommand, name='buddy list')
class ListBuddies(object):
    """
    List dive buddies from UDDF file.
    """
    description = 'list dive buddies stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive buddy list fetched from UDDF file.
        """
        parser.add_argument('buddy',
                nargs='?',
                help='buddy search string; matches id, member number or'
                ' partially firstname or lastname')
        parser.add_argument('input',
                nargs='+',
                help='UDDF file with dive buddies')


    def __call__(self, args):
        """
        Execute command for list of dive buddies in UDDF file.
        """
        import kenozooid.uddf as ku

        fmt = '{0:4}: {1.id:10} {1.fname:10} {1.lname:20}' \
                ' {1.org:5} {1.number:11}'

        if args.buddy:
            query = ku.XP_FIND_BUDDY
        else:
            query = '//uddf:buddy'
        files = args.input

        for fin in files:
            nodes = ku.find(fin, query, buddy=args.buddy)
            print('{}:'.format(fin))
            for i, n in enumerate(nodes):
                b = ku.buddy_data(n)
                print(nformat(fmt, i + 1, b))


@inject(CLICommand, name='buddy del')
class DelBuddy(object):
    """
    Remove dive buddies from UDDF file.
    """
    description = 'remove dive buddies stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for removal of dive buddy from UDDF file.
        """
        parser.add_argument('buddy',
                nargs=1,
                help='buddy search string; matches id, member number or'
                ' partially firstname or lastname')
        parser.add_argument('input',
                nargs=1,
                help='UDDF file with dive buddies')


    def __call__(self, args):
        """
        Execute command for removal of dive buddies from UDDF file.
        """
        import kenozooid.uddf as ku

        query = ku.XP_FIND_BUDDY
        fin = args.input[0]

        doc = ku.parse(fin)
        ku.remove_nodes(doc, query, buddy=args.buddy[0])
        ku.save(doc.getroot(), fin)


@inject(CLICommand, name='upgrade')
class UpgradeFile(object):
    """
    Upgrade a file to newer version of UDDF.
    """
    description = 'upgrade UDDF file to newer version'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for UDDF file format upgrade.
        """
        parser.add_argument('input',
                nargs='+',
                help='input UDDF file')


    def __call__(self, args):
        """
        Execute command UDDF file upgrade.
        """
        import kenozooid.uddf as ku
        import kenozooid.logbook as kl

        for fin in args.input:
            try:
                print('Upgrading {}'.format(fin))
                doc = kl.upgrade_file(fin)
                ku.save(doc.getroot(), fin)
            except Exception as ex:
                print('Cannot upgrade file {}'.format(fin), file=sys.stderr)
                print('Error: {}'.format(ex))



@inject(CLICommand, name='dive enum')
class EnumDives(object):
    """
    Enumerate dives.
    """
    description = 'enumerate dives'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive enumeration.
        """
        parser.add_argument('-ns', '---dive-total-number',
                metavar='dive_total_number',
                nargs='?',
                type=int,
                default=1,
                help='start of total dive number')
        parser.add_argument('input',
                nargs='+',
                help='UDDF files with dive data')


    def __call__(self, args):
        """
        Execute command to enumerate dives.
        """
        import kenozooid.logbook as kl
        kl.enum_dives(args.input, args.dive_total_number)



def _name_parse(name):
    """
    Parse name data from a string. The name string is in simplified BibTeX
    format, i.e.

    - Tom
    - Tom Cora
    - Thomas Henry Corra
    - Corra, Thomas Henry

    Parsed name is tuple consisting of first name, middle name and last
    name.
    """
    f, m, l = None, None, None

    t = name.split(',')
    if len(t) == 1:
        nd = t[0].strip().split(' ', 2)
        if len(nd) == 3:
            f, m, l = nd
        elif len(nd) == 2:
            f, l = nd
        elif len(nd) == 1:
            f = nd[0]
    elif len(t) == 2:
        l = t[0].strip()
        nd = t[1].strip().split(' ', 1)
        f = nd[0]
        if len(nd) == 2:
            m = nd[1]
    else:
        raise ValueError('Cannot parse name')

    if f:
        f = f.strip()
    if m:
        m = m.strip()
    if l:
        l = l.strip()
    return f, m, l


# vim: sw=4:et:ai
