import json

# Syncs a JSON file with a Python dictionary
#
# Syncs by top-level keys. Each top-level key
# should have a dictionary value. The value
# of each second-level key will be updated
# to reflect that of the current data.
def sync(json_filename, data):
    json_file = open(json_filename)
    json_data = json.load(json_file)
    json_file.close()

    for key in data:
        for k, v in data[key].iteritems():
            json_data[key][k] = v

    with open(json_filename, 'w') as outfile:
        json.dump(json_data, outfile)

# Syncs a JSON file with a JSON string
def sync_json(json_filename, data):
    sync(json_filename, json.loads(data))

# Syncs a JSON file with another JSON file
def sync_json(json_filename, other_filename):
    other_file = open(other_filename)
    other_data = json.load(other_file)
    other_file.close()

    sync(json_filename, other_data)