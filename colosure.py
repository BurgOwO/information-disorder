import pandas as pd

df = pd.read_csv("archs_new_2.csv")
df = df[df.type == "Reply"]
df_community = pd.read_csv("community.csv")

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

df_community = df_community[df_community["Messaggi"] >= 200].dropna(subset=["Tasso di chiusura"])
# Salva il DataFrame in un file CSV
df_community.to_csv("community_new.csv", index=False)