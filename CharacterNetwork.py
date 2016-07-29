'''This script can be used to generate a character network
using JavaScript D3. The output is a json file with the connections
and their strength, to be read by the HTML file.

Author: Christopher Hench
License: MIT
'''

from string import punctuation
import re
import pandas as pd
from collections import defaultdict, Counter
from fuzzywuzzy import fuzz
from itertools import combinations
import json
import sys

text_path = sys.argv[1]
males = sys.argv[2]
females = sys.argv[3]
fmatch = int(sys.argv[4])


json_collect = {"nodes": [], "links": []}

# read in and make dict of names and unique ids
with open(males, "r") as f:
    maleNames = f.read().split("\n")

with open(females, "r") as f:
    femaleNames = f.read().split("\n")

for n in maleNames:
    json_collect["nodes"].append({"id": n, "group": 1})

for n in femaleNames:
    json_collect["nodes"].append({"id": n, "group": 2})

characterDict = {ch.lower(): str(i + 1)
                 for i, ch in enumerate(maleNames + femaleNames)}
revCharacterDict = {str(i + 1): ch
                    for i, ch in enumerate(maleNames + femaleNames)}

# open text and read to a string
with open(text_path, "r") as f:  # change name file um Text zu ändern
    textString = f.read()

# strip punctuation and make lowercase, split to get paragraphs
textParagraphs = "".join([ch for ch in textString if ch not in punctuation]).lower(
).split("\n\n")  # change after split

if fmatch == 1:  # use fuzzy matching
    # create hit dictionaries for paragraphs of character ids
    paraHits = []
    for i, para in enumerate(textParagraphs):
        for word in para.split():
            for name, cid in characterDict.items():
                # condition to append interaction
                if fuzz.ratio(word, name) > 80:
                    paraHits.append([i, name, cid])

else:  # only exact matches
    # create hit dictionaries for paragraphs of character ids
    paraHits = []
    for i, para in enumerate(textParagraphs):
        for name, cid in characterDict.items():
            # condition to append interaction
            if name in para:
                paraHits.append([i, name, cid])

paraHitDict = {}
for para, name, cid in paraHits:
    # check if paragraph exists yet as key in paraHitDict
    if para in paraHitDict:
        # check if character id already documented in that paragraph
        if cid in paraHitDict[para]:
            pass
        else:
            # append paragraph number and character id
            paraHitDict[para].append(cid)
    else:
        # if para does not exist as a key, add and assign first character id
        paraHitDict[para] = [cid]

all_links = []
for p in paraHitDict.keys():
    chars_in_para = [revCharacterDict[x] for x in paraHitDict[p]]
    if len(chars_in_para) >= 2:
        all_links += combinations(chars_in_para, 2)

link_freq = Counter(all_links)
for l in all_links:
    freq = link_freq[l]
    json_collect["links"].append(
        {"source": l[0], "target": l[1], "value": freq})

with open("network_data.json", "w") as f:
    json.dump(json_collect, f)

print()
print("JSON file saved.")
print()
