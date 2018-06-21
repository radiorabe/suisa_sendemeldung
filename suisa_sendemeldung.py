#!/usr/bin/env python3
from argparse import ArgumentParser
from csv import writer
from datetime import datetime, date, timedelta
from requests import get

# argument definition
parser = ArgumentParser(description='ACRCloud client for SUISA reporting @ RaBe.')
default_date = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
parser.add_argument('--date',
	help='date in format YYYYMMDD to fetch data for (defaults to yesterday)',
	default=default_date)
parser.add_argument('--output',
	help='file to write to (defaults to <script_name>_<date>.csv)')
parser.add_argument('--stream_id',
	help='the id of the stream at ACRCloud (required)',
	required=True)
parser.add_argument('--access_key',
	help='the access key for ACRCloud (required)',
	required=True)
args = parser.parse_args()

# sanity checks
def print_error(msg):
	print('ERROR: {}\n'.format(msg))
	parser.print_help()
	quit(1)
if not len(args.date) == 8 or not args.date.isdigit():
	print_error('wrong format on date')
#if not args.stream_id.isdigit():
#	print_error('wrong format on stream_id')
if not len(args.access_key) == 32:
	print_error('wrong format on access_key')

stream_id=args.stream_id
url = 'https://api.acrcloud.com/v1/monitor-streams/{}/results'.format(stream_id)
date = args.date

url_params = dict(
	access_key=args.access_key,
	date=date 
)
csv_headers = [
	'Sendedatum',
	'Sendezeit',
	'Sendedauer',
	'Titel',
	'Autoren',
	'Interpreten',
	'ISRC',
	'Label'
]

# fetch the data from the api and check status code
response = get(url=url, params=url_params)
if not response.status_code == 200:
	print('got bad response from server')
	print('status_code: {}'.format(response.status_code))
	print(response.text)
	quit(1)

data = response.json()
# write results to filename_date.csv
if args.output:
	filename = args.output
else:
	filename = __file__.replace('.py','_{}.csv').format(default_date)
with open(filename, 'w', newline='') as csvfile:
	# excel compatibility (https://superuser.com/questions/606272/how-to-get-excel-to-interpret-the-comma-as-a-default-delimiter-in-csv-files/686415#686415)
	csvfile.write('sep=,\n')

	csv_writer = writer(csvfile, dialect='excel')
	csv_writer.writerow(csv_headers)

	for entry in data:
		metadata = entry.get('metadata')
		# import timestamp from metadata (comes in format "yyyy-mm-dd HH:MM:SS")
		timestamp = datetime.strptime(metadata.get('timestamp_utc'), '%Y-%m-%d %H:%M:%S')
		# format date, time and duration according to requirements from SUISA
		date = timestamp.strftime('%d/%m/%y')
		time = timestamp.strftime('%H:%M:%S')
		duration = timedelta(seconds=metadata.get('played_duration'))
		index = 0
		'''
		for music in metadata.get('music'):
			title = music.get('title')
			# artists are separated by comma
			authors = ', '.join([artist.get('name') for artist in music.get('artists')]) # TODO
			performers = ', '.join([artist.get('name') for artist in music.get('artists')])
			isrc = music.get('external_ids').get('isrc') if len(music.get('external_ids')) > 0 else ""
			label = music.get('label')
			score = music.get('score')

			# write to the csv file
			csv_writer.writerow([date, time, duration, title, authors, performers, isrc, label])
		'''
		music = metadata.get('music')[0]
		title = music.get('title')
		# artists are separated by comma
		authors = ', '.join([artist.get('name') for artist in music.get('artists')]) # TODO
		performers = ', '.join([artist.get('name') for artist in music.get('artists')])
		isrc = music.get('external_ids').get('isrc') if len(music.get('external_ids')) > 0 else ""
		label = music.get('label')
		score = music.get('score')

		# write to the csv file
		csv_writer.writerow([date, time, duration, title, authors, performers, isrc, label])
