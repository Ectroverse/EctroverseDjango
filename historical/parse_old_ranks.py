import io
import requests
import pandas as pd
from zipfile import ZipFile

filename = '/home/marc/Downloads/rankings/round27ranks.txt'
with open(filename, 'r') as f:
    html_string = f.read().replace('\n', '')
data = pd.read_html(html_string)[0]
data = data.values.tolist()
for d in data[1:]:
    if len(d) == 6:
        rank, faction, empire, planets, networth, race = d
    elif len(d) == 5:
        rank, name, planets, players, networth = d
    else:
        print("error!")
        exit()
    print(rank)
    print(networth)
    print()
