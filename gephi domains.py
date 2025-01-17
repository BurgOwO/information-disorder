import pandas as pd
import re
import ast
from urllib.parse import urlparse
import csv

def extract_urls(text):
    # Estrae tutti gli URL da una stringa di testo
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    if isinstance(text, str):
        cleaned_message = re.sub(r"\[(DOT|dot|\.)\]", ".", str(text))  # Sostituisce [DOT], [dot], [.] con "."
        cleaned_message = re.sub(r"\](?=\s|$)", "", cleaned_message)  # Rimuove ] alla fine di URL o parole
        return re.findall(url_pattern, cleaned_message)
    return []

def extract_domain(url):
    # Estrae il dominio da un URL
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower()
    except:
        return ""
    
if __name__ == "__main__":

    dizionario = {}

    df = pd.read_csv("output.csv")

    for _, row in df.iterrows():
        message = row["message"]
        urls = extract_urls(message)
        if urls:
            for url in urls:
                domain = extract_domain(url)
                if isinstance(row["replies"], str):                    
                    replies = ast.literal_eval(row["replies"])
                if isinstance(replies, dict) and replies["recent_repliers"]:
                    # Scorro il numero degli utenti
                    for user, _ in enumerate(replies["recent_repliers"]):
                        # Verifico se l'utente ha un ID
                        if "user_id" in replies["recent_repliers"][user]:
                            # Verifico se l'utente esiste nel dizionario
                            if replies["recent_repliers"][user]["user_id"] not in dizionario:
                                # Aggiungo l'utente al dizionario con il tipo "User" e la lista dei canali con cui ha interagito
                                dizionario[replies["recent_repliers"][user]["user_id"]] = ("User", [domain])
                            else:
                                dizionario[replies["recent_repliers"][user]["user_id"]][1].append(domain)

# Nome dei file CSV
nodes = "nodes_domain.csv"
archs = "archs_domain.csv"

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
                writer.writerow([element, "Domain"])

print("I dati sono stati salvati in %s con %d occorrenze" % (nodes, len(open("nodes_domain.csv", "r").read())))

# Scrittura nel file CSV degli archi
with open(archs, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # Scrive l'intestazione delle colonne
    writer.writerow(["source", "target", "type"])
    
    # Scrive le righe con chiavi e valori
    for key, (_, target) in dizionario.items():
        for element in target:
            writer.writerow([key, element, "Reply"])

print("I dati sono stati salvati in %s con %d occorrenze" % (archs, len(open("archs_domain.csv", "r").read())))