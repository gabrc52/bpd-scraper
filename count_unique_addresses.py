import os
import csv

csvs = [file for file in os.listdir('outputs/csvs') if file.endswith('.csv')]

total_addresses = set()
officer_addresses = set()

for filename in csvs:
    reader = csv.reader(open(os.path.join('outputs/csvs/', filename), 'r'))
    fields = next(reader) # skip the header
    for line in reader:
        total_addresses.add(line[5])
        if line[1]:
            officer_addresses.add(line[5])

intersection_addresses = {address for address in officer_addresses if '&' in address}

print('Total addresses:', len(total_addresses))
print('Total addresses with officer data:', len(officer_addresses))
print('Total addresses with officer data and intersections:', len(intersection_addresses))

