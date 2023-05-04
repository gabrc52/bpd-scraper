import csv
import opencage
import pickle
import os
import sys
from dotenv import load_dotenv, find_dotenv
from opencage.geocoder import OpenCageGeocode, UnknownError, InvalidInputError, RateLimitExceededError
import googlemaps
load_dotenv()
OPENCAGE_KEY = os.getenv('OPENCAGE')
GOOGLE_KEY = os.getenv('GOOGLE')
geocoder = OpenCageGeocode(OPENCAGE_KEY)
gmaps = googlemaps.Client(key=GOOGLE_KEY)

INPUT = 'output.csv'
OUTPUT = 'outputs/police_journal.csv'
# OUTPUT = 'debug.csv'

# if cache not found, create it
if not os.path.exists('opencage.pickle'):
    pickle.dump(dict(), open('opencage.pickle', 'wb'))
if not os.path.exists('google.pickle'):
    pickle.dump(dict(), open('google.pickle', 'wb'))

def load_cached_address(address, service):
    addresses = pickle.load(open(f'{service}.pickle', 'rb'))
    if address in addresses:
        return addresses[address]

def save_cached_address(address, geocoded, service):
    addresses = pickle.load(open(f'{service}.pickle', 'rb'))
    addresses[address] = geocoded
    pickle.dump(addresses, open(f'{service}.pickle', 'wb'))

def geocode(addr, force_google=False):
    """
    Geocodes an address, returning a tuple (coords, cleaned address, condience)
    """
    if '&' in addr or force_google:
        # OpenCage cannot deal with addresses with &
        cached = load_cached_address(addr, 'google')
        if cached:
            print(f'{addr} was cached by google', file=sys.stderr)
            return cached
        print(f'Google is geocoding {addr}')
        results = gmaps.geocode(addr)
        result = results[0]
        fields = (result['geometry']['location']['lat'], result['geometry']['location']['lng']), result['formatted_address'], 'google'
        save_cached_address(addr, fields, 'google')
    else:
        cached = load_cached_address(addr, 'opencage')
        if cached:
            print(f'{addr} was cached by opencage', file=sys.stderr)
            return cached
        print(f'OpenCage is geocoding {addr}', file=sys.stderr)
        results = geocoder.geocode(addr, countrycode='us', no_annotations=1, no_record=1)
        result = results[0]
        fields = (result['geometry']['lat'], result['geometry']['lng']), result['formatted'], result['confidence']
        save_cached_address(addr, fields, 'opencage')
    return fields

reader = csv.reader(open(INPUT, 'r'))
fields = next(reader)
fields.extend(['lat', 'lng', 'geocoded_addr', 'confidence'])

# Now to the actual geocoding
writer = csv.writer(open(OUTPUT, 'w'))
writer.writerow(fields)
for line in reader:
    address = line[5]
    coords, formatted_address, confidence = geocode(address)
    line.extend([coords[0], coords[1], formatted_address, confidence])
    writer.writerow(line)
    
