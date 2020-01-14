# Facebook Ads Archive Searching Tool

### Setup
* Install python3 and [pipenv](https://pipenv.kennethreitz.org/en/latest/).
* Add a new file named `.env` to this folder and add the line: `FB_API_TOKEN=[your token here]`
* Run `pipenv install` to download required dependencies.

### Usage

**Download search results as CSV:**

`pipenv run python3 search.py [search_string]`

This runs a search for the specified term, writing a csv file of results in the searches/ folder.

Other options:
* `-p [page_id]` restrict results to a specific Facebook page. 
* `-b '[byline search]'` search for a string in the "paid for by" tag
* `-d 2019-11-01` only include ads since November 1, 2019.

**Merge search results into one big file:**

`pipenv run python3 merge.py [infile1] [infile2] ... -o [outfile]`

This will de-deuplicate identical rows from the input result files, and write them to one big merged file.

**Aggregate search results based on identical key:**

`pipenv run python3 aggregate.py [result.csv] -k [agg_key] -o [outfile]`

This sums up the result statistics for the given key (similar to a SQL `GROUP BY`), which is particularly useful for summing up all the versions of the same ad (usually based on the `ad_creative_text` key.)
