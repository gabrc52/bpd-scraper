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
import concurrent.futures
from pdfquery.cache import FileCache

def load_cached_address(address):
    addresses = pickle.load(open('addresses.pickle', 'rb'))
    if address in addresses:
        return addresses[address]

def save_cached_address(address, geocoded):
    addresses = pickle.load(open('addresses.pickle', 'rb'))
    addresses[address] = geocoded
    pickle.dump(addresses, open('addresses.pickle', 'wb'))

geocoding_error = False

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
    try:
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
    except BaseException as e:
        geocoding_error = True
        print(e)
        return (None, None)

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

def get_csv_file(path):
    """
    Given the path of a .pdf file, return the path of its corresponding .csv
    """
    filename = path.split('/')[-1][:-3] + 'csv'
    return os.path.join('./outputs/csvs/', filename)


def scrape_pdf(path_list, skip_geocoding=False):
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
        # "The initial call to pdf.load() runs very slowly, because the underlying pdfminer 
        # library has to compare every element on the page to every other element."
        pdf = pdfquery.PDFQuery(path)# , parse_tree_cacher=FileCache("./cache/"))
        # Unfortunately, caching is not very straightforward with concurrency

        pdf.load()
        officers.extend(get_category(pdf, cell_text="Officer", h=20, w=220))
        occurrence_times.extend(get_category(pdf, cell_text="Occurrence Date", h=20, w=136))
        report_times.extend(get_category(pdf, cell_text="Report Date", h=20, w=104))
        complaints.extend(get_category(pdf, cell_text="Complaint #", h=20, w=84))
        # HACKY SOLUTION to get full addresses is to increase the height and then remove the "nature of incident"
        # Since I don't understand how the PDF extraction works, and even the docs get bounding boxes
        # Once I have more time (i.e. UROP), I can read the pdfquery docs with the time they deserve
        current_locations = get_category(pdf, cell_text="Location of", h=40, w=520)
        current_locations = [location.replace("Nature Of Incident", "").strip() for location in current_locations]
        locations.extend(current_locations)
        natures.extend(get_category(pdf, cell_text="Nature of", h=20, w=520))

    columns = [officers, occurrence_times, report_times, complaints, locations, natures]
    fields = ['officer', 'occ_time', 'rep_time', 'complaint_no', 'location', 'nature']
    if not skip_geocoding:
        for loc in locations:
            geocoded = geocode(loc)
            lat.append(geocoded[0])
            lng.append(geocoded[1])
        columns.extend([lat, lng])
        fields.extend(['lat', 'lng'])
    df = pd.DataFrame(list(zip(*columns)), columns=fields)
    # If there is only one path to scrape, assume this came from our attempt to write things separately
    if len(path_list) == 1:
        filename = get_csv_file(path_list[0])
        print('Ended scraping', filename)
        df.to_csv(filename, index_label='id')
    else:
        print(path_list)
    return df


if __name__ == '__main__':
    executor = concurrent.futures.ProcessPoolExecutor()

    # file_list = glob(os.path.join('./pdfs/','*.pdf'))
    file_list = ordered_files
    for file in file_list:
        # If we want to try to do the PDF scraping concurrently, then we need to
        # do the geocoding separately, because we might have bad interleavings when trying
        # to remember what we have geocoded so far

        if os.path.exists(get_csv_file(file)):
            print('Skipping', file, '(already done)')
            continue
        # scrape_pdf([file], skip_geocoding=True)
        executor.submit(scrape_pdf, [file], skip_geocoding=True)

    # df = scrape_pdf(file_list)
    # df.to_csv('./outputs/police_journal.csv', index_label='id')