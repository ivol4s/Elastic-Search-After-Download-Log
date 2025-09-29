Name: Ivan 
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
