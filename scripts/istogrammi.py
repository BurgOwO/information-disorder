import pandas as pd
import matplotlib.pyplot as plt
import os

def crea_istogrammi(df, param):
    # Crea la cartella per i grafici se non esiste
    dir = "istogrammi_%s" % param.lower()
    os.makedirs(dir, exist_ok=True)

    # Definisce i range di score
    bins = list(range(0, 101, 5))  # Range da 0 a 100 con step di 5
    labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]  # Etichette dei bin

    # Crea gli istogrammi per ogni community
    for community, group in df.groupby("Community"):
        # Assegna i punteggi ai bin
        group["ScoreRange"] = pd.cut(group["Score"], bins=bins, labels=labels, right=True)

        # Somma i parametri per ciascun range di score
        score_counts = group.groupby("ScoreRange", observed=False)[param].sum().fillna(0)

        # Calcola statistiche
        mean_score = group["Score"].mean()
        var_score = group["Score"].var()
        total_occurrences = group[param].sum()

        # Recupera il valore di Clustering per la community corrente
        clustering_coeff = group["Clustering"].iloc[0] if "Clustering" in group.columns else "N/A"
        
        # Se il valore è NaN, sostituiscilo con "N/A"
        clustering_coeff = "N/A" if pd.isna(clustering_coeff) else clustering_coeff

        # Crea il grafico
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.bar(score_counts.index, score_counts.values, color='skyblue', edgecolor='black')

        ax.set_xlabel("Score Range")
        ax.set_ylabel("Somma di %s" % param)
        ax.set_title("Distribuzione Score per %s" % community)
        ax.set_xticks(range(len(score_counts)))
        ax.set_xticklabels(score_counts.index, rotation=45)

        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Dati della tabella con etichette più leggibili
        table_data = [
            ["Media Score", f"{mean_score:.2f}"],
            ["Varianza Score", f"{var_score:.2f}"],
            [f"Totale {param}", f"{total_occurrences}"],
            ["Coefficiente di Clustering", f"{clustering_coeff}"]
        ]

        # Tabella a destra del grafico
        table = ax.table(cellText=table_data, colLabels=["Parametro", "Valore"],
                        cellLoc="center", loc="center right",
                        bbox=[1.05, 0.2, 0.4, 0.5])

        # Aumenta la dimensione della tabella per evitare tagli
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.4)

        # Salva il grafico
        plt.savefig("%s/%s.png" % (dir, community), bbox_inches="tight")
        plt.close()

if __name__ == "__main__":
    df = pd.read_csv("csv/analisi_canali_per_domini.csv")
    crea_istogrammi(df, "Occorrenze")

    print("Creati gli istogrammi per le occorrenze")

    df_engagement = pd.read_csv("csv/analisi_canali_per_engagement.csv")
    crea_istogrammi(df_engagement, "Views")

    print("Creati gli istogrammi per le views")

    crea_istogrammi(df_engagement, "Forwards")

    print("Creati gli istogrammi per i forwards")