import pandas as pd
from urllib.parse import urlparse
import re
import numpy as np

# Regex patterns
URL_PATTERN = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
DOT_PATTERN = re.compile(r"\[(DOT|dot|\.)\]")
BRACKET_PATTERN = re.compile(r"\](?=\s|$)")

def extract_urls(text):
    if not isinstance(text, str):
        return []
    cleaned = DOT_PATTERN.sub(".", text)
    cleaned = BRACKET_PATTERN.sub("", cleaned)
    return URL_PATTERN.findall(cleaned)

def extract_domain(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        return domain[4:].lower() if domain.startswith("www.") else domain.lower()
    except:
        return ""

# Carica i dataset
newsguard_df = pd.read_csv("Newsguard.csv").dropna(subset=["Score"]).drop_duplicates()
messages_df = pd.read_csv("csv/output.csv").dropna(subset=["channelusername"])
clustering_df = pd.read_csv("csv/clustering_canali_filtrati.csv")

# Converti views e forwards in numerico e sostituisci NaN con 0
messages_df['views'] = pd.to_numeric(messages_df['views'], errors='coerce').fillna(0).astype(np.int64)
messages_df['forwards'] = pd.to_numeric(messages_df['forwards'], errors='coerce').fillna(0).astype(np.int64)

# Crea set di domini Newsguard per ricerca veloce
newsguard_domains = set(domain.lower() for domain in newsguard_df["Domain"] if isinstance(domain, str))

# Mappa ogni dominio al suo score e ogni community al suo cluster
domain_score_map = {domain.lower(): score for domain, score in zip(newsguard_df["Domain"], newsguard_df["Score"])}
clustering_map = dict(zip(clustering_df["node_id"], clustering_df["clustering_coefficient"]))

# Dizionario per tenere traccia delle metriche per dominio per community
community_domain_stats = {}

# Itera attraverso i messaggi
for _, row in messages_df.iterrows():
    community = row["channelusername"]
    message = row["message"]
    views = row["views"]
    forwards = row["forwards"]
    
    if not isinstance(message, str):
        continue
        
    urls = extract_urls(message)
    if not urls:
        continue
        
    # Estrai domini e filtra solo quelli presenti in Newsguard
    domains = {extract_domain(url) for url in urls}
    newsguard_matches = domains & newsguard_domains
    
    for domain in newsguard_matches:
        if community not in community_domain_stats:
            community_domain_stats[community] = {}
        if domain not in community_domain_stats[community]:
            community_domain_stats[community][domain] = {"views": 0, "forwards": 0}
        community_domain_stats[community][domain]["views"] += views
        community_domain_stats[community][domain]["forwards"] += forwards

# Lista per raccogliere i dati
records = []

# Crea i record finali
for community, domain_stats in community_domain_stats.items():
    for domain, stats in domain_stats.items():
        score = domain_score_map.get(domain, None)
        clustering = clustering_map.get(community, None)
        
        records.append({
            "Community": community,
            "Dominio": domain,
            "Views": stats["views"],
            "Forwards": stats["forwards"],
            "Score": score,
            "Clustering": clustering
        })

# Crea il nuovo dataframe e salvalo
result_df = pd.DataFrame(records).dropna(subset="Clustering")
result_df.to_csv("csv/analisi_canali_per_engagement.csv", index=False)

print("File csv/analisi_canali_per_engagement.csv salvato con successo.")