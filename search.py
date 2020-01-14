import requests
import csv
import json
import argparse
import sys
import os
import dateparser
from urllib.parse import urlencode

parser = argparse.ArgumentParser(prog='FB Ad Archive API')
parser.add_argument('-p', '--page')
parser.add_argument('-d', '--date-limit')
parser.add_argument('-t', '--token')
parser.add_argument('-b', '--byline')
parser.add_argument('query')

args = parser.parse_args()

if not args.query:
    sys.exit("A query term is required")

api_token = args.token or os.environ['FB_API_TOKEN']
if not api_token:
  sys.exit("A Facebook API token must be set via --token or the FB_API_TOKEN environment variable")

request_args = {
  'ad_reached_countries': "['US']", 
  'access_token': api_token,
  'ad_type': 'POLITICAL_AND_ISSUE_ADS',
  'ad_active_status': 'ALL',
  'impression_condition': 'HAS_IMPRESSIONS_LIFETIME',
  'search_terms': f"'{args.query}'",
  'limit': 500,
  'fields': 'ad_creation_time,ad_creative_body,ad_creative_link_caption,ad_creative_link_description,ad_creative_link_title,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,currency,demographic_distribution,funding_entity,impressions,page_id,page_name,region_distribution,spend'
}

if args.page:
  request_args['search_page_ids'] = args.page

if args.byline:
  request_args['byline'] = args.byline

if args.date_limit:
  print(args.date_limit)
  datelimit = dateparser.parse(f"{args.date_limit} +0000")
else:
  datelimit = dateparser.parse("1970-01-01 00:00:00 +0000") # Arbitrarily early date for when there's no limit

outfields = [
  'ad_creation_time',
  'ad_creative_body',
  'ad_creative_link_caption',
  'ad_creative_link_description',
  'ad_creative_link_title',
  'ad_delivery_start_time',
  'ad_delivery_stop_time',
  'ad_snapshot_url',
  'currency',
  'top_demographic',
  'top_demographic_pct',
  'funding_entity',
  'impressions.lower_bound',
  'impressions.upper_bound',
  'page_id',
  'page_name',
  'top_region',
  'top_region_pct',
  'spend.lower_bound',
  'spend.upper_bound'
]

out = csv.DictWriter(open(f"searches/{ args.query.replace(' ', '+') }_{ args.page or 'all' }.csv", 'w'), fieldnames=outfields)
out.writeheader()

result = { 'paging': { 'next': 'https://graph.facebook.com/v4.0/ads_archive?'+urlencode(request_args) } }
count = 0
while result.get('paging') and result.get('paging').get('next'):
  count += 1
  print(f"Loading page {count} of results...")
  result = requests.get(result['paging']['next']).json()
  if not 'data' in result:
    print("Error in result")
    print(result)
    break

  backup = open(f"backups/{ args.query.replace(' ', '+') }_{ args.page or 'all' }_{ count }.json","w") 
  backup.write(json.dumps(result))
  backup.close()

  for ad in result['data']:

    if datelimit > dateparser.parse(ad['ad_delivery_start_time']):
      print(f"Halting query at date {ad['ad_delivery_start_time']}...")
      result = {}
      break

    obj = {}
    tops = {}
    for k in outfields:
      if ad.get(k):
        obj[k] = ad.get(k)
      elif '.' in k:
        k2 = k.split('.')
        if ad.get(k2[0]):
          obj[ k ] = ad.get(k2[0]).get(k2[1])
        else:
          obj[ k ] = ''
      elif 'top_' in k:
        pass # we'll do this manually
      else:
        obj[k] = ''
    
    for d in ['region', 'demographic']:
      if ad.get(d+'_distribution'):
        top = max(ad.get(d+'_distribution'), key=lambda k: float(k['percentage']))
        if top:
          obj['top_'+d+'_pct'] = top['percentage']
          if d == 'demographic':
            obj['top_'+d] = top['age'] + ' ' + top['gender']
          else:
            obj['top_'+d] = top[d]
        else:
          obj['top_'+d] = ''
          obj['top_'+d+'_pct'] = ''
      else:
        obj['top_'+d] = ''
        obj['top_'+d+'_pct'] = ''

    out.writerow(obj)
