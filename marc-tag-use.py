#!/usr/bin/env python
from optparse import OptionParser
from pymarc.marcxml import parse_xml_to_array
import gzip
import logging
import os
import os.path

class Stats(object):

    def __init__(self):
        """Initialize counters for Stats object."""
        self.num_records = 0
        self.num_bad = 0
        self.stats = {}
        for j in range(1000):
            self.stats[j] = 0

    def add(self, record):
        """Add a record to the stats."""
        try:
            last_tag = None
            for field in record:
                tag = int(field.tag)
                if (tag != last_tag):  # avoid double counting multiple field entries per record
                    self.stats[tag] += 1
                last_tag = tag
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
        s = ("# Read %d records (ignored %d bad), with the following field occurences:\n" %
             (self.num_records, self.num_bad))
        for (field, count) in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            if (count > 0):
                s += "%03d  %8d  %4.1f%%\n" % (field, count, (count * 100.0 / self.num_records))
        return(s)


def main():
    """Command line handler."""
    parser = OptionParser()
    parser.add_option('--verbose', '-v', action='store_true',
                      help="be verbose.")
    (opts, args) = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO)

    stats = Stats()
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
