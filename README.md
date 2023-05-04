# bpd

Scraping Boston Police Journal pdfs, provided (roughly) daily on https://bpdnews.com/.

Running:

*Note: these instructions are outdated. Because of the large amount of data, there's more intermediate converters/cleaners instead of one monolithic scraper, so these instructions no longer hold. TODO: add the list of all intermediate scripts to run*

1. Save your OpenCage API key in a file called `.env` with contents `OPENCAGE=yourapikeygoeshere`

2. Run `scrape_rss.py` to download the PDF files

3. Run `scrape_reports.py` to parse and geocode the PDF files into ~~a CSV file~~ several CSV fles

4. Run `clean_csvs.py` to clean the addresses into a geocodable format

5. Run `consolidate_csvs.py` to consolidate all CSVs into a single one (`output.csv`)

TODO: geocoding

6. Run `fuzzy_match.py` to join the CSV file `/outputs/police_journal.csv` with the officer and district data
