#!/usr/bin/env python
"""Extract list of MARC tags mentioned in BSR document.

Save extracted text from Word version of BSR spec using
Latin-US (DOS) encoding to avoid UTF-8 issues -- there
is nothing non-ASCII in the data we are looking for.
"""
import re
import sys

tags = set()
subs = set()
n = 0
for line in sys.stdin:
    n += 1
    if (not re.search(r'\d[\dX][\dX]', line)):
        continue  # if nothing looks like a tag
    line = re.sub(r',\s*etc\.', '', line, flags=re.S)  # remove etc
    line = re.sub(r'\s*\([^\)]+\)', '', line, flags=re.S)  # any parens
    line = re.sub(r'\b(00\d)\/[\d\-]+', r'\1', line, flags=re.S)
    line = re.sub(r'\s*(,|;|or)\s*', ',', line, flags=re.S)
    #print("%d# %s" % (n, line))
    for tag in line.split(','):
        m = re.match(r'\s*((\d[\dX][\dX])(\$\w+)?)\s*$', tag)
        if (m):
            print("%d# %s" % (n, tag))
            tags.add(m.group(2))
            if (m.group(3)):
                subs.add(m.group(1))
        else:
            print("ignored: %s" % (tag))

print("#TAGS: " + ','.join(sorted(tags)))
print("#SUBS: " + ','.join(sorted(subs)))
