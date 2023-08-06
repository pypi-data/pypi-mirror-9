import re
import requests
import lxml.html

def search(**kwargs):
    url = "http://offender.tdcj.state.tx.us/OffenderSearch/search.action"
    res = requests.post(url, {
            "page": "index",
            "lastName": kwargs.get('last_name', ''),
            "firstName": kwargs.get('first_name', ''),
            "sid": kwargs.get('number', ''),
            "gender": "ALL",
            "race": "ALL",
            "btnSearch": "Search",
        })

    root = lxml.html.fromstring(res.text)
    rows = root.xpath('//table[@class="ws"]//tr')
    results = []
    errors = []
    for row in rows:
        data = {
            'name': "".join(row.xpath('./td[1]/a/text()')),
            'url': "http://offender.tdcj.state.tx.us" + "".join(row.xpath('./td[1]/a/@href')),
            'tdcj_number': "".join(row.xpath('./td[2]/text()')),
            'race': "".join(row.xpath('./td[3]/text()')),
            'gender': "".join(row.xpath('./td[4]/text()')),
            'projected_release_date': "".join(row.xpath('./td[5]/text()')),
            'unit_of_assignment': "".join(row.xpath('./td[6]/text()')),
            'date_of_birth': "".join(row.xpath('./td[7]/text()')),
        }
        if data['url']:
            match = re.search("sid=([-0-9a-zA-Z]+)", data['url'])
            if match:
                data['sid_number'] = match.group(1)
        if data['name']:
            results.append(data)
        else:
            pass
            #errors.append(''.join(row.xpath('.//text()')))
    return {'state': 'Texas', 'results': results, 'errors': list(errors), 'url': url}
