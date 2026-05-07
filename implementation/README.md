# Implementation

---

## SK Popis

Táto časť repozitára obsahuje implementáciu navrhovaného agentického systému na generovanie zdrojového kódu z prirodzeného jazykového zadania.

Systém je založený na viacagentovej architektúre implementovanej pomocou frameworku LangGraph a využíva GraphRAG znalostnú bázu uloženú v grafovej databáze Neo4j.

---

## Požiadavky

- Python 3.10+
- Neo4j (lokálne alebo Docker)
- GitHub API token
- Mistral API key
- HuggingFace token

---

## Inštalácia

Závislosti:
```bash
pip install streamlit langchain langgraph neo4j sentence-transformers scikit-learn plantuml huggingface_hub requests
```
---

## Konfigurácia (.env)
V koreňovom adresári je potrebné vytvoriť .env súbor:
```bash
MISTRAL_API_KEY=your_key
GITHUB_TOKEN=your_token
HF_TOKEN=your_token
```

## Neo4j databáza
Systém využíva Neo4j databázu pre GraphRAG. 
Spustenie cez Docker (odporúčané):
```bash
docker run \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j
```

Nastavenie pripojenia:
V súbore:
```bash
graphRAG/client.py
```
je potrebné nastaviť:
```bash
neo = Neo4jClient(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)
```


## GitHub prehľadávanie:
V súbore:
```bash
github/ingestion.py
```
je potrebné nastaviť repozitáre, ktoré sa majú použiť na budovanie znalostnej bázy:
```bash
REPOSITORIES = [
    {
        "owner": "your_username",
        "name": "repo_name",
        "full_name": "your_username/repo_name",
        "type": "internal"
    }
]
```

## Spustenie systému
Používateľské rozhranie sa spúšťa pomocou Streamlit:
```bash
python -m streamlit run ui_app.py
```
