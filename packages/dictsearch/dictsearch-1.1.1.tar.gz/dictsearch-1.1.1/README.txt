Takes a dict, and a path delimited with slashes like A/B/C/D, and returns a list of all leaves at all trajectories dict[A][B][C][D]
    
If the path is an empty string, returns the original dict

Each non-leaf node can be either a dictionary or list of dictionaries
Each leaf node can be an arbitrary object. 




import dictsearch


d = dict()
d["A"] = dict()
d["A"]["B"] = []
d["A"]["B"].append(dict())
d["A"]["B"][0]["C"] = 123
d["A"]["B"].append(dict())
d["A"]["B"][1]["C"] = 123
d["A"]["B"].append(dict())
d["A"]["B"][2]["D"] = dict()
d["A"]["B"][2]["D"]["E"] = "ASDF"

print(d)
print( dictsearch.iterate_dictionary(d,"X/Y/Z"))
print( dictsearch.iterate_dictionary(d,"A"))
print( dictsearch.iterate_dictionary(d,"A/B"))
print( dictsearch.iterate_dictionary(d,"A/C"))
print( dictsearch.iterate_dictionary(d,"A/B/C"))
print( dictsearch.iterate_dictionary(d,"A/B/C/D")) #DOES NOT EXIST; D NOT AFTER PATH "C"
print( dictsearch.iterate_dictionary(d,"A/B/D/E")) 
print( dictsearch.iterate_dictionary(d,"A/B/E"))   #DOES NOT EXIST; E NOT A SUBPATH OF "B"

>>

{'A': {'B': [{'C': 123}, {'C': 123}, {'D': {'E': 'ASDF'}}]}}
[]
[{'B': [{'C': 123}, {'C': 123}, {'D': {'E': 'ASDF'}}]}]
[{'C': 123}, {'C': 123}, {'D': {'E': 'ASDF'}}]
[]
[123, 123]
[]
['ASDF']
[]
