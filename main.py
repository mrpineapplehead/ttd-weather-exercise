#!/usr/bin/python3
""" Reads tsv file and creates a tsv histogram file containing histogram bins
of forecasted high temperatures of the locations discovered in the input log.

Example:
  ./main.py -inputFile ./input/devops_coding_input_log1.tsv -o out2 -H 10

 Attributes:
    --inputFile, -i: The input file tsv file

    --outputFile, -o: The output file

    --histogramBuckets, -H: Number of histogram buckets

    --configFile, -c: location of the configuration file for this program. default is data/weather.json

    --flushCache: flushes the cache. Optional

    --verbose -v: prints out where forecast is retrieved from. Cache or api

    For more flags, see Readme
"""
import argparse
import sys

from WeatherLogProcessor import WeatherLogProcessor

INPUT_FILE = ''
OUTPUT_FILE = ''
NUMBER_OF_BUCKETS = 0
CONFIG_FILE = ''
VERBOSE = False
FLUSH_CACHE = False


def read_user_options():
    """Reads user flags and sets global variables"""
    global INPUT_FILE
    global OUTPUT_FILE
    global NUMBER_OF_BUCKETS
    global CONFIG_FILE
    global FLUSH_CACHE
    global VERBOSE

    parser = argparse.ArgumentParser(description="The Trade Desk DevOps coding exercise")
    parser.add_argument('--inputFile', '-i',
                        help='The input file',
                        required=True)
    parser.add_argument('--outputFile', '-o',
                        help='The output file',
                        required=True)
    parser.add_argument('--histogramBuckets', '-H',
                        help='number of histogram buckets',
                        type=int,
                        required=True)
    parser.add_argument('--configFile', '-c',
                        help='location of the configuration file',
                        type=str,
                        default="config/weather.json")
    parser.add_argument('--flushCache',
                        help="flush the cache",
                        action='store_true')
    parser.add_argument('--verbose', '-v',
                        help="prints out where values retrieved from",
                        action='store_true')

    inputs = vars(parser.parse_args())
    INPUT_FILE = inputs['inputFile']
    OUTPUT_FILE = inputs['outputFile']
    NUMBER_OF_BUCKETS = inputs['histogramBuckets']
    CONFIG_FILE = inputs['configFile']
    VERBOSE = inputs['verbose']

    if inputs['flushCache']:
        FLUSH_CACHE = True


def main():
    try:
        read_user_options()
        weather_log_processor = WeatherLogProcessor(config_file=CONFIG_FILE,
                                                    flush_cache=FLUSH_CACHE,
                                                    verbose=VERBOSE)

        weather_log_processor.process_tsv(INPUT_FILE)
        weather_log_processor.create_histogram_tsv(number_of_buckets=NUMBER_OF_BUCKETS,
                                                   output_file=OUTPUT_FILE)
        weather_log_processor.print_error_report()

    except Exception as e:
        print('\033[93m' + str(e) + '\033[0m')
    weather_log_processor.close()


if __name__ == "__main__":
    main()
