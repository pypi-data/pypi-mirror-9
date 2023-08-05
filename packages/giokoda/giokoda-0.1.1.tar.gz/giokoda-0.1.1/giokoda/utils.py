import sys
import csv
from pprint import pprint
from geopy import geocoders, get_geocoder_for_service
from . import settings

GEOCODERS = settings.GEOCODERS
DEFAULT_GEOCODER = settings.DEFAULT_GEOCODER


def geocode_csv(infile, **kwargs):
    """
    Geocode entities from a provided input csv file and write results to an
    output csv file.
    
    Return a dictionary containing error, success and total count of geocoded
    rows.

    **Example:**

    Basic usage::

        >>> from giokoda.utils import geocode_csv
        >>> geocode_csv('input.csv')

    This will will try to goecode the `'input.csv'` file and write output to
    `'input.csv-geocoded.csv'`.

    **Parameters:**

    `infile` *(filepath/str)*: path to a csv file to geocode

    `*kwargs`: Optional and arbitary keyword arguments
      `outfile` (filepath/str): path to file to write output csv

      `service` *(str)*: default: `'nominatim'`. Name of a geocoding service to
      use. This can be a name of any geocoding service accepted by geopy.

      `query_column` *(str)*: default: `'name'`. Name of a column containg text
      to geocode.

      `query_columns` *(list)*: default: `[]`. A list of a columns
      to be combined in order to produce a text to geocode.

      `service_kwargs` *(dict)*: Optional keyword arguments for initialization
      of geocoding service.

      `delimiter` *(str)*: default: `','`, A one-character string used to
      separate fields in a csv file.

      `quotechar` *(str)*: default: `'"'`, A one-character string used to
      quote fields containing special characters in a csv file, such as
      the delimiter or quotechar, or which contain new-line characters.

    **Returns:**
      A dictionary of total success and error count::
      
        {
            'total': 0,
            'success': 0,
            'error': 0
        }
    """
    # Collect parameters
    service = kwargs.get('service', DEFAULT_GEOCODER)
    outfile = kwargs.get('outfile', '%s-geocoded-%s.csv' %(infile, service))
    query_column = kwargs.get('query_column')
    query_columns = kwargs.get('query_columns', [])
    if query_columns and not type(query_columns) == list:
        raise TypeError('A value for `query_columns` must be a list')
    if query_column:
        query_columns.append(query_column)
    elif not query_columns:
        query_columns.append('name')
    service_kwargs = GEOCODERS.get(service, GEOCODERS[DEFAULT_GEOCODER])
    service_kwargs.update(kwargs.get('service_kwargs', {}))
    delimiter = kwargs.get('delimiter', ',')
    quotechar = kwargs.get('quotechar', '"')
    # Get geocoder class
    Geocoder = get_geocoder_for_service(service)
    # Try to catch mandatory arguments, usually these are for authentication.
    # Instanciate geocoder
    if 'api_key' in service_kwargs:
        geocoder = Geocoder(service_kwargs.pop('api_key'), **service_kwargs)
    elif 'username' in service_kwargs and 'password' in service_kwargs:
        geocoder = Geocoder(username=service_kwargs.pop('username'),
                            password=service_kwargs.pop('password'),
                            **service_kwargs)
    elif 'auth_id' in service_kwargs and 'auth_token' in service_kwargs:
        geocoder = Geocoder(auth_id=service_kwargs.pop('auth_id'),
                            auth_token=service_kwargs.pop('auth_token'),
                            **service_kwargs)
    elif 'consumer_key' in service_kwargs and \
            'consumer_secret' in service_kwargs:
        geocoder = Geocoder(
            consumer_key=service_kwargs.pop('consumer_key'),
            consumer_secret=service_kwargs.pop('consumer_secret'),
            **service_kwargs)
    else:
        geocoder = Geocoder(**service_kwargs)
    # Read csv 
    incsv = csv.DictReader(open(infile, 'r'), delimiter=delimiter,
                           quotechar=quotechar)
    # Initialize csv writer
    writer = csv.writer(open(outfile, 'w'), delimiter=delimiter,
                        quotechar=quotechar)
    # Geocode each row
    first_row = True
    successful = 0
    total = 0
    errors = 0
    for row in incsv:
        total += 1
        sorted_row = {'latitude': '', 'longitude': ''}
        for key,value in sorted(row.items()):
            sorted_row[key] = value
        try:
            query = []
            for column in query_columns:
                q = sorted_row.get(column)
                if q:
                    query.append(q)
            query = ', '.join(query)
            if query:
                location = geocoder.geocode(query)
                if location and location.latitude and location.longitude:
                    sorted_row['latitude'] = location.latitude
                    sorted_row['longitude'] = location.longitude
                    successful += 1
        except Exception as e:
            errors += 1
            sys.stdout.write('\n\033[91m%s\033[0m\n' %e)
            pprint(sorted_row)
        if first_row:
            # write header
            writer.writerow(list(sorted_row.keys()))
            first_row = False
        # Write row
        writer.writerow(list(sorted_row.values()))
    return {'total': total, 'success': successful, 'error': errors}
