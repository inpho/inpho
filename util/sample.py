#!/usr/bin/python2
from urllib2 import urlopen
import json

# set a global host parameter so you can test on different servers
host = "https://inpho.cogs.indiana.edu"
# open the url
data = urlopen(host + "/idea/646/graph.json")

# load results into native python objects
graph = json.loads(data.read())
graph = graph['responseData']['result']

# print top 10 ii edges
print "RAW DATA, JWEIGHT SORTED BY DEFAULT"
for edge in graph['ii_out'][:10]:
    print edge['ante'], "->", edge['cons'], edge['jweight'], edge['weight']

# for reference on how to sort based on an alternate method
# in-place sort
print "IN-PLACE SORT"
graph['ii_out'].sort(key=lambda x: x['weight'])
for edge in graph['ii_out'][:10]:
    print edge['ante'], "->", edge['cons'], edge['jweight'], edge['weight']

# sort returning a new list - original unmodified
print "NEW LIST SORT"
sorted_edges = sorted(graph['ii_out'], key=lambda x: x['cons'])
for edge in sorted_edges[:10]:
    print edge['ante'], "->", edge['cons'], edge['jweight'], edge['weight']

