import os
import pandas as pd
import re
from urllib.parse import urlparse
from collections import defaultdict

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

def process_csvs(output_filename, occorrenze_filename, newsguard_filename="Newsguard.csv", folder_path="csv"):
    # Carica il file Newsguard
    newsguard_df = pd.read_csv(newsguard_filename)
    
    # Dizionario per mantenere la capitalizzazione originale dei domini
    original_domains = {domain.lower(): domain for domain in newsguard_df["Domain"] 
                       if isinstance(domain, str)}
    # Mappa gli score per i domini
    domain_scores = {domain.lower(): score for domain, score in zip(newsguard_df["Domain"], newsguard_df["Score"])
                    if isinstance(domain, str)}
    newsguard_domains = set(original_domains.keys())
    
    # Colonne da mantenere nell'output
    columns_to_keep = ["message", "channelusername", "reactions", "forwards", 
                      "postauthor", "replies", "views"]
    
    # Liste e dizionari per memorizzare i dati
    matching_rows = []
    
    # Utilizzo defaultdict per inizializzare automaticamente i contatori
    domain_stats = defaultdict(lambda: {"occorrenze": 0, "views": 0, "forwards": 0})

    # Processa ogni file CSV nella cartella csv/
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            print("Elaborazione file: %s" % filename)
            try:
                df = pd.read_csv(os.path.join(folder_path, filename), low_memory=False)
                
                for _, row in df.iterrows():
                    if isinstance(row["message"], str):
                        urls = extract_urls(row["message"])
                        domains = {extract_domain(url) for url in urls}
                        
                        # Se c'è almeno una corrispondenza con i domini di Newsguard
                        matching_domains = domains & newsguard_domains
                        if matching_domains:
                            matching_rows.append(row[columns_to_keep])
                            
                            # Aggiorna le statistiche per ogni dominio trovato
                            views = int(row["views"]) if pd.notna(row["views"]) else 0
                            forwards = int(row["forwards"]) if pd.notna(row["forwards"]) else 0
                            
                            for domain in matching_domains:
                                domain_stats[domain]["occorrenze"] += 1
                                domain_stats[domain]["views"] += views
                                domain_stats[domain]["forwards"] += forwards
            
            except Exception as e:
                print("Errore nel processare %s: %s" % (filename, str(e)))

    # Crea il DataFrame finale con tutte le righe che hanno match
    if matching_rows:
        output_df = pd.DataFrame(matching_rows)
        output_df.to_csv(output_filename, index=False)
        print("\nAnalisi completata. File %s creato con %s corrispondenze." % (output_filename, len(output_df)))
    else:
        print("\nNessuna corrispondenza trovata.")

    # Crea il DataFrame delle occorrenze solo per i domini con occorrenze > 0
    occorrenze_data = []
    for domain_lower, stats in domain_stats.items():
        if stats["occorrenze"] > 0:  # Include solo domini con almeno un'occorrenza
            occorrenze_data.append({
                "Domain": original_domains[domain_lower],  # Usa la capitalizzazione originale
                "Score": domain_scores[domain_lower],  # Aggiunge lo Score di Newsguard
                "Occorrenze": stats["occorrenze"],
                "Views": stats["views"],
                "Forwards": stats["forwards"]
            })
    
    if occorrenze_data:
        occorrenze_df = pd.DataFrame(occorrenze_data)
        # Ordina il DataFrame per numero di occorrenze in ordine decrescente
        occorrenze_df = occorrenze_df.sort_values("Occorrenze", ascending=False)
        occorrenze_df.to_csv(occorrenze_filename, index=False)
        print("File %s creato con %s domini attivi.\n" % (occorrenze_filename, len(occorrenze_df)))
    else:
        print("Nessun dominio con occorrenze trovato.\n")

if __name__ == "__main__":
    output = "output.csv"
    occorrenze = "occorrenze.csv"

    process_csvs(output, occorrenze)