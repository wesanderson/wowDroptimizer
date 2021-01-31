# Overview
Will parse a Google Sheet's WoW raiders and run them simultaneously against [Droptimizer](https://www.raidbots.com/simbot/droptimizer), scrub the resultant boss kill priorities
and upload these results to the same sheet. This should aid raid leaders in determining what raiders are in most need of a given boss fight.

# Introduction
This single python script leverages a [Google Service Account](https://cloud.google.com/iam/docs/service-accounts) which has **Editor** access to a Google Sheet and runs the 
Droptimizer parses in a local [Selenium Service](https://selenium-python.readthedocs.io/)

# Setup
1. Clone repo
2. Install [Python](https://www.python.org/downloads/)
3. Install [Selenium](https://selenium-python.readthedocs.io/installation.html)
4. Install [gspread](https://gspread.readthedocs.io/en/latest/)
5. Follow [this guide](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html) to create a Google Service Account and 
generate client credentials. Rename the credentials file `client_secret.json` and ensure it's in the same dir as the cloned repo
6. Grant the new Google Service Accout Editor access to the desired Google Sheet

# How to run
Navigate to this cloned repo via a command terminal and run `py droptimer.py`

# Configuration
* Modify `googleDocName` to point to a different Google Sheet name if desired. Ensure the Google Service Account has Editor access to the specified Google Sheet.
* Modify `prioritiesTab` to point to the desired sheet
* The target sheet must have all raiders under the `A column` and named exactly as they'll appear in Droptimizer. The first row shouldn't contain a raider name. This is a header row.
* The target sheet currently hard-code assumes the bosses are listed out in clear order of operation
* To avoid rate limiting issues from Droptimizer (when starting a sim) and from Google Sheets (when updating the parse results), two 10-second waits have been injected 
in between starting a new toon sim and uploading batches of priority results. These constants can be tweaked as desired.
