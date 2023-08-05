#!/usr/bin/env python

import argparse
import json
from giokoda.utils import geocode_csv


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Full path to csv file to geocode',
                        type=str)
    parser.add_argument('-o', '--output', help='Full path to output file',
                        type=str)
    parser.add_argument('-s', '--service', help='Geocoding service name',
                        type=str)
    parser.add_argument(
        '-c', '--column', nargs='*', type=str, 
        help='Names for columns containing text content to geocode. \
        Multiple column names should be separated by white space.')
    parser.add_argument(
        '-p', '--params', type=str,
        help='Keyword arguments for geocoding service initialization \
        presented as json object')
    parser.add_argument(
        '-d', '--delimiter', type=str,
        help='A one-character string used to separate fields in a csv file')
    parser.add_argument(
        '-q', '--quotechar', type=str,
        help= "A one-character string used to\
        quote fields containing special characters in a csv file, such as\
        the delimiter or quotechar, or which contain new-line characters")
    args = parser.parse_args()
    kwargs = {}
    if args.output: kwargs['outfile'] = args.output
    if args.service: kwargs['service'] = args.service
    if args.column: kwargs['query_columns'] = args.column
    if args.delimiter: kwargs['delimiter'] = args.delimiter
    if args.quotechar: kwargs['quotechar'] = args.quotechar
    if args.params:
        try:
            params = json.loads(args.params)
            if type(params) == dict:
                kwargs['service_kwargs'] = params
            else:
                parser.error('Invalid --params (-p) value')
        except:
            parser.error('Invalid --params (-p) value')
    results = geocode_csv(args.input, **kwargs)
    parser.exit(status=0, message='\n%s\n' %str(results)) 
