from clean_address import clean_address
import csv
import os

"""
Cleans the addresses from all CSVs in preparation for geocodingg

Modifies them in-place.
"""

if __name__ == '__main__':
    csvs = [file for file in os.listdir('outputs/csvs') if file.endswith('.csv')]

    for filename in csvs:
        reader = csv.reader(open(os.path.join('outputs/csvs/', filename), 'r'))
        fixed = [next(reader)]
        for line in reader:
            line[5] = clean_address(line[5])
            fixed.append(line)
        writer = csv.writer(open(os.path.join('outputs/csvs/', filename), 'w'))
        writer.writerows(fixed)

