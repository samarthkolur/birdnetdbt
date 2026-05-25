import os
import ast
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

def embedding_to_vector(s):
    if s is None:
        return []
    try:
        if isinstance(s, dict):
            return s.get('dims', [])
        j = ast.literal_eval(s) if isinstance(s, str) else s
        return j.get('dims', [])
    except Exception:
        return []

class AE(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(dim, 64), nn.ReLU(), nn.Linear(64,32), nn.ReLU(), nn.Linear(32,16))
        self.dec = nn.Sequential(nn.Linear(16,32), nn.ReLU(), nn.Linear(32,64), nn.ReLU(), nn.Linear(64,dim))
    def forward(self, x):
        z = self.enc(x)
        return self.dec(z)

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
    X = np.array(padded, dtype=np.float32)
    ds = TensorDataset(torch.from_numpy(X))
    dl = DataLoader(ds, batch_size=4, shuffle=True)
    model = AE(X.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()
    for epoch in range(100):
        total = 0.0
        for (batch,) in dl:
            opt.zero_grad()
            recon = model(batch)
            loss = loss_fn(recon, batch)
            loss.backward()
            opt.step()
            total += loss.item()
    print('trained autoencoder; final loss', total)
    if bad_count > 0:
        print(f"Warning: {bad_count} records had embedding length != {EMB_DIM} and were padded/truncated")

if __name__ == '__main__':
    main()
