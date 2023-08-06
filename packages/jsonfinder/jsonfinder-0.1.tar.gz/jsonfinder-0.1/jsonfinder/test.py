import json
from greedyjson import iterator

with open('test.txt') as infile:
    string = infile.read()
    for x in iterator(string, non_json=str):
        print json.dumps(x, indent=2)