import datetime
from scrape_rss import get_filename

# Parse the list and see if there are any duplicates
# Make symbolic links with much ETU names

all_urls = set()

with open('files.tsv', 'r') as f:
    lines = f.read().split('\n')
    for line in lines:
        if line:
            line = line.split('\t')
            title = line[0]
            date: str = line[1]
            urls = line[2:]
            for url in urls:
                if url in all_urls:
                    print('Duplicate URL found', url)
                all_urls.add(url)

            # if len(line[2:]) > 1:
            #     print('Found more than one file')
            #     print(title, date, urls)
            