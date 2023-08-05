"""Global settings for giokoda module"""

GEOCODERS = {
    'nominatim': {
        'timeout': 60
    }
}

DEFAULT_GEOCODER = 'nominatim'

GEOCODERS['default'] = GEOCODERS[DEFAULT_GEOCODER]
