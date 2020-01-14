import csv
import re
import argparse
import dateparser

parser = argparse.ArgumentParser(prog='Aggregates search results by key')
parser.add_argument('file')
parser.add_argument('-k', '--key')
parser.add_argument('-o', '--out')

args = parser.parse_args()
infile = csv.DictReader(open(args.file))

rowset = {}
real_rowset = set()

out = csv.DictWriter(open(args.out, 'w'), fieldnames=[*infile.fieldnames, 'ad_versions_count'])
out.writeheader()

writecount = 0
count = 0
processedcount = 0

for row in infile:
  row_hash = row[args.key]
  real_rowset.add(row_hash)
  if row_hash in rowset:
    rowset[row_hash].append(row)
  else:
    rowset[row_hash] = [row]
    writecount += 1
  count += 1

print(f"Processing {writecount} lines... (out of {count} total lines)")

outrows = []
for group in rowset.values():
  total = sum(map(lambda d: ( int(d['impressions.lower_bound'] or 0) + int(d['impressions.upper_bound'] or 0) ) / 2, group))

  regions = map(lambda d: (d['top_region'], float(d['top_region_pct'] or 0) * ( int(d['impressions.lower_bound'] or 0) + int(d['impressions.upper_bound'] or 0) ) / 2), group)
  regioncounts = {}
  for region in regions:
    if region[0] in regioncounts:
      regioncounts[region[0]] += region[1]
    else:
      regioncounts[region[0]] = region[1]
  
  for (k,v) in regioncounts.items():
    regioncounts[k] = v / total
  top_region = max(regioncounts.items(), key=lambda d: d[1])

  demographics = map(lambda d: (d['top_demographic'], float(d['top_region_pct'] or 0) * ( int(d['impressions.lower_bound'] or 0) + int(d['impressions.upper_bound'] or 0) ) / 2), group)
  democounts = {}
  for demo in demographics:
    if demo[0] in democounts:
      democounts[demo[0]] += demo[1]
    else:
      democounts[demo[0]] = demo[1]
  
  for (k,v) in democounts.items():
    democounts[k] = v / total
  top_demo = max(democounts.items(), key=lambda d: d[1])

  out.writerow({
    'ad_creation_time': min(group, key=lambda d: dateparser.parse(d['ad_creation_time']))['ad_creation_time'],
    'ad_creative_body': group[0]['ad_creative_body'],
    'ad_creative_link_caption': group[0]['ad_creative_link_caption'],
    'ad_creative_link_description': group[0]['ad_creative_link_description'],
    'ad_creative_link_title': group[0]['ad_creative_link_title'],
    'ad_delivery_start_time': min(group, key=lambda d: dateparser.parse(d['ad_delivery_start_time']) if d.get('ad_delivery_start_time') else dateparser.parse('2100-01-01 +0000') )['ad_delivery_start_time'],
    'ad_delivery_stop_time': max(group, key=lambda d: dateparser.parse(d['ad_delivery_stop_time']) if d.get('ad_delivery_stop_time') else dateparser.parse('2000-01-01 +0000') )['ad_delivery_stop_time'],
    'ad_snapshot_url': 'multiple',
    'currency': group[0]['currency'],
    'top_demographic': top_demo[0],
    'top_demographic_pct': top_demo[1],
    'funding_entity': group[0]['funding_entity'],
    'impressions.lower_bound': sum(map(lambda d: float(d['impressions.lower_bound'] or 0), group)),
    'impressions.upper_bound': sum(map(lambda d: float(d['impressions.upper_bound'] or 0), group)),
    'page_id': group[0]['page_id'],
    'page_name': group[0]['page_name'],
    'top_region': top_region[0],
    'top_region_pct': top_region[1],
    'spend.lower_bound': sum(map(lambda d: float(d['spend.lower_bound'] or 0), group)),
    'spend.upper_bound': sum(map(lambda d: float(d['spend.upper_bound'] or 0), group)),
    'ad_versions_count': len(group)
  })
  
  processedcount += 1
  print(f"{processedcount}/{writecount}")

print(f"Wrote {processedcount} of {writecount} lines (out of {count} total lines)")