import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "sankalp.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Cache for search results (query -> [model_ids])
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_cache (
            query TEXT PRIMARY KEY,
            results_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Store for model metadata (to avoid re-fetching details)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_metadata (
            id TEXT PRIMARY KEY,
            data_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_cached_search(query: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT results_json FROM search_cache WHERE query = ?", (query.lower(),))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def save_search_cache(query: str, results: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO search_cache (query, results_json) VALUES (?, ?)", 
                  (query.lower(), json.dumps(results)))
    conn.commit()
    conn.close()

def get_model_metadata(model_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM model_metadata WHERE id = ?", (model_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def save_model_metadata(model_id: str, data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO model_metadata (id, data_json) VALUES (?, ?)", 
                  (model_id, json.dumps(data)))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
