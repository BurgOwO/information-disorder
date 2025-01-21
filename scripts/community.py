import pandas as pd
import re
from collections import defaultdict
from urllib.parse import urlparse
import numpy as np

# Compilazione del pattern regex per migliorare le performance
URL_PATTERN = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
DOT_PATTERN = re.compile(r"\[(DOT|dot|\.)\]")
BRACKET_PATTERN = re.compile(r"\](?=\s|$)")

def preprocess_newsguard_data(newsguard_df):
    clean_df = newsguard_df.dropna(subset=["Score"]).drop_duplicates()
    
    return {
        'original_domains': {d.lower(): d for d in clean_df["Domain"] 
                           if isinstance(d, str)},
        'orientations': {d.lower(): o for d, o in zip(clean_df["Domain"], clean_df["Orientation"]) 
                        if isinstance(d, str)},
        'scores': {d.lower(): s for d, s in zip(clean_df["Domain"], clean_df["Score"])
                  if isinstance(d, str)},
        'topics': {d.lower(): t for d, t in zip(clean_df["Domain"], clean_df["Topics"]) 
                  if isinstance(d, str)}
    }

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

def process_community_stats(df, newsguard_data):
    community_stats = defaultdict(lambda: {"messaggi": 0, "views": 0, "forwards": 0, "domains": {}})
    newsguard_domains = set(newsguard_data['original_domains'].keys())
    
    df['views'] = pd.to_numeric(df['views'], errors='coerce').fillna(0).astype(np.int32)
    df['forwards'] = pd.to_numeric(df['forwards'], errors='coerce').fillna(0).astype(np.int32)
    
    for community, group in df.groupby('channelusername'):
        valid_messages = group[group['message'].notna()]
        
        for _, row in valid_messages.iterrows():
            urls = extract_urls(row['message'])
            if not urls:
                continue
                
            domains = {extract_domain(url) for url in urls}
            matching_domains = domains & newsguard_domains
            
            if matching_domains:
                stats = community_stats[community]
                stats["messaggi"] += 1
                stats["views"] += row['views']
                stats["forwards"] += row['forwards']
                
                for domain in matching_domains:
                    if domain in community_stats[community]["domains"]:
                        community_stats[community]["domains"][domain] += 1
                    else:
                        community_stats[community]["domains"][domain] = 1
    
    return community_stats

def calculate_topic_percentages(domains, topics_data):
    # Raccoglie tutti i topic da tutti i domini
    all_topics = []
    for domain in domains:
        topic_str = topics_data.get(domain, '')
        if isinstance(topic_str, str):
            topics = [t.strip() for t in topic_str.split(',') if t.strip()]
            all_topics.extend(topics)
    
    if not all_topics:
        return {}
    
    # Calcola le percentuali
    topic_counts = {}
    total_topics = len(all_topics)
    for topic in set(all_topics):
        count = all_topics.count(topic)
        topic_counts[topic] = (count / total_topics) * 100
        
    return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

def calculate_orientation_percentages(domains, orientations_data):
    # Raccoglie tutti gli orientamenti validi
    orientations = [orientations_data.get(domain) for domain in domains]
    orientations = [o for o in orientations if o == o]
    
    if not orientations:
        return None
    
    # Calcola le percentuali
    orientation_counts = {}
    total = len(orientations)
    for orientation in set(orientations):
        count = orientations.count(orientation)
        orientation_counts[orientation] = (count / total) * 100
    
    return dict(sorted(orientation_counts.items(), key=lambda x: x[1], reverse=True))

def calculate_community_data(community_stats, newsguard_data):
    community_data = []
    
    for community, stats in community_stats.items():
        if not stats['domains']:
            continue
            
        domains = stats['domains']
        
        # Calcola topic e orientamenti usando le funzioni dedicate
        topic_percentages = calculate_topic_percentages(domains, newsguard_data['topics'])
        orientation_percentages = calculate_orientation_percentages(domains, newsguard_data['orientations'])
        
        # Calcola score medio
        valid_scores = [newsguard_data['scores'].get(domain) 
                       for domain in domains 
                       if domain in newsguard_data['scores']]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        community_data.append({
            "Community": community,
            "Messaggi": stats["messaggi"],
            "Views": stats["views"],
            "Forwards": stats["forwards"],
            "Score medio": avg_score,
            "Top topic": max(topic_percentages.items(), key=lambda x: x[1])[0] if topic_percentages else '',
            "Top domain": max(domains.items(), key=lambda x: x[1])[0],
            "Orientamento percentuale": orientation_percentages,
            "Topic percentuale": topic_percentages,
            "Domini": domains,
            "Frequent domains": dict(sorted(domains.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True)[:5])
        })
    
    return community_data

if __name__ == "__main__":
    # Caricamento dei dati
    df = pd.read_csv("csv/output.csv")
    newsguard_df = pd.read_csv("Newsguard.csv")
    output_file = "csv/community.csv"
    
    try:
        # Preprocessing dei dati Newsguard
        newsguard_data = preprocess_newsguard_data(newsguard_df)
        
        # Elaborazione delle statistiche
        community_stats = process_community_stats(df, newsguard_data)
        
        # Calcolo dei dati finali
        community_data = calculate_community_data(community_stats, newsguard_data)
        
        # Creazione e salvataggio del DataFrame finale
        if community_data:
            output_df = pd.DataFrame(community_data)
            output_df = output_df.sort_values("Views", ascending=False)
            output_df.to_csv(output_file, index=False)
            print("File %s salvato con successo." % output_file)
        else:
            print("Nessuna community trovata.")
            
    except Exception as e:
        print("Si è verificato un errore:", str(e))