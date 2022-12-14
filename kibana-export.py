import requests
import ndjson
import sys
import getopt

def usage():
    print(f"{sys.argv[0]} -o|--output <file> -k|--key <API key> -e|--env <prod|nonprod> -t|--type <object type> [-r]")

try:
    opts, args = getopt.getopt(sys.argv[1:], 'ho:k:e:t:r', ['help', 'output=', 'key=', 'env=', 'type='])
except getopt.GetoptError as err:
    print(f"{err}")
    usage()
    sys.exit(2)

output = None
api_key = None
env = None
object_type = None
include_refs = False

for opt, arg in opts:
    if opt in ('-o', '--output'):
        output = arg
    elif opt in ('-k', '--key'):
        api_key = arg
    elif opt in ('-e', '--env'):
        env = arg
    elif opt in ('-t', '--type'):
        object_type = arg
    elif opt == '-r':
        include_refs = True
    elif opt in ("-h", "--help"):
        usage()
        sys.exit()
    else:
        assert False, f"Unhandled option: {opt}"

if env == 'prod':
    # prod
    host = 'kibana.logs.diligent.com'
elif env == 'nonprod':
    # nonprod
    host = 'kibana-nonprod.logs.diligent.com'
else:
    print("Please specify environment (prod/nonprod) with '-e'!")
    sys.exit(1)

if not api_key:
    print("Please specify API key with '-k'!")
    sys.exit(1)

if not output:
    print("Please specify output file with '-o'!")
    sys.exit(1)

if not object_type:
    print("Please specify the object type to export '-t'!")
    sys.exit(1)

protocol = 'https'

api_paths = {'dashboard_export': 'api/saved_objects/_export',
			'objects_bulk_get': 'api/saved_objects/_bulk_get'
}

#dashboards = ('f1a1af7b-320c-41da-bbf6-4971b4a65e5d',
#        'd7d7d40d-9771-4244-a30c-f53aa816ccd8')
#dashboards = ('b0804f40-05d3-11ec-89fe-ef2ec4004aca',)
dashboards = ()

headers = { 'Content-Type': 'application/json',
            'kbn-xsrf': 'true',
            'Authorization': 'ApiKey ' + api_key
}

# Individually export objects
for dashboard in dashboards:
    print(f"Exporting '{dashboard}'")
    data = { 'objects': [
            { 'type': 'dashboard', 'id': dashboard }
        ],
        #"includeReferencesDeep": 'true'
    }
    #print(f"(individual)data='{data}'")
    ret = requests.post(f"{protocol}://{host}/{api_paths['dashboard_export']}", json=data, headers=headers)
    """
    if ret.status_code >= 300:
        print(repr(ret))
    """
    ret.raise_for_status()

    #print(f"ret.text='{ret.text}'")
    dash = ndjson.loads(ret.text)
    #print(f"dash='{dash}'")
    for obj in dash:
        #print(f"obj='{obj}'")
        if 'type' in obj  and  obj['type'] == 'dashboard':
            print(f"\t(individual)title: {obj['attributes']['title']}")
            title = obj['attributes']['title']

    with open(f"./{output}", 'w') as output:
        output.write(ret.text)


# Bulk save objects (dashboards in this case)
data = {}
#for dashboard in dashboards:
#    data.append({ 'type': 'dashboard', 'id': dashboard })   # <- the query essentially
#data['objects'] = []
#data['objects'].append({ 'type': 'dashboard' })
data['type'] = object_type
data['includeReferencesDeep'] = 'true' if include_refs else 'false'
#print(f"(bulk)data='{data}'")

print("Retrieving dashboards...")
ret = requests.post(f"{protocol}://{host}/{api_paths['dashboard_export']}", json=data, headers=headers)
ret.raise_for_status()
dashes = ndjson.loads(ret.text)
print("Retrieved dashboards:")
for obj in dashes:
    #print(f"obj='{obj}'")
    if 'type' in obj  and  obj['type'] == object_type:
        print(f"\t(bulk)title: {obj['attributes']['title']}")

print("Saving dashboards...")
with open(f"./{output}", 'w') as output:
    output.write(ret.text)

