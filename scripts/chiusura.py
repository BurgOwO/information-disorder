import pandas as pd
import numpy as np

df = pd.read_csv("csv/archs_new.csv", low_memory=False)
df = df[df.type == "Reply"]
df_community = pd.read_csv("csv/community.csv")
df_closure_gephi = pd.read_csv("csv/chiusura_gephi.csv").dropna(subset=["Tasso di chiusura"])

output_path = "csv/community_new.csv"
txt_path = "correlazione.txt"

# Calcolo degli utenti unici per ciascun canale
users_per_channel = df.groupby("target")["source"].apply(set).to_dict()

# Calcolo dei canali totali con cui ciascun utente interagisce
channels_per_user = df.groupby("source")["target"].apply(set).to_dict()

# Calcolo del tasso di chiusura per ciascun canale
closure_scores = {}
for channel, users in users_per_channel.items():
    total_channels = sum(len(channels_per_user[user]) for user in users)
    closure_scores[channel] = len(users) / total_channels

# Aggiunta del tasso di chiusura al secondo DataFrame
df_community["Tasso di chiusura"] = df_community["Community"].map(closure_scores)

df_closure_gephi = df_closure_gephi[["Id", "Tasso di chiusura"]]
df_closure_gephi.rename(columns={"Tasso di chiusura": "Chiusura Gephi"}, inplace=True)

df_community = df_community.merge(df_closure_gephi, left_on="Community", right_on="Id", how="left")
df_community.drop(columns=["Id"], inplace=True)

df_community = df_community[df_community["Messaggi"] >= 45].dropna(subset=["Tasso di chiusura"])
# Salva il DataFrame in un file CSV
df_community.to_csv(output_path, index=False)
print("File %s salvato con successo." % output_path)

correlazione_matematica = np.corrcoef(df_community["Score medio"], df_community["Tasso di chiusura"])[0, 1]
correlazione_gephi = np.corrcoef(df_community["Score medio"], df_community["Chiusura Gephi"])[0, 1]

with open(txt_path, 'w') as file:
    file.write("Correlazione calcolata mediante il Coefficiente di Pearson\n\n")
    file.write("Correlazione con chiusura matematica: %f\nCorrelazione con chiusura basata sui grafi: %f" % (correlazione_matematica, correlazione_gephi))

print("File %s salvato con successo." % txt_path)

print("\nCorrelazione calcolata mediante il Coefficiente di Pearson\n")
print("Correlazione con chiusura matematica: %f\nCorrelazione con chiusura basata sui grafi: %f\n" % (correlazione_matematica, correlazione_gephi))
