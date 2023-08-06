def conv(user):
    import requests
    import json
    import xmltodict

    url = 'https://api.github.com/users/' + user
    s = requests.get(url)

    # Converter json para dict
    x = {}
    x['wg'] = json.loads(s.text)
    y = xmltodict.unparse(x, pretty=True)
    return y
