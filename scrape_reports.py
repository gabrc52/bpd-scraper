import pdfquery
import pandas as pd
import os
from glob import glob
from dotenv import load_dotenv, find_dotenv
from opencage.geocoder import OpenCageGeocode
load_dotenv()
KEY = os.getenv('OPENCAGE')
geocoder = OpenCageGeocode(key)

def gc(address):
    if len(address) == 0: 
        return None, None
    address = address.strip()
    address = address + ", Boston, MA"
    result = geocoder.geocode(address, countrycode="us")
    if result and len(result):
        print(f"Geocoding {address}.")
        lat = result[0]['geometry']['lat']
        lng = result[0]['geometry']['lng']
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
    occurence_times = []
    report_times = []
    complaints = []
    locations = []
    natures = []
    lat = []
    lng = []
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
        lat.append(gc(loc)[0])
        lng.append(gc(loc)[1])
    df = pd.DataFrame(list(zip(officers, occurrence_times, report_times, complaints, locations, natures, lat, lng)), 
                       columns =['officer', 'occ_time', 'rep_time', 'complaint_no', 'location', 'nature', 'lat', 'lng'])
    return(df)

file_list = glob(os.path.join('./data/pdfs/','*.pdf'))
df = scrape_pdf(file_list)
df.to_csv('./outputs/police_journal.csv', index_label='id')
