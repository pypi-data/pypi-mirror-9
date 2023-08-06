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
    s.post(url + '/login', params=p).raise_for_status()

    p = params(s.get(url + '/settings?tab=authentication'))
    p.update({'settings[rest_api_enabled]': '1'})
    s.post(url + '/settings/edit?tab=authentication',
           params=p).raise_for_status()

    p = params(s.get(url + '/admin'))
    p.update({'lang': 'en'})
    s.post(url + '/admin/default_configuration', params=p).raise_for_status()

    p = params(s.get(url + '/custom_fields/new?type=IssueCustomField'))
    p.update({
        'custom_field[name]': 'Backport',
        'custom_field[tracker_ids][]': "1",
        'custom_field[visible]': "1",
        'custom_field[field_format]': "string",
        'custom_field[is_filter]': "0",
        'custom_field[is_for_all]': "0",
        'custom_field[is_required]': "0",
        'custom_field[searchable]': "0",
        'type': 'IssueCustomField',
    })
    s.post(url + '/custom_fields', params=p).raise_for_status()

init(*sys.argv[1:])
