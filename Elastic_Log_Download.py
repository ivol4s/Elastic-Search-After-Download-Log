'''
Name: LogDownloaded_BSI 
Function: Download logs / records from elasticSearch and then saves it into a JSON file.
Why: I FUCKING HATE MANUAL WORK AND ID RATHER SPEND DAYS MAKING THIS SHIT SCRIPT TO AUTOMATE SOME FUCKASS REQUEST. And also all other scripts I found in the internet is way to hard for me okay. 

Last Updated: 29-09-2025 

Notes:
- The following is a quick and dirty script to download logs from ElasticSearch. 
- It does this by downloading a batch of logs (currently 10000 per iteration) and appending it into a single line in a JSON file.
- This script will limit the amount of logs into one JSON file with an arbritary number (currently 1 Million)
- 1 mllion logs in a about.. idk 5 mins ? The code is bottlenecked by internet, computational power, and elastic query.

TO DO:
- Change authentication to either use encrypted (Base64) or API key.
- Optimize throughput of downloading and append to file to make this faster
    - Ideas: 
        - Reduce PAGE_SIZE
        - Bulk write to file 
        - get better hardware
'''

import requests
import json
import os
import time

#CHANGE THIS
ES_BASE_URL = "https://11112222333aaaabbbbcccc.marsianPeninsula.azure.elastic-cloud.com:443"
INDEX_NAME = "anal-analyzer"
USERNAME = "<elastic username here>"
PASSWORD = "<elastic password here>"
OUTPUT_FILE = "formatted_output.json"
BASE_OUTPUT_FILE = "formatted_output"

PAGE_SIZE = 10000

session = requests.Session()
session.auth = (USERNAME, PASSWORD)
headers = {"Content-Type": "application/json"}


# Main Idea, use the "search_after" function in Elastic to scroll through all logs in a given time.
# (https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results)

# Open PIT, (https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-open-point-in-time)
# If a refresh occurs between these requests, the order of results may change, causing inconsistent results across pages. 
# To prevent this, create a point in time (PIT) to preserve the current index state over searches.
# TL:DR Elastic saves the last record and makes sure that the next iteration will continue from there. (I love you elastic team)
pit_response = session.post(
    f"{ES_BASE_URL}/{INDEX_NAME}/_pit?keep_alive=10m", headers=headers)
pit_response.raise_for_status()
pit_id = pit_response.json()['id']
print(f"PIT opened with id: {pit_id}")


# Query Body - Change as required.
# Can be tested from Elastic Console. 
# Note:
    # If you are unsure where to find the elastic base URL or "ES_BASE_URL". Go to the Dev Tools console in elastic and run a test GET query.
    # If the query works then click the triple dots on that command to "Copy as URL", it will give all you need. 
    # Example, the query
        # "POST /forti-analyzer/_pit?keep_alive=10m"
        # Will give the following curl query (automatically)
        # curl -X POST -H "Authorization: ApiKey $ELASTIC_API_KEY" "https://123123asdasd.antartica.azure.elastic-cloud.com:443/forti-analyzer/_pit?keep_alive=10m"
        # Copy over the URL and put it as the base URL. 
query_body = {
    "size": PAGE_SIZE,
    "pit": {
        "id": pit_id,
        "keep_alive": "10m"
    },
    "_source": [
        "@timestamp",
        "user",
        "source.ip",
        "source.port",
        "destination.ip",
        "destinatio.port",
        "usingpolicy",
        "utmaction",
        "utmevent",
        "url",
        "srcname",
        "service",
        "_id",
        "remotename"
      ],
    "query": {
        "range": {
            "@timestamp": {
                # NOTE: the time is using UTC GMT+0 (I think), so to find the before after easily just find the time in the URL after searching.
                "gte": "2025-07-31T17:00:00.000Z",
                "lte": "2025-08-31T17:00:00.000Z"
            }
        }
    },
    "sort": [
         {
          "@timestamp": {
            "order": "asc", 
            "format": "strict_date_optional_time", 
            "numeric_type" : "date" 
          }
        }
    ],
    "track_total_hits": False
}

# Append to file on each iteration.
def append_to_file(filename, data, isClose):
    if not os.path.isfile(filename):
        with open(filename, 'w') as f:

            # Note: You can just skip this and dump the returned JSON to file immediately.
            # I did this to reduce the size a bit, modify as required. 
            sources = [entry['_source'] for entry in data]
            f.write("[")
            # Remove all new line and put the All returned json into one giant line.
            json.dump(sources, f, separators=(',', ':'))
    else:
        with open(filename, 'a') as f:
            # DO NOT USE THIS, im keeping it to remind me never to use this again.
            # Commented code will open the file to write on it. Doesn't matter until a file reaches multi GB.
            # existing = json.load(f)                   # BAD
            # existing.extend(data)                     # DO
            # f.seek(0)                                 # NOT
            # json.dump(existing, f, indent=2)          # USE

            f.write(",")
            # Take only the required data 
            sources = [entry['_source'] for entry in data]
            # fuck it we ball put it all in one line
            json.dump(sources,f, separators=(',', ':'))

            if(isClose):
                # Close with square bracket to make it into json again
                f.write("]")
                f.close()

all_hits_count = 0
search_after = None
file_index = 0
isClosed = False

while True:
    if search_after:
        # Append the PIT search after ID to continue downloading correctly.
        query_body["search_after"] = search_after
    else:
        # First run of the program to get next PIT ID
        query_body.pop("search_after", None)

    response = session.post(f"{ES_BASE_URL}/_search", json=query_body, headers=headers)
    response.raise_for_status()
    data = response.json()

    # Update PIT ID to keep it alive
    pit_id = data.get('pit_id', pit_id)
    query_body['pit']['id'] = pit_id

    hits = data['hits']['hits']
    if not hits:
        print("No more results to fetch.")
        break
    
    # I KNOW THIS IS STUPID OK, BUT I HAD TO JUST MAKE IT WORK
    # Every Million hit, make a new file so windows / python doesnt freak out. 
    if all_hits_count % 1000000 == 0 and all_hits_count != 0: 
        isClosed = True

    # Analytic, uncomment if you want to see how long an Apend to file takes
    start = time.time()

    append_to_file(OUTPUT_FILE, hits, isClosed)

    # I KNOW THIS IS STUPID OK, BUT I HAD TO JUST MAKE IT WORK
    if all_hits_count % 1000000 == 0 and all_hits_count != 0: 
        file_index += 1
        OUTPUT_FILE = f"{BASE_OUTPUT_FILE}_{file_index}.json"

    isClosed = False

    all_hits_count += len(hits)
    print(f"Fetched {len(hits)} hits, total so far: {all_hits_count}")

    end = time.time()
    print(end - start)

    # Find PIT for next query
    search_after = hits[-1]['sort']

# Close PIT
close_resp = session.delete(f"{ES_BASE_URL}/_pit", json={"id": pit_id}, headers=headers)
if close_resp.status_code == 200:
    print("PIT closed successfully.")
else:
    print(f"Failed to close PIT: {close_resp.text}")

print(f"Finished! Total documents saved: {all_hits_count}")
