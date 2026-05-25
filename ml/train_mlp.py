import os
import ast
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def embedding_to_vector(s):
    if s is None:
        return []
    try:
        if isinstance(s, dict):
            return s.get('dims', [])
        # sometimes stored as JSON string
        j = ast.literal_eval(s) if isinstance(s, str) else s
        return j.get('dims', [])
    except Exception:
        return []

def load_data_from_db(url):
    import psycopg2
    import pandas.io.sql as psql
    conn = psycopg2.connect(url)
    df = psql.read_sql('select * from raw.bird_features', conn)
    conn.close()
    return df

def main():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        df = load_data_from_db(db_url)
    else:
        df = pd.read_csv('data/seed_bird_features.csv')
    EMB_DIM = int(os.environ.get('EMBEDDING_DIM', '1024'))
    X = df['embeddings_json'].apply(embedding_to_vector).tolist()
    padded = []
    bad_count = 0
    for v in X:
        if len(v) != EMB_DIM:
            bad_count += 1
        padded.append((v + [0]*EMB_DIM)[:EMB_DIM])
    X = np.array(padded, dtype=float)
    y = df['species']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    clf = MLPClassifier(hidden_layer_sizes=(256,128), max_iter=500)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print(classification_report(y_test, preds))
    if bad_count > 0:
        print(f"Warning: {bad_count} records had embedding length != {EMB_DIM} and were padded/truncated")

if __name__ == '__main__':
    main()
