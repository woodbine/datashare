# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup

#### FUNCTIONS 1.2

import requests    #  import requests to validate url

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


def validateURL(url):
    try:
        r = urllib2.urlopen(url)
        count = 1
        while r.getcode() == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = urllib2.urlopen(url)
        sourceFilename = r.headers.get('Content-Disposition')
        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.getcode() == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
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

entity_id = "datashare"
urls = ["http://data.peterborough.gov.uk/api/commercial-activities/transparency-code-payments-over-500",
        "http://data.bracknell-forest.gov.uk/api/finance/payments-over-500", "http://data.wolverhampton.gov.uk/api/finance",
        "http://data.hounslow.gov.uk/api/finance-and-assets/council-spending-over-500",
        "http://datashare.blackburn.gov.uk/api/expenditure-exceeding-500"]
errors = 0
data = []
url="http://example.com"

#### READ HTML 1.0

html = urllib2.urlopen(url)
soup = BeautifulSoup(html, 'lxml')


#### SCRAPE DATA

for url in urls:
    if 'peterborough.gov.uk' in url:
        entity_id = "E0501_PCC_gov"
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html, 'lxml')
        restdataset = soup.select('restdataset')
        for restdata in restdataset:
            link = restdata.select_one('friendlyurl').text.replace('/XML', '/csv')
            title = restdata.select_one('title').text.split()
            csvMth = title[-2][:3]
            csvYr = title[-1]
            csvMth = convert_mth_strings(csvMth.upper())
            data.append([csvYr, csvMth, link])
    if 'bracknell-forest.gov.uk' in url:
        entity_id = "E0301_BFBC_gov"
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html, 'lxml')
        restdataset = soup.select('restdataset')
        for restdata in restdataset:
            link = restdata.select_one('friendlyurl').text.replace('/XML', '/csv')
            title = restdata.select_one('title').text
            csvMth = title.split()[-2][:3]
            csvYr = title.split()[-1]
            if "to" in title:
                if 'January to March' in title:
                    csvMth = 'Q1'
                if 'April to June' in title:
                    csvMth = 'Q2'
                if 'July to September' in title:
                    csvMth = 'Q3'
                if 'October to December' in title:
                    csvMth = 'Q4'
                else:
                    csvMth = 'Q0'
            if 'September' in csvYr:
                csvYr = '2015'
            csvMth = convert_mth_strings(csvMth.upper())
            data.append([csvYr, csvMth, link])
    if 'hounslow.gov.uk' in url:
        entity_id = 'E5042_HLBC_gov'
        html = urllib2.urlopen(url)
        soup = BeautifulSoup(html, 'lxml')
        restdataset = soup.select('restdataset')
        for restdata in restdataset:
            link = restdata.select_one('friendlyurl').text.replace('/XML', '/csv')
            title = restdata.select_one('title').text.split()
            csvMth = title[-2][:3]
            csvYr = title[-1]
            if '20' not in csvYr and '20' in csvMth:
                csvYr = title[-2]
                csvMth = 'Y1'
            if u'£50' in csvMth:
                csvMth='May'
            if 'October November 2015' in restdata.select_one('title').text:
                csvMth='Q0'
            if 'September 2010 to March 2011' in restdata.select_one('title').text:
                csvMth = 'Q0'
            if '20' not in csvYr:
                csvYr = '20'+csvYr
            csvMth = convert_mth_strings(csvMth.upper())
            data.append([csvYr, csvMth, link])
    if 'blackburn.gov.uk' in url:
        entity_id = 'E2301_BWDBC_gov'
        proxy = urllib2.ProxyHandler({'http': 'http://176.126.245.23:3128'})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        html = urllib2.urlopen(url)
        # headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 OPR/42.0.2393.94',
        #            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        # proxy = {'http':'http://176.126.245.23:3128'}
        # page = requests.get(url, proxies=proxy, headers=headers)
        soup = BeautifulSoup(html, 'lxml')
        restdataset = soup.select('restschema')
        for restdata in restdataset:
            friendlyurl = restdata.select_one('friendlyurl')
            title = restdata.select_one('title').text
            path_link = friendlyurl.text
            html = urllib2.urlopen(url+'/'+path_link)
            # html = requests.get(url+'/'+path_link, proxies=proxy)
            soup = BeautifulSoup(html, 'lxml')
            # soup = BeautifulSoup(html, 'lxml')
            restdataset = soup.select('restdataset')
            for restdata in restdataset:
                link = restdata.select_one('friendlyurl').text.replace('/XML', '/csv')
                title = restdata.select_one('title').text
                csvYr = title[:4]
                csvMth = 'Y1'
                csvMth = convert_mth_strings(csvMth.upper())
                data.append([csvYr, csvMth, link])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['f'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename

    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF
