import os
import csv
from datetime import date, datetime
from pprint import pprint

csvs = [file for file in os.listdir('outputs/csvs') if file.endswith('.csv')]

dates = set()

def get_datetime(text):
    """
    Get a datetime object from the given text in the format of the PDFs
    """
    try:
        return datetime.strptime(text.upper(), "%m/%d/%Y %I:%M:%S %p")
    except:
        return None

if __name__ == '__main__':
    for filename in csvs:
        reader = csv.reader(open(os.path.join('outputs/csvs/', filename), 'r'))
        fields = next(reader) # skip the header
        for line in reader:
            if line[1] and line[2]:
                dates.add(get_datetime(line[2]))
    pprint(sorted({dt.date() for dt in dates}))


