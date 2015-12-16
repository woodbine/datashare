# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup

#### FUNCTIONS 1.2
import requests      # import requests to validate filetype

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url, requestdata):

    try:
        r = requests.post(url, data= requestdata, allow_redirects=True, timeout=20)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = requests.post(url, data= requestdata, allow_redirects=True, timeout=20)
        sourceFilename = r.headers.get('Content-Disposition')
        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')[:4]
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.status_code == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx', '.zip']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False

def validate(filename, file_url, requestdata):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url, requestdata)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string

#### VARIABLES 1.0

entity_id = "E5022_WCC_gov"
url = "http://www.spotlightonspend.org.uk/259/City+of+Westminster+Council/Downloads"
user_agent = {'User-agent': 'Mozilla/5.0'}
errors = 0
data = []


#### READ HTML 1.0

html = requests.get(url, headers=user_agent)
soup = BeautifulSoup(html.text, 'lxml')

#### SCRAPE DATA

blocks = soup.find_all('td', 'treeMonthlyFiles_1')
for block in blocks:
    csvfile = block.find('a')['href'].split('_')[-1].split('.')[0]
    url_csv = block.find('a')['href']
    if 'document' not in csvfile:
        csv_data = url_csv.split("javascript:fnRequestFile('")[-1].split("');")[0]
        requestdata = {'treeMonthlyFiles_ExpandState': 'cnnnnnnnnncnnnnnnnnnnnnennnnnnnnnnnncnnn', 'treeMonthlyFiles_SelectedNode':'', '__EVENTTARGET':'', '__EVENTARGUMENT':'', 'treeMonthlyFiles_PopulateLog':'', 'treeContractFiles_ExpandState':'n', 'treeContractFiles_SelectedNode': '', 'treeContractFiles_PopulateLog':'', '__VIEWSTATE':'/wEPDwUIMzUyNzY2NjkPZBYCZg9kFgICAw9kFggCAQ8PFgIeC05hdmlnYXRlVXJsBS4vMzE3L0xvbmRvbitCb3JvdWdoK29mK0hhbW1lcnNtaXRoK2FuZCtGdWxoYW0vZGQCBQ8WAh4EVGV4dAUoTG9uZG9uIEJvcm91Z2ggb2YgSGFtbWVyc21pdGggYW5kIEZ1bGhhbWQCCw9kFgwCBw8WAh8BBfsJPHA+c3BvdGxpZ2h0b25zcGVuZCBpcyBhbiBpbm5vdmF0aXZlIG9ubGluZSBwbGF0Zm9ybSB0aGF0IHNlZWtzIHRvIGRlbGl2ZXIgbWVhbmluZ2Z1bCB2aXNpYmlsaXR5IG9mIHB1YmxpYyBzZWN0b3Igc3BlbmRpbmcgb24gZ29vZHMgJmFtcDsgc2VydmljZXMuIFRvIHRoYXQgZW5kLCBzaWduaWZpY2FudCBlZmZvcnQgaXMgcmVxdWlyZWQgdG8gaW1wcm92ZSB0aGUgcmF3IGZpbmFuY2lhbCBkYXRhIHN1Y2ggdGhhdCBpdCBpcyBhY2Nlc3NpYmxlLCByZWxldmFudCBhbmQgb2YgdmFsdWUgdG8gdGhlIGdlbmVyYWwgcHVibGljLiBUaGUgd29yayB0byBlZmZlY3QgdGhlIGRhdGEgaW1wcm92ZW1lbnQgaXMgdW5kZXJ0YWtlbiBieSBTcGlrZXMgQ2F2ZWxsIOKAkyBhIHByaXZhdGUgc2VjdG9yIG9yZ2FuaXphdGlvbiB0aGF0IHRyYW5zZm9ybXMgYW5kIGFuYWx5emVzIHNwZW5kIGFuZCByZWxhdGVkIGRhdGEgZm9yIG1vcmUgdGhhbiAxLDAwMCBwdWJsaWMgc2VjdG9yIGJvZGllcyB3b3JsZHdpZGUgdG8gaGVscCB0aGVtIHNhdmUgbW9uZXksIGFkZHJlc3MgaW1wb3J0YW50IHBvbGljeSByZWxhdGVkIHF1ZXN0aW9ucyBhbmQsIGFzIGEgYmktcHJvZHVjdCBvZiB0aG9zZSBlZmZvcnRzLCBmYWNpbGl0YXRlIHRoZSBkZWxpdmVyeSBvZiB0cmFuc3BhcmVuY3kuPC9wPjxwPlRoZSBmdW5jdGlvbmFsaXR5IG9uIHRoaXMgYW5kIHJlbGF0ZWQgcGFnZXMgZW5hYmxlcyB0aGUgZG93bmxvYWQgb2YgdGhlIHRyYW5zYWN0aW9ucyBhYm92ZSAmIzM2OzUwMCBpbiB2YWx1ZSBiZWZvcmUgYW55IGNsZWFuc2luZywgZW5yaWNobWVudCwgYWdncmVnYXRpb24gb3Igb3RoZXIgZGF0YSBpbXByb3ZlbWVudCBoYXMgYmVlbiBtYWRlIGJ5IFNwaWtlcyBDYXZlbGwgb3RoZXIgdGhhbjs8L3A+PHVsPjxsaT50aGUgaWRlbnRpZmljYXRpb24gYW5kIHJlZGFjdGlvbiBvZiBwYXltZW50cyBtYWRlIHRvIGluZGl2aWR1YWxzLDwvbGk+PGxpPnN0YW5kYXJkaXphdGlvbiBvZiB0aGUgZmlsZSBmb3JtYXQgKGluY2x1ZGluZyBjb2x1bW4gaGVhZGluZ3MgYW5kIHBvc2l0aW9ucykuPC9saT48L3VsPjxwPlRoZSBjb3B5cmlnaHQgaW4gdGhlIHJhdyBmaW5hbmNpYWwgZGF0YSBpcyBvd25lZCBieSBMb25kb24gQm9yb3VnaCBvZiBIYW1tZXJzbWl0aCBhbmQgRnVsaGFtICh0aGUgJnF1b3Q7RGF0YSBQcm92aWRlciZxdW90Oykgd2hvIGhhdmUgZWxlY3RlZCB0byBtYWtlIHRoZSByYXcgZmluYW5jaWFsIGRhdGEgZnJlZWx5LXJldXNhYmxlIGJ5IHRoZSBnZW5lcmFsIHB1YmxpYy48L3A+ZAINDw8WAh8ABQ4vRG93bmxvYWRzLzMxN2RkAg8PFgIfAQXVAUFueSBxdWVzdGlvbnMgeW91IG1heSBoYXZlIHdpdGggcmVnYXJkcyB0byB0aGUgZGF0YSBwcm92aWRlZCBpbiB0aGlzIGRvd25sb2FkIHNlY3Rpb24sIHRoZW4gcGxlYXNlIGNvbnRhY3QgdGhlIGRhdGEgb3duZXIgPGEgaHJlZj0iLzMxNy9Mb25kb24rQm9yb3VnaCtvZitIYW1tZXJzbWl0aCthbmQrRnVsaGFtL0J1eWluZy9LZXlGYWN0c1Blb3BsZSI+ZGlyZWN0bHk8L2E+LmQCFQ8PFgIfAAU8LzMxNy9Mb25kb24rQm9yb3VnaCtvZitIYW1tZXJzbWl0aCthbmQrRnVsaGFtL0J1eWluZy9TdW1tYXJ5ZGQCJQ8PFgIfAAU3LzMxNy9Mb25kb24rQm9yb3VnaCtvZitIYW1tZXJzbWl0aCthbmQrRnVsaGFtL0Fib3V0RGF0YWRkAicPFgIeB1Zpc2libGVnFgICAg8PFgIfAAVJLzMxNy9Mb25kb24rQm9yb3VnaCtvZitIYW1tZXJzbWl0aCthbmQrRnVsaGFtL0Rvd25sb2Fkcy9BZGRpdGlvbmFsRmlndXJlc2RkAhEPFgIfAQVEJmNvcHk7IDIwMTUgPHN0cm9uZz5zcG90bGlnaHRvbnNwZW5kPC9zdHJvbmc+LiAgQWxsIHJpZ2h0cyByZXNlcnZlZC5kGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYCBSJjdGwwMCRTaXRlQ29udGVudCR0cmVlTW9udGhseUZpbGVzBSNjdGwwMCRTaXRlQ29udGVudCR0cmVlQ29udHJhY3RGaWxlcxkrEAAPqVT7IECMHZ6cx4o/kxkH', '__VIEWSTATEGENERATOR':'BBE16BD4', '__EVENTVALIDATION': '/wEWAgKK1s6vBQKW25yCD0ccXeeFBIjlsuo9L0SDHw3pghYi', 'ctl00$SiteContent$requestedFileName':'{}'.format(csv_data)}
        csvYr = csvfile[-4:]
        csvMth = csvfile[:3]
        csvMth = convert_mth_strings(csvMth.upper())
        data.append([csvYr, csvMth, url, requestdata])

#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url, requestdata = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url, requestdata)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['f'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF
