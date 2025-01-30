import networkx as nx
import pandas as pd

def analyze_graph_clustering(graphml_path):
    # Carica il grafo dal file GraphML
    try:
        G = nx.read_graphml(graphml_path)
    except Exception as e:
        print(f"Errore durante la lettura del file GraphML: {e}")
        return None, None
    
    # Calcola il coefficiente di clustering per ogni nodo
    node_clustering = nx.clustering(G)
    
    # Calcola il coefficiente di clustering medio del grafo
    avg_clustering = nx.average_clustering(G)
    
    # Crea un DataFrame per una migliore visualizzazione dei risultati
    clustering_df = pd.DataFrame.from_dict(node_clustering, 
                                           orient='index', 
                                           columns=['clustering_coefficient'])
    clustering_df.index.name = 'Canali'  # Rinomina la colonna index in "Canali"
    clustering_df = clustering_df.sort_values('clustering_coefficient', 
                                              ascending=False)
    
    # Stampa i risultati
    print("\nAnalisi del Clustering:")
    print(f"Coefficiente di clustering medio del grafo: {avg_clustering:.4f}")

    # Salva i risultati in un file CSV
    save_clustering_results(clustering_df, avg_clustering)
    
    return node_clustering, avg_clustering

def save_clustering_results(clustering_df, avg_clustering):
    try:
        # Aggiunge una riga per il valore medio del clustering
        avg_row = pd.DataFrame({'clustering_coefficient': [avg_clustering]}, 
                               index=['average_clustering'])
        final_df = pd.concat([clustering_df, avg_row])
        
        # Salva il DataFrame in un file CSV con l'indice etichettato correttamente
        final_df.to_csv("csv/clustering_canali_filtrati.csv", index_label="node_id")
        print("\nRisultati salvati nel file.")
    except Exception as e:
        print(f"Errore durante il salvataggio dei risultati: {e}")

if __name__ == "__main__":
    file_path = "grafo_canali_filtrati.graphml"
    node_clustering, avg_clustering = analyze_graph_clustering(file_path)