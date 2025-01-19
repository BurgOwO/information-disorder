import pandas as pd
import ast
import csv

# Leggi il file CSV
data = pd.read_csv("output.csv")
df = pd.DataFrame(data)

dizionario = {}

for index, replies in enumerate(df["replies"]):
    # Converti la stringa in un dizionario
    if isinstance(replies, str):
        replies = ast.literal_eval(replies)
    if isinstance(replies, dict) and replies["recent_repliers"]:
        # Scorro il numero degli utenti
        for user, _ in enumerate(replies["recent_repliers"]):
            # Verifico se l'utente ha un ID
            if "user_id" in replies["recent_repliers"][user]:
                # Verifico se l'utente esiste nel dizionario
                if replies["recent_repliers"][user]["user_id"] not in dizionario:
                    # Aggiungo l'utente al dizionario con il tipo "User" e la lista dei canali con cui ha interagito
                    dizionario[replies["recent_repliers"][user]["user_id"]] = ("User", [df["channelusername"][index]])
                else:
                    dizionario[replies["recent_repliers"][user]["user_id"]][1].append(df["channelusername"][index])

# Nome dei file CSV
nodes = "nodes.csv"
archs = "archs.csv"

target_set = set()

# Scrittura nel file CSV dei nodi
with open(nodes, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # Scrive l'intestazione delle colonne
    writer.writerow(["id", "type"])
    
    # Scrive le righe con chiavi e valori
    for key, (value, target) in dizionario.items():
        writer.writerow([key, value])

        for element in target:
            if element not in target_set:
                target_set.add(element)
                writer.writerow([element, "Channel"])

print("I dati sono stati salvati in %s." % nodes)

# Scrittura nel file CSV degli archi
with open(archs, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # Scrive l'intestazione delle colonne
    writer.writerow(["source", "target", "type"])
    
    # Scrive le righe con chiavi e valori
    for key, (_, target) in dizionario.items():
        for element in target:
            writer.writerow([key, element, "Reply"])

print("I dati sono stati salvati in %s." % archs)