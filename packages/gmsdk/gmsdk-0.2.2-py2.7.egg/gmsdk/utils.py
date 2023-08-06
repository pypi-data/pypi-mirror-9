import requests
import urllib
from django.conf import settings
from gmsdk.app_settings import CONFIG


def get_auth_token(HOST, username=None, password=None):
    """
    hits the api and retrieves the token from
    username and password and stroe it in TOKEN
    """
    payload = {'username': username, 'password': password}
    payload = urllib.urlencode(payload)
    header = {
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json"}
    URI = "/api-token-auth/"
    try:
        r = requests.post('http://'+HOST+URI, data=payload, headers=header)
        r.raise_for_status()
    except:
        return {'message': r.content}
    else:
        return r.json()['token']


def _input_credentials(HOST):
    """
    takes in the username and password and calls get_auth_token
    """
    print "Enter credentials to generate token:"
    _username = raw_input("Username: ")
    _password = raw_input("Password: ")
    return get_auth_token(HOST, _username, _password)
