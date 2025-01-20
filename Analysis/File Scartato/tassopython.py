import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Caricare i dati dal file CSV
file_path = 'statpython.csv'
df = pd.read_csv(file_path)

# Assicurarsi che le colonne necessarie siano presenti
required_columns = ["Node", "Degree", "Betweenness", "Closeness", "Authority", "Eigenvector"]
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"Il file CSV deve contenere le seguenti colonne: {', '.join(required_columns)}")

# Creare una copia delle metriche per normalizzarle senza sovrascrivere i dati originali
metrics = ["Degree", "Betweenness", "Closeness", "Authority", "Eigenvector"]
scaler = MinMaxScaler()
normalized_metrics = scaler.fit_transform(df[metrics])

# Calcolare il tasso di apertura usando le metriche normalizzate
df["Openness"] = normalized_metrics.mean(axis=1)

# Salvare il DataFrame con la nuova colonna in un file CSV
output_file_path = "statpython_with_openness.csv"
df.to_csv(output_file_path, index=False)

# Stampare conferma
print(f"Tasso di apertura calcolato e salvato in '{output_file_path}'")
