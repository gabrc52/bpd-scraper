Continuation of <https://github.com/ericrobskyhuntley/bpd-scraper/>

All credit goes to Eric Robsky Huntley!

Running:

1. Save your OpenCage API key in a file called `.env` with contents `OPENCAGE=yourapikeygoeshere`

2. Run `scrape_rss.py` to download the PDF files

3. Run `scrape_reports.py` to parse and geocode the PDF files into a CSV file

4. Run `fuzzy_match.py` to join the CSV file with the officer and district data