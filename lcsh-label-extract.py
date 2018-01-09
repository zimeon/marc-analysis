#!/usr/bin/python

import argparse
import logging
from rdflib import Graph
from rdflib.namespace import RDF, SKOS
from rdflib.plugins.parsers.ntriples import NTriplesParser

class GraphSink(object):

    def __init__(self, graph=None):
        """Initialize GraphSink object."""
        self.length = 0
        self.graph = graph

    def triple(self, s, p, o):
        """Add triple to graph."""
        self.graph.add((s, p, o))


class FilterSink(object):

    def __init__(self, sink=None, triple_patterns=None, stop_after=None):
        """Initialize FilterSink object.

        Parameters:

        triples_patterns - a list of triple patterns, each expressed as a tuple
            of (ps, po, pp) where each value may be None to match anything, or a
            specific value. A triple matching any of the supplied patterns will
            be added to the filtered graph.
        stop_after - set to an integer to limit the number of triples collected
            after filtering. Will raise StopIteration exception if the limit is
            reached before the end of the input.
        """
        self.length = 0
        self.sink = sink
        self.triple_patterns = triple_patterns
        self.stop_after = stop_after

    def triple(self, s, p, o):
        """Add triple to sink.

        Required method of a sink object for NTriplesParser to work. Input arguments
        are the subject, predecate and object of the new triple.
        """
        # Conditions
        if self.triple_patterns is not None:
            match = False
            for ps, pp, po in self.triple_patterns:
                if ((ps is None or ps == s) and
                    (pp is None or pp == p) and
                    (po is None or po == o)):
                    match = True
                    break
            if not match:
                return
        # Add triple
        self.length += 1
        if (self.stop_after is not None and
            self.length >= self.stop_after):
            raise StopIteration("Reached limit of %d triples extracted" % (self.stop_after))
        self.sink.triple(s, p, o)


def main():
    """Command line handler."""
    parser = argparse.ArgumentParser(description='Extract data from LCSH',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--lcsh-skos',  default='authoritiessubjects.skos.nt',
                        help='LCSH SKOS description in ntriples format')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="be verbose.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    g = Graph()
    try:
        triple_patterns = [(None, RDF.type, SKOS.Concept),
                           (None, SKOS.prefLabel, None),
                           (None, SKOS.altLabel, None)]
        p = NTriplesParser(sink=FilterSink(sink=GraphSink(graph=g),
                                           stop_after=None,
                                           triple_patterns=triple_patterns))
        s = p.parse(open(args.lcsh_skos, 'rb'))
    except StopIteration as e:
        logging.warn(str(e))

    n = 0
    for s, p, o in g.triples(None, RDF.type, SKOS.Concept):
        n += 1
    print("Got %d terms" % n)    
    #print(g.serialize(format='nt'))


if __name__ == "__main__":
    main()
