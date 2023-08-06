import re
from django.conf import settings

from gmsdk.utils import get_auth_token, _input_credentials
from gmsdk.app_settings import CONFIG
from django.core.exceptions import ImproperlyConfigured

token = ""


def validate_settings():
    """
    Description:
        Validator for validating settings
    """
    if HOST not in CONFIG['host']:
        raise AttributeError

    if not AUTH_TOKEN:
        token_input = raw_input(
            "Token Not Found. Press 'y' to login and generate token.\n")
        if token_input == 'y':
            token = _input_credentials(HOST)
            print(
                "Enter the token generated in settings"
                " GODAM_AUTH_TOKEN = %s and try again." % token)
            exit()
        else:
            raise AttributeError

try:
    AUTH_TOKEN = getattr(settings, "GODAM_AUTH_TOKEN")
    HOST = getattr(settings, "GODAM_HOST")
    validate_settings()
except AttributeError, e:
    print "\nApp gmsdk is not configured properly. Try Again."
    print(
        "Enter the following appropriate details in the settings"
        " file to continue :\n GODAM_HOST_TOKEN =  ('godam.delhivery.com'"
        " Prod Envitonment or 'stg-godam.delhivery.com' Test Environment)"
        "\n GODAM_AUTH_TOKEN =  (Enter token)")
    exit()

from gmsdk.api import GMSDK
