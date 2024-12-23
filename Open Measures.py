import requests
import json
import pandas as pd
import re
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

jwt_token = open("open-measures-key.txt", "r").read()

headers = {
    "Authorization": f"Bearer {jwt_token}"
}

term = "White Power".lower()
social = "telegram".lower()
total = 0

for i in range(1, 11):
    if i < 10:
        i = "0"+str(i)
    if i in ["01", "03", "05", "07", "08", "10", "12"]:
        ii = 31
    elif i in ["04", "06", "09", "11"]:
        ii = 30
    else:
        ii = 29

    # Configuring parameters - edit these!
    params = {
    'term' : f'(message:http OR message:https) AND message:{term}', # elasticsearch query string
    'limit': 10000,
    'site': f'{social}',
    'since': f'2024-{i}-01',
    'until': f'2024-{i}-{ii}',
    'esquery': 'true'
    }

    # We can create a URL to represent this query
    url = 'https://api.openmeasures.io/content?{}'.format(
        '&'.join(
            [f"{k}={v}" for k,v in params.items()]
        )
    )

    # now make a request to the API using Python requests
    r = requests.get(
        url,
        headers=headers
    )

    data = r.json()

    hits = data['hits']['hits']

    df = pd.DataFrame([hit['_source'] for hit in hits])

    print(f"Il mese {i} ha prodotto {len(df)} risultati.")
    total += len(df)

    if len(df) != 0:
        df.to_csv(f'csv/{social}_{term.replace(" ", "_")}_{i}_2024.csv')

print(f"Risultati totali: {total}.")