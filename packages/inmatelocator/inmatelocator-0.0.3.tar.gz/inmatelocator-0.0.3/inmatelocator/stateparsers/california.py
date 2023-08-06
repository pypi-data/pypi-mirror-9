import re
import time
import requests
import lxml.html

def search(**kwargs):
    url = "http://inmatelocator.cdcr.ca.gov/search.aspx"
    
    # Get the session cookie.
    sess = requests.Session()
    res = sess.get(url)
    root = lxml.html.fromstring(res.text)
    data = {
        "__EVENTVALIDATION": "".join(root.xpath('//input[@id="__EVENTVALIDATION"]/@value')),
        '__VIEWSTATE': ''.join(root.xpath('//input[@id="__VIEWSTATE"]/@value')),
        '__EVENTTARGET': "",
        '__EVENTARGUMENT': "",
        'text': ''.join(root.xpath('//textarea[@name="text"]/text()')),
        "ctl00$LocatorPublicPageContent$btnAccept": "Agree",
    }
    time.sleep(1)
    sess.post("http://inmatelocator.cdcr.ca.gov/default.aspx", data)

    # Now do the search
    time.sleep(1)
    res = sess.get(url)
    root = lxml.html.fromstring(res.text)
    query = {
        "ctl00$LocatorPublicPageContent$txtLastName": kwargs.get("last_name", ""),
        "ctl00$LocatorPublicPageContent$txtFirstName": kwargs.get("first_name", ""),
        "ctl00$LocatorPublicPageContent$txtCDCNumber": kwargs.get("number", ""),
        "ctl00$LocatorPublicPageContent$txtMiddleName": "",
        "ctl00$LocatorPublicPageContent$btnSearch": "Search",
        "__LASTFOCUS": "",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__EVENTVALIDATION": ''.join(root.xpath('//input[@id="__EVENTVALIDATION"]/@value')),
        "__VIEWSTATE": ''.join(root.xpath('//input[@id="__VIEWSTATE"]/@value')),

    }
    time.sleep(1)
    res = sess.post(url, query)

    # Now parse the results.
    root = lxml.html.fromstring(res.text)
    rows = root.xpath('//table[@id="ctl00_LocatorPublicPageContent_gvGridView"]//tr')
    results = []
    errors = []
    for row in rows:
        if len(row.xpath('./td')) == 0:
            continue
        data = {
            "name": "".join(row.xpath('(./td)[1]/text()')),
            "cdcr_number": "".join(row.xpath('(./td)[2]/text()')),
            "age": "".join(row.xpath('(./td)[3]/text()')),
            'admission_date': ''.join(row.xpath('(./td)[4]/text()')),
            'current_location': ''.join(row.xpath('(./td)[5]/a/text()')),
            'current_location_url': ''.join(row.xpath('(./td)[5]/a/@href')),
            'map_url': ''.join(row.xpath('(./td)[6]/a/@href')),
        }
        if data['name']:
            results.append(data)
        else:
            text = u''.join(row.xpath('//text()')).strip()
            if "Next Page" in text or "Previous Page" in text or re.search("Page \d+ of \d+", text):
                continue
            else:
                errors.append(text)

    return {'state': 'California', 'results': results, 'errors': errors, 'url': url}
