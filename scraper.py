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
new_url = 'https://www.westminster.gov.uk/spending-procurement-and-data-transparency'
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
        requestdata = {'treeMonthlyFiles_ExpandState': 'cnnnnnnnnncnnnnnnnnnnnnennnnnnnnnnnncnnn', 'treeMonthlyFiles_SelectedNode':'', '__EVENTTARGET':'', '__EVENTARGUMENT':'', 'treeMonthlyFiles_PopulateLog':'', 'treeContractFiles_ExpandState':'n', 'treeContractFiles_SelectedNode': '', 'treeContractFiles_PopulateLog':'', '__VIEWSTATE':'/wEPDwUIMzUyNzY2NjkPZBYCZg9kFgICAw9kFggCAQ8PFgIeC05hdmlnYXRlVXJsBSEvMjU5L0NpdHkrb2YrV2VzdG1pbnN0ZXIrQ291bmNpbC9kZAIFDxYCHgRUZXh0BRtDaXR5IG9mIFdlc3RtaW5zdGVyIENvdW5jaWxkAgsPZBYMAgcPFgIfAQXuCTxwPnNwb3RsaWdodG9uc3BlbmQgaXMgYW4gaW5ub3ZhdGl2ZSBvbmxpbmUgcGxhdGZvcm0gdGhhdCBzZWVrcyB0byBkZWxpdmVyIG1lYW5pbmdmdWwgdmlzaWJpbGl0eSBvZiBwdWJsaWMgc2VjdG9yIHNwZW5kaW5nIG9uIGdvb2RzICZhbXA7IHNlcnZpY2VzLiBUbyB0aGF0IGVuZCwgc2lnbmlmaWNhbnQgZWZmb3J0IGlzIHJlcXVpcmVkIHRvIGltcHJvdmUgdGhlIHJhdyBmaW5hbmNpYWwgZGF0YSBzdWNoIHRoYXQgaXQgaXMgYWNjZXNzaWJsZSwgcmVsZXZhbnQgYW5kIG9mIHZhbHVlIHRvIHRoZSBnZW5lcmFsIHB1YmxpYy4gVGhlIHdvcmsgdG8gZWZmZWN0IHRoZSBkYXRhIGltcHJvdmVtZW50IGlzIHVuZGVydGFrZW4gYnkgU3Bpa2VzIENhdmVsbCDigJMgYSBwcml2YXRlIHNlY3RvciBvcmdhbml6YXRpb24gdGhhdCB0cmFuc2Zvcm1zIGFuZCBhbmFseXplcyBzcGVuZCBhbmQgcmVsYXRlZCBkYXRhIGZvciBtb3JlIHRoYW4gMSwwMDAgcHVibGljIHNlY3RvciBib2RpZXMgd29ybGR3aWRlIHRvIGhlbHAgdGhlbSBzYXZlIG1vbmV5LCBhZGRyZXNzIGltcG9ydGFudCBwb2xpY3kgcmVsYXRlZCBxdWVzdGlvbnMgYW5kLCBhcyBhIGJpLXByb2R1Y3Qgb2YgdGhvc2UgZWZmb3J0cywgZmFjaWxpdGF0ZSB0aGUgZGVsaXZlcnkgb2YgdHJhbnNwYXJlbmN5LjwvcD48cD5UaGUgZnVuY3Rpb25hbGl0eSBvbiB0aGlzIGFuZCByZWxhdGVkIHBhZ2VzIGVuYWJsZXMgdGhlIGRvd25sb2FkIG9mIHRoZSB0cmFuc2FjdGlvbnMgYWJvdmUgJiMzNjs1MDAgaW4gdmFsdWUgYmVmb3JlIGFueSBjbGVhbnNpbmcsIGVucmljaG1lbnQsIGFnZ3JlZ2F0aW9uIG9yIG90aGVyIGRhdGEgaW1wcm92ZW1lbnQgaGFzIGJlZW4gbWFkZSBieSBTcGlrZXMgQ2F2ZWxsIG90aGVyIHRoYW47PC9wPjx1bD48bGk+dGhlIGlkZW50aWZpY2F0aW9uIGFuZCByZWRhY3Rpb24gb2YgcGF5bWVudHMgbWFkZSB0byBpbmRpdmlkdWFscyw8L2xpPjxsaT5zdGFuZGFyZGl6YXRpb24gb2YgdGhlIGZpbGUgZm9ybWF0IChpbmNsdWRpbmcgY29sdW1uIGhlYWRpbmdzIGFuZCBwb3NpdGlvbnMpLjwvbGk+PC91bD48cD5UaGUgY29weXJpZ2h0IGluIHRoZSByYXcgZmluYW5jaWFsIGRhdGEgaXMgb3duZWQgYnkgQ2l0eSBvZiBXZXN0bWluc3RlciBDb3VuY2lsICh0aGUgJnF1b3Q7RGF0YSBQcm92aWRlciZxdW90Oykgd2hvIGhhdmUgZWxlY3RlZCB0byBtYWtlIHRoZSByYXcgZmluYW5jaWFsIGRhdGEgZnJlZWx5LXJldXNhYmxlIGJ5IHRoZSBnZW5lcmFsIHB1YmxpYy48L3A+ZAINDw8WAh8ABQ4vRG93bmxvYWRzLzI1OWRkAg8PFgIfAQXIAUFueSBxdWVzdGlvbnMgeW91IG1heSBoYXZlIHdpdGggcmVnYXJkcyB0byB0aGUgZGF0YSBwcm92aWRlZCBpbiB0aGlzIGRvd25sb2FkIHNlY3Rpb24sIHRoZW4gcGxlYXNlIGNvbnRhY3QgdGhlIGRhdGEgb3duZXIgPGEgaHJlZj0iLzI1OS9DaXR5K29mK1dlc3RtaW5zdGVyK0NvdW5jaWwvQnV5aW5nL0tleUZhY3RzUGVvcGxlIj5kaXJlY3RseTwvYT4uZAIVDw8WAh8ABS8vMjU5L0NpdHkrb2YrV2VzdG1pbnN0ZXIrQ291bmNpbC9CdXlpbmcvU3VtbWFyeWRkAiUPDxYCHwAFKi8yNTkvQ2l0eStvZitXZXN0bWluc3RlcitDb3VuY2lsL0Fib3V0RGF0YWRkAicPFgIeB1Zpc2libGVnFgICAg8PFgIfAAU8LzI1OS9DaXR5K29mK1dlc3RtaW5zdGVyK0NvdW5jaWwvRG93bmxvYWRzL0FkZGl0aW9uYWxGaWd1cmVzZGQCEQ8WAh8BBUQmY29weTsgMjAxNiA8c3Ryb25nPnNwb3RsaWdodG9uc3BlbmQ8L3N0cm9uZz4uICBBbGwgcmlnaHRzIHJlc2VydmVkLmQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFImN0bDAwJFNpdGVDb250ZW50JHRyZWVNb250aGx5RmlsZXN5YmuQAajZGUBXvEdCJuOecO56nQ==', '__VIEWSTATEGENERATOR':'BBE16BD4', '__EVENTVALIDATION': '/wEdAAKD7C9MHe7QXeJuZkH2vS93Mq7+XPodPdKcQ/RQ+ItsENLS5F+w/BFhfwX8DhbkeithGqXN', 'ctl00$SiteContent$requestedFileName':'{}'.format(csv_data)}
        csvYr = csvfile[-4:]
        csvMth = csvfile[:3]
        csvMth = convert_mth_strings(csvMth.upper())
        data.append([csvYr, csvMth, url, requestdata])
new_html = urllib2.urlopen(new_url)
archive_soup = BeautifulSoup(new_html, 'lxml')
rows = archive_soup.find_all('a')
for row in rows:
    link = row['href']
    if 'Q' in row.text and ('xpenditure' in link or 'contract' in link and '2015' not in link):
        title = row.text.strip()
        csvYr = title[:4]
        csvMth = title.split(',')[1].strip()[:2]
        requestdata = None
        data.append([csvYr, csvMth, link, requestdata])

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
