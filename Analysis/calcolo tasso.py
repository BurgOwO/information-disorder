import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Caricare i dati dal file CSV
file_path = 'data.csv'
df = pd.read_csv(file_path)

# Stampare le colonne presenti nel CSV per il debug
print("Colonne presenti nel CSV:", df.columns.tolist())

# Filtrare i nodi di tipo "Channel" e creare una copia per evitare il warning
channel_nodes = df[df["type"] == "Channel"].copy()

# Assicurarsi che le colonne necessarie siano presenti
required_columns = ["degree", "closnesscentrality", "betweenesscentrality", "Authority", "eigencentrality"]
if not all(col in channel_nodes.columns for col in required_columns):
    raise ValueError(f"Il file CSV deve contenere le seguenti colonne: {', '.join(required_columns)}")

# Creare una copia delle metriche per normalizzarle senza sovrascrivere i dati originali
metrics = ["degree", "closnesscentrality", "betweenesscentrality", "Authority", "eigencentrality"]
scaler = MinMaxScaler()
normalized_metrics = scaler.fit_transform(channel_nodes[metrics])

# Calcolare il tasso di apertura usando le metriche normalizzate
channel_nodes["Openness"] = normalized_metrics.mean(axis=1)

# Unire i risultati al DataFrame originale
df = df.merge(channel_nodes[["Id", "Openness"]], on="Id", how="left")

# Salvare il DataFrame con la nuova colonna in un file CSV
output_file_path = "statpython_with_openness.csv"
df.to_csv(output_file_path, index=False)

# Stampare conferma
print(f"Tasso di apertura calcolato per i nodi di tipo 'Channel' e salvato in '{output_file_path}'")
