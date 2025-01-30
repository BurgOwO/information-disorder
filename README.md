# 📊 **Telegram e la disinformazione: studio delle connessioni informative**  
**_Esiste una relazione tra la chiusura delle community Telegram e la disinformazione? Il caso studio tramite Open Measures e Newsguard_**  

### 🌍 Information Disorder e Global Security  
Un progetto sviluppato per il corso di Information Disorder e Global Security nel CdL Data Science e gestione dell'innovazione.

---

## 🚀 **Descrizione del Progetto**  
Questo studio analizza le community online su Telegram per esplorare:  
1. **Il livello di apertura delle community**  
2. **La correlazione tra apertura e affidabilità delle fonti di notizie condivise**  

Attraverso la raccolta di dati, l'utilizzo di valutazioni NewsGuard e la visualizzazione delle relazioni tramite grafi in Gephi, il progetto fornisce una panoramica innovativa delle dinamiche informative nel mondo digitale.  

---

## 📚 **Indice**  
- [⚙️ Obiettivo principale](#-obiettivi)  
- [🛠️ Metodi e strumenti di lavoro](#️-strumenti-utilizzati)  
- [📂 Struttura del Progetto](#-struttura-del-progetto)

---

## ⚙️ **Obiettivo principale**  
- Analizzare l'apertura delle community Telegram.  
- Correlare l'apertura con l'affidabilità delle fonti tramite le valutazioni NewsGuard.  
- Visualizzare le dinamiche informative con grafi chiari e interattivi.  

---

## 🛠️ **Metodi e strumenti di lavoro**  
### 1. **Python** 🐍  
- Elaborazione dei dati ottenuti 
- Creazione del file .csv con nodi e archi
- Incrocio delle fonti con NewsGuard
- Analisi delle community secondo diverse metriche
- Calcolo correlazione tra score NewsGuard e chiusura della community

### 2. **Open Measures** 🔎
- Raccolta di messaggi e metadati da Telegram

### 3. **NewsGuard** 📊 
- Valutazione dell'affidabilità dei siti di notizie

### 4. **Gephi** 📈  
- Creazione e analisi dei grafi 

---

## 📂 **Struttura del Progetto**  
```plaintext
📁 LaTrasparenzaCommunityOnline/
├── 📂 data/            # Dataset raccolti
├── 📂 csv/             # CSV risultante dall'elaborazione dei dati
├── 📂 scripts/         # Script Python per raccolta e analisi dati
├── 📂 graphs/          # Grafi generati in Gephi
├── 📂 istogrammi/      # Istogrammi di tutte le community analizzate
├── 📄 README.md        # Documentazione
└── 📂 docs/            # Documentazione estesa e contesto storico