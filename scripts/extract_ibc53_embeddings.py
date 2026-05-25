#!/usr/bin/env python3
"""
Extract 1024-d embeddings from iBC53 WAV files using mel-spectrogram + PCA.
Produces data/ibc53_features.csv with columns matching seed loader.
This uses real audio from the iBC53 folder.
"""
import os
import json
import csv
import time
import sys
import argparse
import librosa
import numpy as np
from sklearn.decomposition import PCA

ROOT = os.path.join(os.path.dirname(__file__), '..')
IBC53 = os.path.join(ROOT, 'iBC53')
OUT_CSV = os.path.join(ROOT, 'data', 'ibc53_features.csv')

def collect_files(limit=None):
    files = []
    for species in sorted(os.listdir(IBC53)):
        spath = os.path.join(IBC53, species)
        if not os.path.isdir(spath):
            continue
        for fname in sorted(os.listdir(spath)):
            if not fname.lower().endswith('.wav'):
                continue
            files.append((species, os.path.join(spath, fname)))
            if limit and len(files) >= limit:
                return files
    return files


def human_progress(processed, total):
    pct = (processed / total) * 100 if total else 0
    return f'Processed {processed}/{total} ({pct:5.1f}%)'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=None, help='Limit number of files to process (for testing)')
    parser.add_argument('--update-seconds', type=float, default=1.0, help='How often (s) to update progress')
    args = parser.parse_args()

    files = collect_files(limit=args.limit)
    total = len(files)
    print(f'Found {total} WAV files')

    feats = []
    last_update = time.time()
    for i, (species, path) in enumerate(files, start=1):
        try:
            y, sr = librosa.load(path, sr=44100)
        except Exception as e:
            print(f"Warning: failed to load {path}: {e}")
            continue
        duration_ms = int(1000 * len(y) / sr)
        rms = librosa.feature.rms(y=y).mean()
        amplitude_db = 20 * np.log10(rms + 1e-9)
        # mel spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
        logS = librosa.power_to_db(S)
        # flatten summary stats
        vec = np.concatenate([np.mean(logS, axis=1), np.std(logS, axis=1)])
        # estimate pitch via YIN; bound fmax to a safe value
        fmax = min(8000, int(sr/2))
        try:
            pitch_est = float(librosa.yin(y, fmin=50, fmax=fmax).mean())
        except Exception:
            pitch_est = 0.0
        feats.append({
            'recording_id': f"{species}__{os.path.basename(path)}",
            'species': species,
            'confidence': float(min(max((rms*10), 0.0), 1.0)),
            'duration_ms': duration_ms,
            'amplitude_db': float(amplitude_db),
            'pitch_hz': pitch_est,
            'sample_rate': sr,
            'vec': vec.tolist()
        })

        # progress update every args.update_seconds
        now = time.time()
        if now - last_update >= args.update_seconds or i == total:
            msg = human_progress(i, total)
            sys.stdout.write('\r' + msg)
            sys.stdout.flush()
            last_update = now

    # finish line
    print('\n')

    if len(feats) == 0:
        print('No features collected, aborting write.')
        return

    # Build PCA to 1024 dims
    allvecs = np.stack([f['vec'] for f in feats])
    COMPONENTS = 1024
    if allvecs.shape[1] < COMPONENTS:
        # pad with zeros
        allvecs = np.hstack([allvecs, np.zeros((allvecs.shape[0], COMPONENTS - allvecs.shape[1]))])
    elif allvecs.shape[1] > COMPONENTS:
        pca = PCA(n_components=COMPONENTS)
        allvecs = pca.fit_transform(allvecs)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['recording_id','species','confidence','duration_ms','amplitude_db','pitch_hz','sample_rate','embeddings_json'])
        for i, rec in enumerate(feats):
            vec = allvecs[i].tolist()
            embeddings_json = json.dumps({'dims': vec})
            writer.writerow([rec['recording_id'], rec['species'], rec['confidence'], rec['duration_ms'], rec['amplitude_db'], rec['pitch_hz'], rec['sample_rate'], embeddings_json])

    print('Wrote', OUT_CSV)


if __name__ == '__main__':
    main()
