import pandas as pd
import re
from collections import defaultdict
from urllib.parse import urlparse
import numpy as np

URL_PATTERN = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
DOT_PATTERN = re.compile(r"\[(DOT|dot|\.)\]")
BRACKET_PATTERN = re.compile(r"\](?=\s|$)")

# Mappa i dati di Newsguard
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
    community_stats = defaultdict(lambda: {
        "messaggi": 0, 
        "views": 0, 
        "forwards": 0, 
        "domains": {},
        "domain_views": {},  # per tenere traccia delle views per dominio
        "domain_forwards": {}  # per tenere traccia dei forwards per dominio
    })
    
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
                    # Aggiorna conteggi domini
                    if domain in stats["domains"]:
                        stats["domains"][domain] += 1
                    else:
                        stats["domains"][domain] = 1
                    
                    # Aggiorna views per dominio
                    if domain not in stats["domain_views"]:
                        stats["domain_views"][domain] = 0
                    stats["domain_views"][domain] += row['views']
                    
                    # Aggiorna forwards per dominio
                    if domain not in stats["domain_forwards"]:
                        stats["domain_forwards"][domain] = 0
                    stats["domain_forwards"][domain] += row['forwards']
    
    return community_stats

def calculate_weighted_score(domains, domain_weights, scores_data):
    total_weight = 0
    weighted_sum = 0
    
    for domain, weight in domain_weights.items():
        score = scores_data.get(domain)
        if score is not None:
            weighted_sum += score * weight
            total_weight += weight
            
    return weighted_sum / total_weight if total_weight > 0 else 0

def calculate_simple_average_score(domains, scores_data):
    valid_scores = [scores_data.get(domain) for domain in domains if domain in scores_data]
    return sum(valid_scores) / len(valid_scores) if valid_scores else None

def calculate_community_data(community_stats, newsguard_data):
    community_data = []
    
    for community, stats in community_stats.items():
        if not stats['domains']:
            continue
            
        domains = stats['domains']
        
        # Calcola la media semplice basata sulle occorrenze
        simple_avg_score = calculate_simple_average_score(
            domains.keys(), 
            newsguard_data['scores']
        )
        
        # Calcola gli score ponderati
        views_weighted_score = calculate_weighted_score(
            domains, 
            stats['domain_views'], 
            newsguard_data['scores']
        )
        
        forwards_weighted_score = calculate_weighted_score(
            domains, 
            stats['domain_forwards'], 
            newsguard_data['scores']
        )
        
        topic_percentages = calculate_topic_percentages(domains, newsguard_data['topics'])
        orientation_percentages = calculate_orientation_percentages(domains, newsguard_data['orientations'])
        
        community_data.append({
            "Community": community,
            "Messaggi": stats["messaggi"],
            "Views": stats["views"],
            "Forwards": stats["forwards"],
            "Score medio occorrenze": simple_avg_score,
            "Score medio views": views_weighted_score,
            "Score medio forwards": forwards_weighted_score,
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

def calculate_topic_percentages(domains, topics_data):
    all_topics = []
    for domain in domains:
        topic_str = topics_data.get(domain, '')
        if isinstance(topic_str, str):
            topics = [t.strip() for t in topic_str.split(',') if t.strip()]
            all_topics.extend(topics)
    
    if not all_topics:
        return {}
    
    topic_counts = {}
    total_topics = len(all_topics)
    for topic in set(all_topics):
        count = all_topics.count(topic)
        topic_counts[topic] = (count / total_topics) * 100
        
    return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

def calculate_orientation_percentages(domains, orientations_data):
    orientations = [orientations_data.get(domain) for domain in domains]
    orientations = [o for o in orientations if o == o]  # Rimuove i NaN
    
    if not orientations:
        return None
    
    orientation_counts = {}
    total = len(orientations)
    for orientation in set(orientations):
        count = orientations.count(orientation)
        orientation_counts[orientation] = (count / total) * 100
    
    return dict(sorted(orientation_counts.items(), key=lambda x: x[1], reverse=True))

if __name__ == "__main__":
    df = pd.read_csv("csv/output.csv")
    newsguard_df = pd.read_csv("Newsguard.csv")
    output_file = "csv/community_engagement.csv"
    
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
        print("Si è verificato un errore:", str(e))