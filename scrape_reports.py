import pdfquery
import pandas as pd
import os
from glob import glob
from dotenv import load_dotenv, find_dotenv
from opencage.geocoder import OpenCageGeocode
load_dotenv()
KEY = os.getenv('OPENCAGE')
geocoder = OpenCageGeocode(KEY)
import pickle
from list_files import ordered_files

def load_cached_address(address):
    addresses = pickle.load(open('addresses.pickle', 'rb'))
    if address in addresses:
        return addresses[address]

def save_cached_address(address, geocoded):
    addresses = pickle.load(open('addresses.pickle', 'rb'))
    addresses[address] = geocoded
    pickle.dump(addresses, open('addresses.pickle', 'wb'))

def geocode(address):
    # First, try to return cached address
    cached_address = load_cached_address(address)
    if cached_address:
        print(f"No need to geocode {address}, we did it before :)")
        return cached_address
    
    if len(address) == 0: 
        return None, None
    address = address.strip()
    address = address + ", Boston, MA"
    result = geocoder.geocode(address, countrycode="us")
    if result and len(result):
        print(f"Geocoding {address}.")
        lat = result[0]['geometry']['lat']
        lng = result[0]['geometry']['lng']
        
        # Save into cache
        save_cached_address(address, (lat, lng))
    else:
        lat = None
        lng = None
    return (lat, lng)

def get_category(pdf, cell_text, h=20, w=220):
    label = pdf.pq(f'LTTextLineHorizontal:contains("{cell_text}")')
    instances = []
    for instance in label:
        p = next(instance.iterancestors('LTPage')).layout.pageid - 1
        l = instance.layout.x0
        b = instance.layout.y0
        if b < 72:
            p = p + 1
            b = 774
        result = pdf.extract([
            ('with_parent', f'LTPage[page_index="{p}"]'),
            ('with_formatter', 'text'),
            ('instance', 'LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (l, b - h, l + w, b))
        ])
        instances.append(result['instance'].title())
    return instances

def scrape_pdf(path_list):
    officers = []
    occurrence_times = []
    report_times = []
    complaints = []
    locations = []
    natures = []
    lat = []
    lng = []
    # TODO: I don't like how it waits to parse all the PDFs and only then it tries geocoding
    # If there is any failure, maybe we want to do it gradually like scrape_rss.py so we can
    # resume after failures, power outages, etc
    # Or maybe do the scraping and geocoding separately. They don't need to be together.
    for path in path_list:
        print(f"Scraping {path}...")
        pdf = pdfquery.PDFQuery(path)
        pdf.load()
        officers.extend(get_category(pdf, cell_text="Officer", h=20, w=220))
        occurrence_times.extend(get_category(pdf, cell_text="Occurrence Date", h=20, w=136))
        report_times.extend(get_category(pdf, cell_text="Report Date", h=20, w=104))
        complaints.extend(get_category(pdf, cell_text="Complaint #", h=20, w=84))
        locations.extend(get_category(pdf, cell_text="Location of", h=20, w=520))
        natures.extend(get_category(pdf, cell_text="Nature of", h=20, w=520))
    for loc in locations:
        geocoded = geocode(loc)
        lat.append(geocoded[0])
        lng.append(geocoded[1])
    df = pd.DataFrame(list(zip(officers, occurrence_times, report_times, complaints, locations, natures, lat, lng)), 
                       columns =['officer', 'occ_time', 'rep_time', 'complaint_no', 'location', 'nature', 'lat', 'lng'])
    return df



# file_list = glob(os.path.join('./pdfs/','*.pdf'))
file_list = ordered_files[:3]
df = scrape_pdf(file_list)
df.to_csv('./outputs/police_journal.csv', index_label='id')