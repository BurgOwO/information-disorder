import pandas as pd
import matplotlib.pyplot as plt
import os

# Crea la cartella per i grafici se non esiste
os.makedirs("istogrammi", exist_ok=True)

# Carica i dati principali
df = pd.read_csv("csv/analisi_canali_per_domini.csv")

# Definisce i range di score
bins = list(range(0, 101, 5))  # Range da 0 a 100 con step di 5
labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]  # Etichette dei bin

# Crea gli istogrammi per ogni community
for community, group in df.groupby("Community"):
    # Assegna i punteggi ai bin
    group["ScoreRange"] = pd.cut(group["Score"], bins=bins, labels=labels, right=True)

    # Somma le occorrenze per ciascun range di score
    score_counts = group.groupby("ScoreRange", observed=False)["Occorrenze"].sum().fillna(0)

    # Calcola statistiche
    mean_score = group["Score"].mean()
    var_score = group["Score"].var()
    total_occurrences = group["Occorrenze"].sum()

    # Recupera il valore di Clustering per la community corrente (se esiste)
    clustering_coeff = group["Clustering"].iloc[0] if "Clustering" in group.columns else "N/A"
    
    # Se il valore è NaN, sostituiscilo con "N/A"
    clustering_coeff = "N/A" if pd.isna(clustering_coeff) else clustering_coeff

    # Crea il grafico con spazio extra per la tabella
    fig, ax = plt.subplots(figsize=(14, 6))  # Aumentata la larghezza per ospitare meglio la tabella
    ax.bar(score_counts.index, score_counts.values, color='skyblue', edgecolor='black')

    ax.set_xlabel("Score Range")
    ax.set_ylabel("Somma delle Occorrenze")
    ax.set_title(f"Distribuzione Score per {community}")

    # Imposta correttamente i tick dell'asse X
    ax.set_xticks(range(len(score_counts)))  # Fissa i tick ai valori corrispondenti
    ax.set_xticklabels(score_counts.index, rotation=45)  # Ora possiamo impostare le etichette

    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Dati della tabella con etichette più leggibili
    table_data = [
        ["Media Score", f"{mean_score:.2f}"],
        ["Varianza Score", f"{var_score:.2f}"],
        ["Totale Occorrenze", f"{total_occurrences}"],
        ["Coefficiente di Clustering", f"{clustering_coeff}"]
    ]

    # Aggiungi la tabella a destra del grafico
    table = ax.table(cellText=table_data, colLabels=["Parametro", "Valore"],
                     cellLoc="center", loc="center right",
                     bbox=[1.05, 0.2, 0.4, 0.5])  # bbox più largo per gestire meglio il testo

    # Aumenta la dimensione della tabella per evitare tagli
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.4)  # Scala la tabella per maggiore leggibilità

    # Salva il grafico
    plt.savefig(f"istogrammi/{community}.png", bbox_inches="tight")
    plt.close()
