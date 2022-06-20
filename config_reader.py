import json
import re

with open('config_map12e.json', 'r') as read_file:
    data = json.load(read_file)

# for x in data['device']['channels']:
#     if ' ' in x['name']:
#         try:
#             print(x['name'], x['address'], x['scale'])
#         except IndexError:
#             print(x['name'], x['address'])

out_dict = {}

for x in data['device']['channels']:
    string = f'Ch \d{1} ' + 'Total P'
    name = 'Total P'
    try:
        test = re.findall(r'Ch \d{1} Total P$', x['name'])[0]
        out_dict[test] = x['address']
    except IndexError:
        pass

print(out_dict)
