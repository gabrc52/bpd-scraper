import os
import csv
from scrape_reports import load_cached_address, save_cached_address
from count_unique_addresses import officer_addresses
from pprint import pprint

# TODO don't forget no_record=1

combinations = set()
abbreviations_or_partial = set()
exceptions = set()

usps_types = ('ALY', 'ANX', 'ARC', 'AVE', 'YU', 'BCH', 'BND', 'BLF', 'BTM', 'BLVD', 'BR', 'BRG', 'BRK', 'BG', 'BYP', 'CP', 'CYN', 'CPE', 'CSWY', 'CTR', 'CIR', 'CLFS', 'CLB', 'COR', 'CORS', 'CRSE', 'CT', 'CTS', 'CV', 'CRK', 'CRES', 'XING', 'DL', 'DM', 'DV', 'DR', 'EST', 'EXPY', 'EXT', 'FALL', 'FLS', 'FRY', 'FLD', 'FLDS', 'FLT', 'FOR', 'FRST', 'FGR', 'FORK', 'FRKS', 'FT', 'FWY', 'GDNS', 'GTWY', 'GLN', 'GN', 'GRV', 'HBR', 'HVN', 'HTS', 'HWY', 'HL', 'HLS', 'HOLW', 'INLT', 'IS', 'ISS', 'ISLE', 'JCT', 'CY', 'KNLS', 'LK', 'LKS', 'LNDG', 'LN', 'LGT', 'LF', 'LCKS', 'LDG', 'LOOP', 'MALL', 'MNR', 'MDWS', 'ML', 'MLS', 'MSN', 'MT', 'MTN', 'NCK', 'ORCH', 'OVAL', 'PARK', 'PKY', 'PASS', 'PATH', 'PIKE', 'PNES', 'PL', 'PLN', 'PLNS', 'PLZ', 'PT', 'PRT', 'PR', 'RADL', 'RNCH', 'RPDS', 'RST', 'RDG', 'RIV', 'RD', 'ROW', 'RUN', 'SHL', 'SHLS', 'SHR', 'SHRS', 'SPG', 'SPGS', 'SPUR', 'SQ', 'STA', 'STRA', 'STRM', 'ST', 'SMT', 'TER', 'TRCE', 'TRAK', 'TRL', 'TRLR', 'TUNL', 'TPKE', 'UN', 'VLY', 'VIA', 'VW', 'VLG', 'VL', 'VIS', 'WALK', 'WAY', 'WLS')

usps_types = {t[0] + t[1:].lower() for t in usps_types}

types_of_street = usps_types | {
    'Dr', 'St', 'Street', 'Av', 'Ave', 'Avenue', 'Rd', 'Road', 'Pkwy', 'Blvd', 'Way', 'Pl', 'Sq', 'Ln', 'Ter', 'Place', 'Ct', 'Plz', 'Plaza'
}

# I don't mean for this to work in the general case,
# just for the addresses I happen to have
# Sorry for the hacky code.

def clean_address(address: str):
    if 'United States' in address:
        address = address.replace(' Ma ', ' MA ')
        address = address.replace(' United States', '')
        splat = address.split(' ')
        if len(splat) < 4:
            # address saying just "Boston, MA 02120" was certainly a mistake
            return address
        else:
            if splat[-4] in types_of_street:
                splat[-4] += ','
                address = ' '.join(splat)
            elif splat[-5] in types_of_street:
                splat[-5] += ','
                address = ' '.join(splat)
            elif 'South Boston' in address:
                address = address.replace(' South Boston', ', South Boston')
            elif 'Boston' in address:
                address = address.replace(' Boston', ', Boston')
            elif 'Jamaica Plain' in address:
                address = address.replace(' Jamaica Plain', ', Jamaica Plain')
            elif 'Roxbury' in address:
                address = address.replace(' Roxbury', ', Roxbury')
            elif 'Brighton' in address:
                address = address.replace(' Brighton', ', Brighton')
            elif 'Charlestown' in address:
                address = address.replace(' Charlestown', ', Charlestown')
            elif 'Concord' in address:
                address = address.replace(' Concord', ', Concord')
            elif 'Braintree' in address:
                address = address.replace(' Braintree', ', Braintree')
            else:
                abbreviations_or_partial.add(splat[-4])
                combinations.add(tuple(splat[-5:-2]))
                exceptions.add(address)
    else:
        address += ', Boston, MA'
    return address.strip()

if __name__ == '__main__':
    with open('addresses.tsv', 'w') as f:
        print('Unclean address', 'Cleaned address', sep='\t', file=f)
        for address in officer_addresses:
            print(address, clean_address(address), sep='\t', file=f)
        
    assert not exceptions