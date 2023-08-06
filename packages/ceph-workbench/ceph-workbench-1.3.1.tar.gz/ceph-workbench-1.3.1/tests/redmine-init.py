import re
import requests
import sys


def params(page):
    (csrf_token,) = re.findall(r'meta content="(.*?)" name="csrf-token"',
                               page.text)
    (csrf_param,) = re.findall(r'meta content="(.*?)" name="csrf-param"',
                               page.text)
    return {csrf_param: csrf_token}


def init(url, user, password):
    s = requests.Session()

    p = params(s.get(url + '/login'))
    p.update({"username": user, "password": password})
    s.post(url + '/login', params=p)

    p = params(s.get(url + '/settings?tab=authentication'))
    p.update({'settings[rest_api_enabled]': '1'})
    s.post(url + '/settings/edit?tab=authentication', params=p)

    p = params(s.get(url + '/admin'))
    p.update({'lang': 'en'})
    s.post(url + '/admin/default_configuration', params=p)

    p = params(s.get(url + '/admin'))
    p.update({'lang': 'en'})
    s.post(url + '/admin/default_configuration', params=p)

init(*sys.argv[1:])
