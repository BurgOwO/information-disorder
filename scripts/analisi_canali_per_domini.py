import pandas as pd
import ast

# Carica i dataset
newsguard_df = pd.read_csv("Newsguard.csv")
community_df = pd.read_csv("csv/community_chiusura.csv")
clustering_df = pd.read_csv("csv/clustering_canali_filtrati.csv")

# Mappa ogni dominio al suo score
domain_score_map = dict(zip(newsguard_df["Domain"], newsguard_df["Score"]))

# Mappa ogni community al suo cluster
clustering_map = dict(zip(clustering_df["node_id"], clustering_df["clustering_coefficient"]))

# Lista per raccogliere i dati
records = []

# Itera le righe di community_df
for _, row in community_df.iterrows():
    community = row["Community"]
    domain_dict_str = row["Domini"]
    
    # Converte la stringa in un vero dizionario
    try:
        domain_dict = ast.literal_eval(domain_dict_str)
    except Exception as e:
        print("Errore nella conversione della colonna Domini per %s: %s" % (community, e))
        continue
    
    # Estrae i dati
    for domain, occurrences in domain_dict.items():
        score = domain_score_map.get(domain, None)  # Recupera lo score
        clustering = clustering_map.get(community, None)  # Recupera il clustering

        records.append({
            "Community": community,
            "Dominio": domain,
            "Occorrenze": occurrences,
            "Score": score,
            "Clustering": clustering
        })

# Crea il nuovo dataframe
result_df = pd.DataFrame(records)

# Salva il file principale
result_df.to_csv("csv/analisi_canali_per_domini.csv", index=False)

print("File csv/analisi_canali_per_domini.csv salvato con successo.")
