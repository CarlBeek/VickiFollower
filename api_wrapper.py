from bittrex import Bittrex
import twitter
import json

class Wrapper(object):
    """
    This is a wrapper for both the Bittrex and Twitter API.
    It's purpose it to handle API  errors as well as making the trading code distinct
    from the API in the intrests of portability
    """

    def __init__(self):

    def instantiate_apis(self, secrets_file_location):
        """
        Sets up apis for bittrex and twitter
        :param secrets_file_location: location of API secrets json file
        :type secrets_file_location: str
        """
        with open(secrets_file_location) as secrets_file:
            