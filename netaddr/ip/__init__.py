#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Provides access to public network address information published by IANA.

More details can be found at the following URLs :-

Internet Assigned Numbers Authority (IANA)

    - http://www.iana.org/
    - http://www.iana.org/protocols/
"""

import os as _os
import os.path as _path
import re as _re

from netaddr.core import Publisher, Subscriber, PrettyPrinter
from netaddr import AT_INET, AT_INET6
from netaddr.address import CIDR, IPRange

#-----------------------------------------------------------------------------

#: Topic based lookup dictionary for IANA information.
IANA_INFO = {
    'IPv4'      : {},
    'IPv6'      : {},
    'multicast' : {},
}

#-----------------------------------------------------------------------------
class LineRecordParser(Publisher):
    """
    A configurable Parser that understands how to parse line based records.
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to line based record data.
        """
        super(LineRecordParser, self).__init__()
        self.fh = fh

        self.__dict__.update(kwargs)

        #   Regex used to identify start of lines of interest.
        if 're_start' not in self.__dict__:
            self.re_start = r'^.*$'

        #   Regex used to identify line to be parsed within block of interest.
        if 're_parse_line' not in self.__dict__:
            self.re_parse_line = r'^.*$'

        #   Regex used to identify end of lines of interest.
        if 're_stop' not in self.__dict__:
            self.re_stop = r'^.*$'

        #   If enabled, skips blank lines after being stripped.
        if 'skip_blank_lines' not in self.__dict__:
            self.skip_blank_lines = False

    def parse_line(self, line):
        """
        This is the callback method invoked for every line considered valid by
        the line parser's settings. It is usually over-ridden by base classes
        to provide specific line parsing and line skipping logic.

        Any line can be vetoed (not passed to registered Subscriber objects)
        by simply returning None.
        """
        return line

    def parse(self):
        """
        Parse and normalises records, notifying registered subscribers with
        record data as it is encountered.
        """
        record = None
        section_start = False
        section_end = False

        for line in self.fh:
            line = line.strip()

            #   Skip blank lines if required.
            if self.skip_blank_lines and line == '':
                continue

            #   Entered record section.
            if not section_start and len(_re.findall(self.re_start, line)) > 0:
                section_start = True

            #   Exited record section.
            if section_start and len(_re.findall(self.re_stop, line)) > 0:
                section_end = True

            #   Stop parsing.
            if section_end:
                break

            #   Is this a line of interest?
            if section_start and len(_re.findall(self.re_parse_line, line)) == 0:
                continue

            if section_start:
                record = self.parse_line(line)

                #   notify subscribers of final record details.
                self.notify(record)

#-----------------------------------------------------------------------------
class IPv4Parser(LineRecordParser):
    """
    A LineRecordParser that understands how to parse and retrieve data records
    from the IANA IPv4 address space file.

    It can be found online here :-

    http://www.iana.org/assignments/ipv4-address-space
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to an OUI Registry data file.

        kwargs - additional parser options.

        """
        super(IPv4Parser, self).__init__(fh,
            re_start=r'^Prefix',
            re_parse_line=r'^\d{3}\/\d',
            re_stop=r'^Notes\s*$',
            skip_blank_lines=True,
        )

        self.record_widths = (
            ('prefix', 0, 8),
            ('designation', 8, 49),
            ('date', 57, 10),
            ('whois', 67, 20),
            ('status', 87, 19),
        )

    def parse_line(self, line):
        """
        Callback method invoked for every line considered valid by the line
        parser's settings.

        See base class method for more details.
        """
        record = {}
        for (key, start, width) in self.record_widths:
            value = line[start:start+width]
            record[key] = value.strip()

        #   Strip leading zeros from octet.
        if '/' in record['prefix']:
            (octet, prefix) = record['prefix'].split('/')
            record['prefix'] = "%d/%d" % (int(octet), int(prefix))

        record['status'] = record['status'].capitalize()

        return record

#-----------------------------------------------------------------------------
class IPv6Parser(LineRecordParser):
    """
    A LineRecordParser that understands how to parse and retrieve data records
    from the IANA IPv6 address space file.

    It can be found online here :-

    http://www.iana.org/assignments/ipv6-address-space
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to an OUI Registry data file.

        kwargs - additional parser options.

        """
        super(IPv6Parser, self).__init__(fh,
        re_start=r'^IPv6 Prefix',
        re_parse_line=r'^[A-F0-9]+::\/\d+',
        re_stop=r'^Notes:\s*$',
            skip_blank_lines=True)

        self.record_widths = (
            ('prefix', 0, 22),
            ('allocation', 22, 24),
            ('reference', 46, 15))

    def parse_line(self, line):
        """
        Callback method invoked for every line considered valid by the line
        parser's settings.

        See base class method for more details.
        """
        record = {}
        for (key, start, width) in self.record_widths:
            value = line[start:start+width]
            record[key] = value.strip()

            #   Remove square brackets from reference field.
            record[key] = record[key].lstrip('[')
            record[key] = record[key].rstrip(']')
        return record

#-----------------------------------------------------------------------------
class MulticastParser(LineRecordParser):
    """
    A LineParser that knows how to process the IANA IPv4 multicast address
    allocation file.

    It can be found online here :-

    http://www.iana.org/assignments/multicast-addresses
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to an OUI Registry data file.

        kwargs - additional parser options.

        """
        super(MulticastParser, self).__init__(fh,
        re_start=r'^Registry:',
        re_parse_line=r'^\d+\.\d+\.\d+\.\d+',
        re_stop=r'^Relative',
            skip_blank_lines=True)

    def normalise_addr(self, addr):
        """
        Removes variations from address entries found in this particular file.
        """
        if '-' in addr:
            (a1, a2) = addr.split('-')
            o1 = a1.strip().split('.')
            o2 = a2.strip().split('.')
            return "%s-%s" % ('.'.join([str(int(i)) for i in o1]),
                              '.'.join([str(int(i)) for i in o2]))
        else:
            o1 = addr.strip().split('.')
            return '.'.join([str(int(i)) for i in o1])

    def parse_line(self, line):
        """
        Callback method invoked for every line considered valid by the line
        parser's settings.

        See base class method for more details.
        """
        index = line.find('[')
        if index != -1:
            line = line[0:index].strip()
        (addr, descr) = [i.strip() for i in _re.findall(
            r'^([\d.]+(?:\s*-\s*[\d.]+)?)\s+(.+)$', line)[0]]
        addr = self.normalise_addr(addr)
        descr = ' '.join(descr.split())
        descr = descr.replace('Date registered' , '').rstrip()

        return dict(address=addr, descr=descr)

#-----------------------------------------------------------------------------
class DictUpdater(Subscriber):
    """
    Concrete Subscriber that inserts records received from a Publisher into a
    dictionary.
    """
    def __init__(self, dct, topic, unique_key):
        """
        Constructor.

        dct - lookup dict or dict like object to insert records into.

        topic - high-level category name of data to be processed.

        unique_key - key name in data dict that uniquely identifies it.
        """
        self.dct = dct
        self.topic = topic
        self.unique_key = unique_key

    def update(self, data):
        """
        Callback function used by Publisher to notify this Subscriber about
        an update. Stores topic based information into dictionary passed to
        constructor.
        """
        data_id = data[self.unique_key]

        if self.topic == 'IPv4':
            cidr = CIDR(data_id)
            self.dct[cidr] = data
        elif self.topic == 'IPv6':
            cidr = CIDR(data_id)
            self.dct[cidr] = data
        elif self.topic == 'multicast':
            iprange = None
            if '-' in data_id:
                (first, last) = data_id.split('-')
                iprange = IPRange(first, last)
            else:
                iprange = IPRange(data_id, data_id)
            self.dct[iprange] = data

#-----------------------------------------------------------------------------
def load_iana_info():
    """
    Parse and load internal IANA data lookups with the latest information from
    data files.
    """
    PATH = _path.dirname(__file__)

    ipv4 = IPv4Parser(open(_path.join(PATH, 'ipv4-address-space')))
    ipv4.attach(DictUpdater(IANA_INFO['IPv4'], 'IPv4', 'prefix'))
    ipv4.parse()

    ipv6 = IPv6Parser(open(_path.join(PATH, 'ipv6-address-space')))
    ipv6.attach(DictUpdater(IANA_INFO['IPv6'], 'IPv6', 'prefix'))
    ipv6.parse()

    mcast = MulticastParser(open(_path.join(PATH, 'multicast-addresses')))
    mcast.attach(DictUpdater(IANA_INFO['multicast'], 'multicast', 'address'))
    mcast.parse()

#-----------------------------------------------------------------------------
def query(ip_addr):
    """
    Returns informational data specific to this IP address.
    """
    info = {}

    if ip_addr.addr_type == AT_INET:
        for cidr, record in IANA_INFO['IPv4'].items():
            if ip_addr in cidr:
                info.setdefault('IPv4', [])
                info['IPv4'].append(record)

        if ip_addr.is_multicast():
            for iprange, record in IANA_INFO['multicast'].items():
                if ip_addr in iprange:
                    info.setdefault('Multicast', [])
                    info['Multicast'].append(record)

    elif ip_addr.addr_type == AT_INET6:
        for cidr, record in IANA_INFO['IPv6'].items():
            if ip_addr in cidr:
                info.setdefault('IPv6', [])
                info['IPv6'].append(record)

    return info

#-----------------------------------------------------------------------------
def get_latest_files():
    """Download the latest files from IANA"""
    import urllib2

    urls = [
        'http://www.iana.org/assignments/ipv4-address-space',
        'http://www.iana.org/assignments/ipv6-address-space',
        'http://www.iana.org/assignments/multicast-addresses',
    ]

    for url in urls:
        print 'downloading latest copy of %s' % url
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        save_path = _path.dirname(__file__)
        basename = _os.path.basename(response.geturl().rstrip('/'))
        filename = _path.join(save_path, basename)
        fh = open(filename, 'wb')
        fh.write(response.read())
        fh.close()


#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #   Generate indices when module is executed as a script.
    get_latest_files()

#   On module import, read IANA data files and populate lookups dict.
load_iana_info()
