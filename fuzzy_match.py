import pandas as pd
import geopandas as gpd
import d6tjoin.top1
from os import path

# Remove commas and reverse last-first.
bpd = pd.read_csv('./data/employee_earnings.csv')
bpd.columns = map(str.lower, bpd.columns)
bpd = bpd[bpd.department_name.eq('Boston Police Department')]
bpd.loc[:,'name'] = bpd.name.str.split(pat = ',').apply(lambda x: ' '.join(x[::-1]))
bpd.loc[:,'name'] = bpd.name.str.split(pat = r' [a-zA-Z]\. ').apply(lambda x: ' '.join(x))
bpd.loc[:,'name'] = bpd.name.str.split(pat = r' [a-zA-Z] ').apply(lambda x: ' '.join(x))
bpd.loc[:,'postal'] = bpd.postal.astype(str).apply(lambda x: '0'+ x)
bpd = bpd.applymap(lambda x: x.strip() if isinstance(x, str) else x)
bpd.replace(r'^-$', value='', regex=True, inplace=True)
bpd.replace(r',', value='', regex=True, inplace=True)

cols = bpd.columns.drop(['name', 'department_name', 'title', 'postal'])
bpd[cols] = bpd[cols].apply(pd.to_numeric, errors='coerce').fillna(0)

incidents = pd.read_csv('./outputs/police_journal.csv', index_col='id')
incidents = incidents[incidents.officer.notnull()]
incidents = incidents[incidents.location.notnull()]
incidents['badge'] = incidents.officer.str.split(pat = ' ').apply(lambda x: x[0])
incidents['name'] = incidents.officer.str.split(pat = ' ').apply(lambda x: ' '.join(x[1:]))
incidents.loc[:,'occ_time'] = incidents.occ_time.apply(pd.to_datetime)
incidents.loc[:,'rep_time'] = incidents.rep_time.apply(pd.to_datetime)
incidents = gpd.GeoDataFrame(incidents, geometry=gpd.points_from_xy(incidents.lng, incidents.lat))
incidents.crs = 4326
incidents = incidents.to_crs(epsg=2249)

# Read Boston Police districts
districts_path = './data/districts.geojson'
if path.exists(districts_path):
    districts = gpd.read_file(districts_path).to_crs(epsg=2249)
else:
    districts = gpd.read_file('http://bostonopendata-boston.opendata.arcgis.com/datasets/9a3a8c427add450eaf45a470245680fc_5.geojson?outSR={%22latestWkid%22:2249,%22wkid%22:102686}', index_col='OBJECTID')
    districts = districts.to_crs(epsg=2249)
    districts = districts[['geometry', 'ID']].rename(columns={'ID': 'district'})
    districts.to_crs(epsg=4326).to_file(districts_path, driver='GeoJSON')

# Read neighborhoods
neighs_path = './data/neighs.geojson'
if path.exists(neighs_path):
    neighs = gpd.read_file(neighs_path).to_crs(epsg=2249)
else:
    neighs = gpd.read_file('http://bostonopendata-boston.opendata.arcgis.com/datasets/3525b0ee6e6b427f9aab5d0a1d0a1a28_0.geojson?outSR={%22latestWkid%22:2249,%22wkid%22:102686}')
    neighs = neighs.to_crs(epsg=2249)
    neighs = neighs[['geometry', 'Name']].rename(columns={'Name': 'neigh'})
    neighs.to_crs(epsg=4326).to_file(neighs_path, driver='GeoJSON')

incidents.sindex
incidents = gpd.sjoin(incidents, districts, how='inner', op='within')
incidents = incidents.drop('index_right', axis=1)
incidents = gpd.sjoin(incidents, neighs, how='inner', op='within')
incidents = incidents.drop('index_right', axis=1)

fuzzy_merge = d6tjoin.top1.MergeTop1(incidents, bpd, fuzzy_left_on=['name'], fuzzy_right_on=['name'], top_limit=[3]).merge()
incidents = fuzzy_merge['merged']

incidents.to_crs(epsg=4326).to_file('./outputs/incidents.geojson', driver='GeoJSON')
