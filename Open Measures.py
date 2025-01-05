import requests
import pandas as pd
import json
import os

# Leggere il token di autorizzazione
jwt_token = open("open-measures-key.txt", "r").read()

headers = {
    "Authorization": "Bearer %s" % jwt_token
}

with open("parametri/required_columns.json", "r") as f:
    data = json.load(f)
    required_columns = set(data)

with open("parametri/dtypes.json", "r") as f:
    dtypes = json.load(f)

with open("parametri/terms.json", "r") as f:
    terms = json.load(f)

def fetch_results(term, social, start_date, end_date, attempt_count=None):
    # Se attempt_count è None, inizializza un nuovo dizionario
    if attempt_count is None:
        attempt_count = {"count": 1}
    
    current_attempt = attempt_count["count"]
    
    params = {
        'term': '(message:http OR message:https) AND message:%s' % term,
        'limit': 10000,
        'site': social,
        'since': start_date,
        'until': end_date,
        'esquery': 'true'
    }

    url = 'https://api.openmeasures.io/content?{}'.format(
        '&'.join([f"{k}={v}" for k, v in params.items()])
    )

    # Richiesta API
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print("Richiesta API fallita con codice %d per il termine '%s'" % (r.status_code, term))
        return pd.DataFrame()

    data = r.json()
    hits = data.get('hits', {}).get('hits', [])

    if len(hits) == 10000:
        # Controlla se il range è un singolo giorno
        if pd.Timestamp(start_date) == pd.Timestamp(end_date):
            print("Tentativo %d per '%s': Range singolo giorno (%s), ancora troppi risultati. Restituisco dati senza ulteriore divisione." % 
                  (current_attempt, term, start_date))
            return pd.DataFrame([hit['_source'] for hit in hits])

        # Se non è un singolo giorno dimezza il range temporale
        mid_date = pd.Timestamp(start_date) + (pd.Timestamp(end_date) - pd.Timestamp(start_date)) / 2
        second_half = mid_date + pd.Timedelta(days=1)
        mid_date = mid_date.strftime("%Y-%m-%d")
        second_half = second_half.strftime("%Y-%m-%d")

        print("Tentativo %d per '%s': Range troppo grande (%s - %s). Divido a meta (%s - %s, %s - %s)." % 
              (current_attempt, term, start_date, end_date, start_date, mid_date, second_half, end_date))

        # Incrementa il contatore per i prossimi tentativi
        attempt_count["count"] += 1

        # Raccolta dei risultati da ciascuna metà
        first_half_df = fetch_results(term, social, start_date, mid_date, attempt_count)
        second_half_df = fetch_results(term, social, second_half, end_date, attempt_count)
        
        # Concatena solo se almeno uno dei DataFrame non è vuoto
        if not first_half_df.empty or not second_half_df.empty:
            dfs_to_concat = []
            for df in [first_half_df, second_half_df]:
                if not df.empty:
                    df = df.reindex(columns=required_columns.union(df.columns)).astype(dtypes)
                    dfs_to_concat.append(df)
            if dfs_to_concat:
                return pd.concat(dfs_to_concat, ignore_index=True)
            
        return pd.DataFrame()
    
    else:
        # Converte i risultati in un DataFrame
        df = pd.DataFrame([hit['_source'] for hit in hits])
        if not df.empty:
            df = df.reindex(columns=required_columns.union(df.columns)).astype(dtypes)
        return df

if __name__ == "__main__":
    social = "telegram".lower()
    terms = list(map(str.lower, terms))

    for term in terms:
        if not os.path.isfile(os.path.join("csv", "%s_%s_2024.csv" % (social, term.replace(" ", "_")))):
            try:
                total_df = pd.DataFrame()

                for i in range(1, 13):
                    month = "%02d" % i
                    if month in ["01", "03", "05", "07", "08", "10", "12"]:
                        days = 31
                    elif month in ["04", "06", "09", "11"]:
                        days = 30
                    else:
                        days = 29

                    start_date = "2024-%s-01" % month
                    end_date = "2024-%s-%s" % (month, days)

                    # Non serve passare alcun contatore, verrà inizializzato nella funzione
                    df = fetch_results(term, social, start_date, end_date, None)
                    print("Il mese %s ha prodotto %d risultati per il termine '%s'." % (month, len(df), term))

                    if not df.empty:
                        df = df.reindex(columns=required_columns.union(df.columns)).astype(dtypes)
                        total_df = pd.concat([total_df, df], ignore_index=True)

                if not total_df.empty:
                    output_file = "csv/%s_%s_2024.csv" % (social, term.replace(" ", "_"))
                    total_df.to_csv(output_file, index=False)
                    print("\nSalvato il file per il termine '%s' in: %s con %d righe.\n" % (term, output_file, len(total_df)))
                else:
                    print("\nNessun risultato trovato per il termine '%s'.\n" % term)
            except Exception as e:
                print("\nErrore durante il processamento del termine '%s': %s\n" % (term, str(e)))
    
    print("Tutti i termini sono stati processati.\n")