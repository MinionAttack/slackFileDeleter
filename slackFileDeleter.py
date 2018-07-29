from urllib.parse import urlencode
from urllib.request import urlopen
import time
import json
import codecs
import datetime
from collections import OrderedDict

reader = codecs.getreader("utf-8")

# Obtain here: https://api.slack.com/custom-integrations/legacy-tokens
token = ''

# Params for file listing. More info here: https://api.slack.com/methods/files.list

# Delete files older than this:
days = 0
ts_to = int(time.time()) - days * 24 * 60 * 60

# How many? (Maximum is 1000, otherwise it defaults to 100)
count = 1000

# Size in MB, if your files are less than 1 MB, set to 0
size = 0

#What size to check: greater, smaller
delimiter = 'greater'

# Types?
types = 'all'
# types = 'spaces,snippets,images,gdocs,zips,pdfs'
# types = 'zips'


def list_files():
    params = {
        'token': token,
        'ts_to': ts_to,
        'count': count,
        'types': types
    }
    uri = 'https://slack.com/api/files.list'
    response = reader(urlopen(uri + '?' + urlencode(params)))
    return json.load(response)['files']


def filter_by_size(files, mb, greater_or_smaller):
    if greater_or_smaller == 'greater':
        return [file for file in files if (file['size'] / 1000000) > mb]
    elif greater_or_smaller == 'smaller':
        return [file for file in files if (file['size'] / 1000000) < mb]
    else:
        return None


def info(file):
    order = ['Title', 'Name', 'Created', 'Size', 'Filetype',
             'Comment', 'Permalink', 'Download', 'User', 'Channels']
    info = {
        'Title': file['title'],
        'Name': file['name'],
        'Created': datetime.datetime.utcfromtimestamp(file['created']).strftime('%B %d, %Y %H:%M:%S'),
        'Size': str(file['size'] / 1000000) + ' MB',
        'Filetype': file['filetype'],
        'Comment': file['initial_comment'] if 'initial_comment' in file else '',
        'Permalink': file['permalink'],
        'Download': file['url_private'],
        'User': file['user'],
        'Channels': file['channels']
    }
    return OrderedDict((key, info[key]) for key in order)


def file_ids(files):
    return [f['id'] for f in files]


def delete_files(file_ids):
    num_files = len(file_ids)
    for index, file_id in enumerate(file_ids):
        params = {
            'token': token,
            'file': file_id
        }
        uri = 'https://slack.com/api/files.delete'
        response = reader(urlopen(uri + '?' + urlencode(params)))
        print((index + 1, "of", num_files, "-",
               file_id, json.load(response)['ok']))

files = list_files()
files_by_size = filter_by_size(files, size, delimiter)
print(len(files_by_size))
[info(file) for file in files_by_size]
file_ids = file_ids(files_by_size)
#delete_files(file_ids) # Commented out, so you don't accidentally run this.
