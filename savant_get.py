import datetime
import urllib.parse
import urllib.request
import io
import csv
import itertools
import pathlib
import os
import argparse
import logging


def split_date_span(first_date, last_date, days_in_subspan):
    """Generate pairs of dates from `first_date` through `last_date` that are
    each at most `days_in_subspan` apart (inclusive).
    """
    while first_date <= last_date:
        second_date = first_date + datetime.timedelta(days_in_subspan - 1)
        # Don't let the subspan exceed the last date
        if second_date > last_date:
            second_date = last_date
        yield (first_date, second_date)
        first_date = second_date + datetime.timedelta(1)


def date_span_intersection(date_span_1, date_span_2):
    """Return a tuple of dates representing the overlap between `date_span_1`
    and `date_span_2`.  If the date spans do not overlap, return `None`.
    """
    intersection_first_date = max(date_span_1[0], date_span_2[0])
    intersection_second_date = min(date_span_1[1], date_span_2[1])
    if intersection_first_date > intersection_second_date:
        # Date spans don't overlap
        return None
    else:
        return (intersection_first_date, intersection_second_date)

SEASON_STARTS_AND_ENDS = (
    ((2015, 3, 3),  (2015, 11, 1)),
    ((2016, 3, 1),  (2016, 11, 2)),
    ((2017, 2, 24), (2017, 11, 1)),
    ((2018, 2, 23), (2018, 10, 28)),
    ((2019, 2, 21), (2019, 9, 29)),
)


def week_long_date_spans_in_season(first_date, last_date):
    """Generate 7-day-long date spans between two dates that fall in season.
    """
    for season_start, season_end in SEASON_STARTS_AND_ENDS:
        intersection = date_span_intersection(
            (first_date, last_date),
            (datetime.date(*season_start), datetime.date(*season_end)))
        if intersection is not None:
            yield from split_date_span(intersection[0], intersection[1], 7)


def request_date_span_from_baseball_savant(game_date_gt, game_date_lt):
    """Make one request to Baseball Savant for all games starting on
    the first date through the second date.
    """
    # Assume dates span at most two different seasons
    parameter_string = urllib.parse.urlencode({
        'all': 'true',
        'batter_stands': '',
        'game_date_gt': game_date_gt.strftime('%Y-%m-%d'),
        'game_date_lt': game_date_lt.strftime('%Y-%m-%d'),
        'group_by': 'name',
        'hfAB': '',
        'hfBBL': '',
        'hfBBT': '',
        'hfC': '',
        'hfFlag': '',
        'hfGT': 'R|PO|S|',
        'hfInn': '',
        'hfNewZones': '',
        'hfOuts': '',
        'hfPR': '',
        'hfPT': '',
        'hfRO': '',
        'hfSA': '',
        # Assume dates never span more than one season
        'hfSea': game_date_gt.strftime('%Y|'),
        'hfSit': '',
        'hfZ': '',
        'home_road': '',
        'metric_1': '',
        'min_abs': '0',
        'min_pitches': '0',
        'min_results': '0',
        'opponent': '',
        'pitcher_throws': '',
        'player_event_sort': 'h_launch_speed',
        'player_type': 'batter',
        'position': '',
        'sort_col': 'pitches',
        'sort_order': 'desc',
        'stadium': '',
        'team': '',
        'type': 'details',
    })
    url = 'https://baseballsavant.mlb.com/statcast_search/csv?{}'.format(
        parameter_string)
    logging.debug('Getting url: {}'.format(url))
    response = urllib.request.urlopen(url)
    logging.debug('Response status code: {}'.format(response.status))
    return response


def gen_rows_from_response(response):
    """Read, parse, and yield each row from the socket.  Discard the header
    and replace "null" with `None`.
    """
    encoding = response.headers.get_content_charset('utf_8')
    with io.TextIOWrapper(response, encoding=encoding) as file_handle:
        reader = csv.reader(file_handle)
        header = next(reader)  # Discard the header
        for row in reader:
            # Replace the word "null" with `None`
            yield [None if column == "null" else column for column in row]


def write_rows_to_files(rows, directory_path):
    for game_date, rows in itertools.groupby(rows, lambda row: row[1]):
        file_name = 'baseball-savant-{}.csv'.format(game_date)
        file_path = directory_path / file_name
        print(str(file_path))
        with file_path.open('w') as file_handle:
            writer = csv.writer(file_handle)
            writer.writerows(rows)

class NoFilesInDataDirectoryError(Exception): pass


def get_last_game_date_downloaded(directory_path):
    sorted_paths = sorted(directory_path.glob('baseball-savant-*.csv'))
    try:
        last_path_by_game_date = sorted_paths[-1]
    except IndexError:
        raise NoFilesInDataDirectoryError(str(directory_path))
    else:
        last_game_datetime = datetime.datetime.strptime(
            last_path_by_game_date.name, 'baseball-savant-%Y-%m-%d.csv')
        return last_game_datetime.date()


def get_data_between_dates(first_game_date, last_game_date, directory_path):
    for game_date_gt, game_date_lt in week_long_date_spans_in_season(
            first_game_date, last_game_date):
        response = request_date_span_from_baseball_savant(
            game_date_gt, game_date_lt)
        rows = gen_rows_from_response(response)
        write_rows_to_files(rows, directory_path)

argument_parser = argparse.ArgumentParser(
    description='Get data from Baseball Savant')
argument_parser.add_argument(
    'first_game_date', nargs='?', help='get data from this date')
argument_parser.add_argument(
    'last_game_date', nargs='?', help='get data through this date')
argument_parser.add_argument(
    '-v', '--verbose', action='store_true', help='display verbose logging')


def main():
    args = argument_parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    # If environment variable is not set, use blank (current directory)
    directory_path = pathlib.Path(
        os.environ.get('BASEBALL_SAVANT_DATA_DIR', ''))
    logging.debug('Directory of files: {}'.format(str(directory_path)))
    # Determine first and last game dates to get
    last_game_date = datetime.date.today() - datetime.timedelta(days=1)
    if args.first_game_date is None:
        try:
            last_game_date_downloaded = get_last_game_date_downloaded(
                directory_path)
        except NoFilesInDataDirectoryError:
            first_game_date = datetime.date(*SEASON_STARTS_AND_ENDS[0][0])
            logging.debug(
                'Starting on the first day of the first season: {}'.format(
                    first_game_date))
        else:
            first_game_date = last_game_date_downloaded + datetime.timedelta(1)
            logging.debug(
                'Starting on the day after the last day downloaded: {}'.format(
                    first_game_date))
        logging.debug('Ending on yesterday: {}'.format(last_game_date))
    else:
        first_game_date = datetime.datetime.strptime(
            args.first_game_date, '%Y-%m-%d').date()
        logging.debug(
            'Starting on the day passed as the first argument: {}'.format(
                first_game_date))
        if args.last_game_date is not None:
            last_game_date = datetime.datetime.strptime(
                args.last_game_date, '%Y-%m-%d').date()
            logging.debug(
                'Ending on the day passed as the second argument: {}'.format(
                    last_game_date))
        else:
            logging.debug('Ending on yesterday: {}'.format(last_game_date))
    get_data_between_dates(first_game_date, last_game_date, directory_path)

if __name__ == '__main__':
    main()
