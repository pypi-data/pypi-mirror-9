import json
import time
import requests

def search(**kwargs):
    url = "http://www.bop.gov/PublicInfo/execute/inmateloc"

    searches = []
    if kwargs.get('number'):
        for numtype in ("IRN", "DCDC", "FBI", "INS"):
            searches.append({"inmateNum": kwargs['number'], "inmateNumType": numtype})
    else:
        searches.append({"nameFirst": kwargs.get("first_name"), "nameLast": kwargs.get("last_name")})

    results = []
    errors = []

    for i,search in enumerate(searches):
        search['todo'] = 'query'
        search['output'] = 'json'
        res = requests.get(url, params=search)
        if res.status_code != 200:
            errors.append(res.content)
            break

        data = json.loads(res.content)
        for result in data['InmateLocator']:
            result['name'] = u"{} {}".format(result['nameFirst'], result['nameLast'])
            if 'faclURL' in result:
                result['facility URL'] = "http://www.bop.gov{}".format(result['faclURL'])
            results.append(result)

        # Throttle. be nice.
        if i < len(searches) - 1:
            time.sleep(0.5)

    return {"state": "Federal", "results": results, "errors": errors, "url": url}

