import networkx as nx
import pandas as pd
 
# Caricare il grafo da un file .graphml
graph = nx.read_graphml("project.graphml")
print("Grafo caricato con successo. Numero di nodi:", graph.number_of_nodes(), "Numero di archi:", graph.number_of_edges())
 
# Filtrare i nodi di tipo 'channel'
channels = [node for node in graph.nodes if graph.nodes[node].get("type") == "Channel"]
print(f"Numero di nodi di tipo 'channel': {len(channels)}")
 
# Calcolare il grado (degree) senza ponderazione, come in Gephi
degree_dict = dict(graph.degree(channels))  # Degree semplice (senza pesi)
 
# Calcolare la betweenness centrality con l'approccio di Brandes ottimizzato
betweenness_dict = nx.betweenness_centrality(
    graph, 
    normalized=True, 
    endpoints=False  # Gephi di default non usa gli estremi
)
 
# Calcolare la closeness centrality. NetworkX normalizza già come fa Gephi.
closeness_dict = nx.closeness_centrality(graph)
 
# Calcolare la authority score usando l'algoritmo HITS
if nx.is_directed(graph):
    _, authority_dict = nx.hits(graph, normalized=True)
else:
    # Gephi non calcola authority per grafi non diretti
    authority_dict = {node: 0 for node in graph.nodes}
 
# Calcolare l'eigenvector centrality con iterazioni elevate e tolleranza bassa
eigenvector_dict = nx.eigenvector_centrality(
    graph, 
    max_iter=1000,  # Iterazioni alte per migliorare la convergenza
    tol=1e-6        # Tolleranza più bassa (simile a Gephi)
)
 
# Creare una lista di risultati per tutti i nodi di tipo 'channel'
results = []
for node in channels:
    results.append({
        "Node": node,
        "Degree": degree_dict.get(node, 0),
        "Betweenness": betweenness_dict.get(node, 0),
        "Closeness": closeness_dict.get(node, 0),
        "Authority": authority_dict.get(node, 0),
        "Eigenvector": eigenvector_dict.get(node, 0),
    })
 
# Convertire i risultati in un DataFrame Pandas
df = pd.DataFrame(results)
 
# Salvare i risultati in un file CSV
output_file = "channel_metrics_gephi.csv"
df.to_csv(output_file, index=False)
print(f"Analisi completata. I risultati sono stati salvati in '{output_file}'.")