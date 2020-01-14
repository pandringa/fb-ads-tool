import csv
import argparse
import re

parser = argparse.ArgumentParser(prog='Merge search results')
parser.add_argument('files', nargs="+")
parser.add_argument('-o', '--out')

args = parser.parse_args()
filecount = len(args.files)
infile = csv.DictReader(open(args.files.pop(0)))

rowset = set()

out = csv.DictWriter(open(args.out, 'w'), fieldnames=infile.fieldnames)
out.writeheader()

writecount = 0
count = 0
filecount = 0;
while infile:
  for row in infile:
    count += 1
    filecount += 1
    ad_id = re.search(r"id=(\d+)&", row['ad_snapshot_url']).group()[3:-1]
    if ad_id not in rowset:
      out.writerow(row)
      rowset.add(ad_id)
      writecount += 1
  
  print(f"Parsed {filecount} lines");

  if args.files:
    filename = args.files.pop(0)
    print(f"Opening {filename}...");
    infile = csv.DictReader(open(filename))
    filecount = 0
  else:
    infile = None

print(f"Wrote {writecount} lines (out of {count} total lines in {filecount} files)")