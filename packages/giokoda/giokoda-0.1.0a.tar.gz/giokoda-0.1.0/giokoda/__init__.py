"""
A Python utility for geocoding csv writen on top of `geopy`.
"""


from .utils import geocode_csv


def get_version():
    return '0.1.0'

__version__ = get_version()


