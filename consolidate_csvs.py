from count_dates import get_datetime, csvs
import os
import csv
from pprint import pprint

"""
Consolidate CSVs into a single one, also filtering by points which have an officer
"""

OUTPUT = 'output.csv'

lines = []
the_fields = None

for filename in csvs:
    reader = csv.reader(open(os.path.join('outputs/csvs/', filename), 'r'))
    fields = next(reader) # skip the header
    if not the_fields:
        the_fields = fields
    for line in reader:
        # NOTE THAT rep_time may be missing! in which case it will be None
        if line[1] and line[2] and line[5]:
            line[2] = get_datetime(line[2])
            line[3] = get_datetime(line[3])
            # We only want 2021 and later for now
            if line[2].year >= 2021:
                lines.append(line)

# sort by occ_time
lines.sort(key=lambda line: line[2])
# They're ascending, we want descending

# but hold up, we can add the fields then reverse :)
lines.append(the_fields)
lines.reverse()

writer = csv.writer(open(OUTPUT, 'w'))
writer.writerows(lines)

# Note that the `id` field is now useless, but let's leave it for comparison purposes IDK
# Just don't use it; it's useless