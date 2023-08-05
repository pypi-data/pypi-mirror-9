import json
import urllib2

# Syncs a MongoDB collection with a list of dictionaries
# 
# Collection should be from PyMongo
# Key should be the field of the dictionaries to key by
def sync(collection, data, key):
    for doc in data:
        collection.find_and_modify(query={key: doc[key]},
            update={'$set': doc},
            upsert=True)

# Syncs a MongoDB collection with a JSON string
#
# Collection should be from PyMongo
# JSON data should be an array of dictionaries
# Key should be the field of the dictionaries to key by
def sync_json(collection, json_string, key):
    sync(collection, json.loads(json_string), key)

# Syncs a MongoDB collection with a JSON file
#
# Collection should be from PyMongo
# JSON data should be an array of dictionaries
# Key should be the field of the dictionaries to key by
def sync_json_file(collection, json_filename, key):
    with open(json_filename) as data_file:    
        data = json.load(data_file)
    sync(collection, data, key)

# Syncs a MongoDB collection with a JSON from a URL
#
# Collection should be from PyMongo
# JSON data should be an array of dictionaries
# Key should be the field of the dictionaries to key by
def sync_json_url(collection, json_url, key):
    response = urllib2.urlopen(json_url)
    data = json.load(response)
    sync(collection, data, key)