import pandas as pd
from itertools import combinations

# Leggi il file
df = pd.read_csv("archs.csv")

# Nome del file di output
output_file = "archs_new.csv"

# Inizializza un DataFrame vuoto
df_total = pd.DataFrame(columns=["source", "target", "type"])

for target, group in df.groupby("target"):
    # Crea un set di utenti in modo che non vengano salvati più volte
    users = set()
    for user in group["source"]:
        users.add(user)
    
    # Genera le combinazioni e crea il DataFrame
    pairs = list(combinations(users, 2))
    df_new = pd.DataFrame(pairs, columns=["source", "target"])
    
    # Aggiungi la colonna "type" con valore "Connection"
    df_new["type"] = "Connection"
    
    # Concatena al DataFrame totale
    df_total = pd.concat([df_total, df_new], ignore_index=True)

# Concatena il DataFrame totale al DataFrame originale
df_final = pd.concat([df, df_total], ignore_index=True)
df_final.to_csv(output_file, index=False)

print("File %s salvato con successo." % output_file)