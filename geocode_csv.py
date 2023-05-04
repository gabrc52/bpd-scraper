"""
Geocode the CSV in output.csv (or change INPUT below) into outputs/police_journal.csv (or change OUTPUT below)

You can run this, without fear of having to cancel and re-run.

You can Ctrl+C, and if you re-run, the cache will be used :)
Same for not having to geocode the same address twice

It will use the OpenCage geocoder whenever possible (no street intersections), otherwise it will use the Google geocoder.

To prefer Google, set FORCE_GOOGLE to True
"""

# TODO: might be good to add something to ensure Google doesn't charge us
# i.e. completely refuse any Google requests if the limit is reached

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
FORCE_GOOGLE = False # Change to force the use of Google geocoder instead of opencage
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

def geocode(addr, force_google=FORCE_GOOGLE):
    """
    Geocodes an address, returning a tuple (coords, cleaned address, condience)
    """
    cached_opencage = load_cached_address(addr, 'opencage')
    cached_google = load_cached_address(addr, 'google')
    # Always prefer cached Google result (change if you want to alwasy prefer OpenCage)
    if cached_google:
        print('g', end='', flush=True)
        return cached_google
    if cached_opencage:
        print('o', end='', flush=True)
        return cached_opencage
    # Okay, not in cache
    if '&' in addr or force_google and not cached_opencage:
        # OpenCage cannot deal with addresses with &
        print('G', end='', flush=True)
        results = gmaps.geocode(addr)
        result = results[0]
        fields = (result['geometry']['location']['lat'], result['geometry']['location']['lng']), result['formatted_address'], 'google'
        save_cached_address(addr, fields, 'google')
    else:
        print('O', end='', flush=True)
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
    
