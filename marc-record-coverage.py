#!/usr/bin/env python
"""Given an order of MARC tags, how many of a set of records are covered."""
from optparse import OptionParser
from pymarc.marcxml import parse_xml_to_array
import gzip
import logging
import os
import os.path


class Coverage(object):
    """Class to accumulate record coverage stats."""

    def __init__(self, tags):
        """Initialize counters for Coverage object.

        Goal is to calculate number/fraction of records covered
        by supporting all tags in self.tag (in order) up to the
        given tag.
        """
        self.tags = tags
        self.num_records = 0
        self.num_bad = 0
        self.coverage = {}
        for t in tags:
            self.coverage[t] = 0

    def add(self, record):
        """Add a record to the stats."""
        try:
            # Set of tags used in this record
            tt = set()
            for field in record:
                tt.add(int(field.tag))
            # Count of self.tags until all covered
            for t in self.tags:
                tt.discard(t)
                if (len(tt) == 0):
                    self.coverage[t] += 1
                    break
            self.num_records += 1
        except:
            self.num_bad += 1

    def add_records(self, fh):
        """Read and add set of records from file."""
        records = parse_xml_to_array(fh)
        for record in records:
            self.add(record)

    def add_records_from_file(self, filepath):
        """Read records from file (plain or .gz)."""
        ext = os.path.splitext(filepath)[1]
        if (ext == '.gz'):
            with gzip.open(filepath, 'rb') as fh:
                self.add_records(fh)
        else:
            with open(filepath, 'r') as fh:
                self.add_records(fh)
        logging.info("[%d records...]" % (self.num_records))

    def __str__(self):
        """Write summary for all records added."""
        s = ("# Read %d records (ignored %d bad), with the following coverage results:\n" %
             (self.num_records, self.num_bad))
        total = 0
        for j in range(len(self.tags)):
            tag = self.tags[j]
            tag_subset = self.tags[0:(j + 1)]
            total += self.coverage[tag]
            tstr = "%s tags (%s)" % (j + 1, tag_summary(tag_subset))
            s += "%-30s  %8d (+%6d)  %4.1f%%\n" % (tstr, total, self.coverage[tag], (total * 100.0 / self.num_records))
        return(s)


def read_marc_tag_order(filename):
    """Read list of tags from filename, one per line.

    Stores integer values, not padded strings.
    """
    tags = []
    with (open(filename, 'r')) as fh:
        for line in fh:
            if (not line.startswith('#')):
                tags.append(int(line.split()[0]))
    logging.info("Read a list of %d tags (%s)" % (len(tags), tag_summary(tags)))
    return tags


def tag_summary(tags):
    """Generate summary string of tags list, at most one from start, three from end."""
    if (len(tags) <= 4):
        t = tags
    else:
        t = [tags[0], '...', tags[-3], tags[-2], tags[-1]]
    return ','.join((x if isinstance(x, str) else "%03d" % x) for x in t)


def main():
    """Command line handler."""
    parser = OptionParser()
    parser.add_option('--order-list', default='marc_tag_order.dat',
                      help="file with ordered list of tags, one per line (default %default)")
    parser.add_option('--verbose', '-v', action='store_true',
                      help="be verbose.")
    (opts, args) = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO)

    tags = read_marc_tag_order(opts.order_list)

    stats = Coverage(tags)
    for top in args:
        if (os.path.isfile(top)):
            logging.info("Reading %s" % (top))
            stats.add_records_from_file(top)
        else:
            logging.info("Looking under %s" % (top))
            for (dirpath, dirnames, filenames) in os.walk(top):
                for name in filenames:
                    filepath = os.path.join(dirpath, name)
                    logging.info("Reading %s" % (filepath))
                    stats.add_records_from_file(filepath)
    print(stats)

if __name__ == "__main__":
    main()
