#!/usr/bin/python

from shutil import copy

import json
import keys
import locale
import math
import os
import random
import requests
import string
import subprocess
import twitter
import urllib

place = None

PWD = '/home/amarriner/python/zoom'
MAP_MAX = 20
MAP_DIR = '/maps'

# Number of times to attempt retrieval of a city from Google API
MAX_RETRIES                 = 10

# Retrieves static Google map
google_static_map_URL       = 'http://maps.googleapis.com/maps/api/staticmap?'                + \
                                  'maptype=hybrid&'                                           + \
                                  'center=<LAT>,<LNG>&'                                       + \
                                  'size=400x400&'                                             + \
                                  'markers=size:mid|color:blue|<LAT>,<LNG>&'                  + \
                                  '&style=feature:road|visibility:off&'                       + \
                                  'key=' + keys.google_api_key_server + '&'                   + \
                                  'zoom='

# Used to pull random cities 
google_autocomplete_URL     = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?' + \
                                  'sensor=false&'                                             + \
                                  'types=(cities)&'                                           + \
                                  'key=' + keys.google_api_key_server + '&'                   + \
                                  'input='

# Gets specific data on a particular city
google_places_URL           = 'https://maps.googleapis.com/maps/api/place/details/json?'      + \
                                  'sensor=false&'                                             + \
                                  'key=' + keys.google_api_key_server + '&'                   + \
                                  'reference='

# Retrieves random geo information on a place from Google API
def get_place(place):
   retries = 0
   while (place == None and retries < MAX_RETRIES):

      # Get a random string of three characters
      prefix = random.choice(string.letters) + random.choice(string.letters) + random.choice(string.letters)

      # Pull google places via the autocomplete API using the random string
      print 'Retrieving google autocomplete data with prefix ' + prefix + '...'
      request = requests.get(google_autocomplete_URL + prefix)
      places = json.loads(request.content)
      print 'Found ' + str(len(places['predictions'])) + ' places...'

      try:
         # Get data specific to a random place in the autocomplete results 
         print 'Retrieving google places data...'
         request = requests.get(google_places_URL + random.choice(places['predictions'])['reference'])
         result = json.loads(request.content)['result']
      except IndexError:
         retries += 1
      else:
         return result

   return None

# Retrieve Google static maps and assemble them into an animated GIF
def get_maps(lat, lng):
   for i in range(2, MAP_MAX):
      suff = str(i)
      if int(suff) < 10:
         suff = '0' + str(suff)

      print 'Saving ' + suff + ' ...'

      urllib.urlretrieve(google_static_map_URL.replace('<LAT>', lat).replace('<LNG>', lng) + str(i), PWD + MAP_DIR + '/' + suff + '.png')

      if i > 2 and i < (MAP_MAX - 1):
         copy(PWD + MAP_DIR + '/' + suff + '.png', PWD + MAP_DIR + '/' + str((MAP_MAX - int(suff)) + MAP_MAX) + '.png')

   subprocess.call(PWD + '/make_animated_gif.shl')

# Attempt place retrieval
place = get_place(place)

if place != None:
   print place['formatted_address'] + ' ' + str(place['geometry']['location']['lat']) + ',' + str(place['geometry']['location']['lng'])

   get_maps(str(place['geometry']['location']['lat']), str(place['geometry']['location']['lng']))
