Name: Ivan <br>
Function: Download logs / records from elasticSearch and then saves it into a JSON file. <br>
Why: I FUCKING HATE MANUAL WORK AND ID RATHER SPEND DAYS MAKING THIS SHIT SCRIPT TO AUTOMATE SOME FUCKASS REQUEST. And also all other scripts I found in the internet is way to hard for me okay.  <br>
 <br>
Last Updated: 29-09-2025  <br>
 <br>
Notes: <br>
- The following is a quick and dirty script to download logs from ElasticSearch.  <br>
- It does this by downloading a batch of logs (currently 10000 per iteration) and appending it into a single line in a JSON file. <br>
- This script will limit the amount of logs into one JSON file with an arbritary number (currently 1 Million) <br>
- 1 mllion logs in a about.. idk 5 mins ? The code is bottlenecked by internet, computational power, and elastic query. <br>
 <br>
TO DO: <br>
- Change authentication to either use encrypted (Base64) or API key. <br>
- Optimize throughput of downloading and append to file to make this faster <br>
    - Ideas:  <br>
        - Reduce PAGE_SIZE <br>
        - Bulk write to file  <br>
        - get better hardware <br>
