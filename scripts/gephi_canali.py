import pandas as pd
from itertools import combinations

# Imposta il filtro per prendere solo i canali di community_chiusura.csv
filter = True

if filter:
    output_archs = "csv/archs_canali_filtrati.csv"
    output_nodes = "csv/nodes_canali_filtrati.csv"
else:
    output_archs = "csv/archs_canali.csv"
    output_nodes = "csv/nodes_canali.csv"

df = pd.read_csv("csv/archs.csv").astype(str)

df_filter = pd.read_csv("csv/community_chiusura.csv").astype(str)
name_set = set(df_filter["Community"].unique())

if filter:
    df = df[df["target"].isin(name_set)]

# Crea un dizionario che mappa ogni source ai suoi target associati
source_to_targets = df.groupby("source")["target"].apply(set).to_dict()

# Cfea un dizionario che mappa ogni target alle sue source
target_to_sources = df.groupby("target")["source"].apply(set).to_dict()

# Trova tutte le coppie di target che condividono almeno una source comune
connections = []
for source, targets in source_to_targets.items():
    if len(targets) > 1:  # Solo se ci sono più target per una source
        for target_pair in combinations(targets, 2):
            connections.append(target_pair)

# Crea un dataframe per le connessioni
df_new = pd.DataFrame(connections, columns=["Source", "Target"])

# Rimuove duplicati e si assicura che ogni coppia sia unica (indipendentemente dall'ordine)
df_new = df_new.apply(lambda x: tuple(sorted(x)), axis=1).drop_duplicates().apply(pd.Series)
df_new.columns = ["Source", "Target"]

# Calcola il peso per ogni coppia di target
def calculate_weight(row):
    t1_sources = target_to_sources[row["Source"]]
    t2_sources = target_to_sources[row["Target"]]

    # Calcola il numero di source condivise
    shared_sources = len(t1_sources & t2_sources)

    # Calcola il numero totale di source per i due target
    total_sources = len(t1_sources | t2_sources)

    # Calcola il peso
    weight = shared_sources / total_sources if total_sources > 0 else 0
    return weight

df_new["weight"] = df_new.apply(calculate_weight, axis=1)
df_new["type"] = "Connection"

df_new.to_csv(output_archs, index=False)

print("File %s salvato con successo." % output_archs)

df_nodes = pd.read_csv("csv/nodes.csv")

if filter:
    df_nodes = df_nodes[df_nodes["id"].isin(name_set)]

df_nodes = df_nodes[df_nodes["type"] == "Channel"]

df_nodes.to_csv(output_nodes, index=False)

print("File %s salvato con successo." % output_nodes)