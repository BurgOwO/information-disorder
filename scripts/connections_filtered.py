import pandas as pd
from itertools import combinations
# Leggi il file
df = pd.read_csv("csv/archs_filtered.csv")
# Nome del file di output
output_file = "csv/archs_filtered_new.csv"
# Inizializza un DataFrame vuoto
df_total_users = pd.DataFrame(columns=["source", "target", "type"])
for _, group in df.groupby("target"):
    # Crea un set di utenti in modo che non vengano salvati più volte
    users = set()
    for user in group["source"]:
        users.add(user)
    
    # Genera le combinazioni e crea il DataFrame
    pairs = list(combinations(users, 2))
    df_new = pd.DataFrame(pairs, columns=["source", "target"]).drop_duplicates()
    
    # Aggiungi la colonna "type" con valore "Connection"
    df_new["type"] = "Connection"
    
    # Concatena al DataFrame totale
    df_total_users = pd.concat([df_total_users, df_new], ignore_index=True)
    
# Inizializza un DataFrame vuoto
df_total_channels = pd.DataFrame(columns=["source", "target", "type"])
for _, group in df.groupby("source"):
    # Crea un set di utenti in modo che non vengano salvati più volte
    targets = set()
    for target in group["target"]:
        targets.add(target)
    
    # Genera le combinazioni e crea il DataFrame
    pairs = list(combinations(targets, 2))
    df_new = pd.DataFrame(pairs, columns=["source", "target"]).drop_duplicates()
    
    # Aggiungi la colonna "type" con valore "Connection"
    df_new["type"] = "Connection"
    
    # Concatena al DataFrame totale
    df_total_channels = pd.concat([df_total_channels, df_new], ignore_index=True)
# Concatena il DataFrame totale al DataFrame originale
df_final = pd.concat([df, df_total_users, df_total_channels], ignore_index=True).dropna()
df_final.to_csv(output_file, index=False)
print("File %s salvato con successo." % output_file)