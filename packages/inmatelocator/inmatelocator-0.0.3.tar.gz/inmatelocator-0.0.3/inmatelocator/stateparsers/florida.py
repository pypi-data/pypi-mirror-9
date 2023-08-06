import re
import requests
import lxml.html
import utils
from addresscleaner import format_address

# Load facility data.

# Mapping from things we get from the search API to normalized names from the
# directory.
NORMALIZE_FACILITIES = {
    "suwannee ci annex": "suwannee annex",
    "nwfrc main unit": "northwest florida reception center",
    "jackson work camp": "jackson ci",
    "gulf ci annex": "gulf ci annex",
    "blackwater cf": "blackwater river cf",
    "columbia annex": "columbia correctional institution annex",
    "out of dept custody by court order": None,
}
def normalize_florida_name(name):
    name = utils.normalize_name(name)
    name = re.sub(r'\bci\b', "correctional institution", name)
    return NORMALIZE_FACILITIES.get(name, name)

facility_lookup = utils.make_facility_lookup("florida", normalize_florida_name)

def search(**kwargs):
    base = "http://www.dc.state.fl.us/ActiveInmates/search.asp"
    search = "http://www.dc.state.fl.us/ActiveInmates/List.asp?DataAction=Filter"
    res = requests.get(base)
    root = lxml.html.fromstring(res.text)
    sessionId = root.xpath("//input[@name='SessionID']/@value")[0]

    res = requests.post(search, {
            "SessionID": sessionId,
            "lastname": kwargs.get('last_name', ''),
            "firstname": kwargs.get('first_name', ''),
            "dcnumber": kwargs.get('number', ''), 
            "searchaliases": "on",
            "race": "ALL",
            "sex": "ALL",
            "eyecolor": "ALL",
            "haircolor": "ALL",
            "fromheightfeet": "",
            "fromheightinches": "",
            "toheightfeet": "",
            "toheightinches": "",
            "fromweight": "",
            "toweight": "",
            "fromage": "",
            "toage": "",
            "offensecategory": "ALL",
            "commitmentcounty": "ALL",
            "facility2": "ALL",
            "items": "20"
        })

    root = lxml.html.fromstring(res.text)
    rows = root.xpath('//table[@class="dcCSStableLight"]//tr')
    results = []
    errors = []
    for row in rows:
        tds = row.xpath('./td')
        if len(tds) != 8:
            continue
        data = {
            "name": "".join(tds[1].xpath('.//text()')).strip(),
            "url": "".join(tds[1].xpath('.//a/@href')).strip(),
            "photo": "".join(tds[0].xpath('.//img/@src')).strip(),
            "dc_number": "".join(tds[2].xpath('.//text()')).strip(),
            "race": "".join(tds[3].xpath('.//text()')).strip(),
            "sex": "".join(tds[4].xpath('.//text()')).strip(),
            "release_date": "".join(tds[5].xpath('.//text()')).strip(),
            "current_facility": "".join(tds[6].xpath('.//text()')).strip(),
            "birth_date": "".join(tds[7].xpath('.//text()')).strip(),
        }
        if data['url']:
            data['url'] = "http://www.dc.state.fl.us/ActiveInmates/" + data['url']
        if data['photo']:
            data['photo'] = "http://www.dc.state.fl.us" + data['photo']
        if data['name']:
            results.append(data)
        else:
            pass
        facility = facility_lookup(data['current_facility'])
        if facility:
            address_parts = {}
            address_parts.update(facility)
            address_parts['name'] = u" ".join((data['name'], data['dc_number']))
            data['address'] = format_address(address_parts)
        else:
            data['address'] = "FACILITY NOT FOUND: {}".format(data['current_facility'])

    return {'state': 'Florida', 'results': results, 'errors': list(errors), 'url': base}
